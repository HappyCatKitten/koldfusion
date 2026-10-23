/*
 * ldapd.c - the Gibson Directory Server 1.0, an LDAPv3 directory bundled
 * with KoldFusion so CFLDAP has something to talk to out of the box (in 1999
 * that was a Netscape Directory Server on the next machine over).
 *
 *   - listens on 127.0.0.1:3890 by default (registry key DirectoryServer)
 *   - bind (simple; anonymous read allowed), search (all scopes, all RFC 2254
 *     filters, attribute selection, size limit), add, modify, delete,
 *     modifyDN, compare, unbind, abandon, and the "Who am I?" extended op
 *   - the directory lives in memory and is written to an LDIF file
 *     (kfroot/ldap/gibson.ldif) after every change; it is seeded from
 *     kfroot/seed/directory.ldif
 *   - userPassword values are stored {SHA}-hashed, the Netscape default
 *   - access control, Netscape style: anyone may read (but never another
 *     user's userPassword), "cn=Directory Manager" and the members of
 *     cn=Directory Administrators may write, users may modify their own entry
 *
 * One thread per connection; the entries are guarded by a rwlock.
 */
#define _GNU_SOURCE
#include "engine.h"
#include "func.h"
#include "ldap.h"
#include <stdlib.h>
#include <strings.h>
#include <ctype.h>
#include <errno.h>
#include <netdb.h>
#include <unistd.h>
#include <signal.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define DS_KEY "DirectoryServer"
#define DS_VENDOR_VERSION "Gibson Directory Server 1.0"
#define MAX_MESSAGE (1 << 20)
#define MAX_CONNS 128

/* ================================================================ data */
typedef struct LVal { char *v; size_t n; } LVal;
typedef struct LAttr { char *name; LVal *vals; int nvals, cap; } LAttr;
typedef struct LEntry { char *dn, *ndn; LAttr *attrs; int nattrs, cap; } LEntry;

typedef struct Conf {
    int enabled, port, sizelimit, anon, log, sha;
    char *bind, *base, *nbase, *admindn, *nadmindn, *adminpw, *ldif, *seed;
} Conf;

static pthread_rwlock_t dit_lock = PTHREAD_RWLOCK_INITIALIZER;
static LEntry **E; static int NE, CAPE;
static int dit_loaded;
static struct { dev_t dev; ino_t ino; long sec, nsec; off_t size; int valid; } disk;

static pthread_mutex_t conf_mu = PTHREAD_MUTEX_INITIALIZER;
static Conf *CF;
static int lazy_mode, override_port, disabled_flag;
static int listen_fd = -1;
static pthread_t accept_thr;
static volatile int running;
static int nconns;
static long nops, connseq;
static double started_at;

extern Struct *g_server_scope;
extern Arena *g_server_arena;

static void *xmalloc(size_t n) { void *p = calloc(1, n ? n : 1); if (!p) abort(); return p; }
static void *xrealloc(void *p, size_t n) { void *q = realloc(p, n ? n : 1); if (!q) abort(); return q; }
static char *xstrdup(const char *s) { size_t n = strlen(s); char *d = xmalloc(n + 1); memcpy(d, s, n); return d; }
static char *xstrndup(const char *s, size_t n) { char *d = xmalloc(n + 1); memcpy(d, s, n); return d; }

/* ================================================================ configuration */
static void ds_default(const char *entry, const char *value) {
    if (!reg_exists(cfg_key(DS_KEY), entry)) cfg_set(DS_KEY, entry, value);
}

/* default user directory + security context so CFAUTHENTICATE works against us out of the box */
static void seed_security(const char *base) {
    if (cfg_int(DS_KEY, "SecuritySeeded", 0)) return;
    cfg_set(DS_KEY, "SecuritySeeded", "1");
    char *dk = cfg_key("Security\\UserDirectories\\Gibson Directory");
    if (!reg_exists(dk, NULL)) {
        reg_set(dk, "Namespace", "LDAP", 0);
        reg_set(dk, "Location", kprintf("127.0.0.1:%d", cfg_int(DS_KEY, "Port", 3890)), 0);
        reg_set(dk, "Description", "Gibson Directory Server (built in)", 0);
        reg_set(dk, "Root", base, 0);
        reg_set(dk, "Username", "", 0);
        reg_set(dk, "Password", kf_scramble(""), 0);
        reg_set(dk, "LookupStart", "uid=", 0);
        reg_set(dk, "LookupEnd", kprintf(",ou=People,%s", base), 0);
        reg_set(dk, "UserAttribute", "uid", 0);
    }
    char *ck = cfg_key("Security\\Contexts\\GibsonIntranet");
    if (!reg_exists(ck, NULL)) {
        reg_set(ck, "Description", "Gibson Mainframe Co. intranet (users from the Gibson Directory)", 0);
        reg_set(ck, "UserDirectories", "Gibson Directory", 0);
        char *rk = cfg_key("Security\\Contexts\\GibsonIntranet\\Rules\\EditPhoneBook");
        reg_set(rk, "ResourceType", "Application", 0);
        reg_set(rk, "Resource", "PhoneDirectory", 0);
        reg_set(rk, "Actions", "Edit", 0);
        char *pk = cfg_key("Security\\Contexts\\GibsonIntranet\\Policies\\PhoneBookEditors");
        reg_set(pk, "Rules", "EditPhoneBook", 0);
        reg_set(pk, "Users", "", 0);
        reg_set(pk, "Groups", "Directory Administrators", 0);
    }
}

static void install_ds_defaults(void) {
    /* Basic Security: CFLDAP can be switched off like CFFILE or CFREGISTRY */
    if (!reg_exists(cfg_key("Server\\TagRestrictions"), "CFLDAP")) cfg_set("Server\\TagRestrictions", "CFLDAP", "1");
    ds_default("Enabled", "1");
    ds_default("Port", "3890");
    ds_default("BindAddress", "127.0.0.1");
    ds_default("BaseDN", "o=Gibson Mainframe Co, c=US");
    ds_default("AdminDN", "cn=Directory Manager");
    if (!reg_exists(cfg_key(DS_KEY), "AdminPassword")) cfg_set(DS_KEY, "AdminPassword", kf_scramble("admin"));
    ds_default("SizeLimit", "500");
    ds_default("AllowAnonymous", "1");
    ds_default("PasswordStorage", "SHA");
    ds_default("LogAccess", "1");
    ds_default("LDIFFile", kf_path_join(G.root, "ldap/gibson.ldif"));
    seed_security(cfg(DS_KEY, "BaseDN", ""));
}

static Conf *conf_load(void) {
    Conf *c = xmalloc(sizeof *c);
    c->enabled = cfg_int(DS_KEY, "Enabled", 1) && !disabled_flag;
    c->port = override_port ? override_port : cfg_int(DS_KEY, "Port", 3890);
    c->sizelimit = cfg_int(DS_KEY, "SizeLimit", 500);
    c->anon = cfg_int(DS_KEY, "AllowAnonymous", 1);
    c->log = cfg_int(DS_KEY, "LogAccess", 1);
    c->sha = kf_stricmp(cfg(DS_KEY, "PasswordStorage", "SHA"), "CLEAR") != 0;
    c->bind = xstrdup(cfg(DS_KEY, "BindAddress", "127.0.0.1"));
    c->base = xstrdup(cfg(DS_KEY, "BaseDN", "o=Gibson Mainframe Co, c=US"));
    c->nbase = dn_normalize(c->base);
    if (!c->nbase) c->nbase = xstrdup("");
    c->admindn = xstrdup(cfg(DS_KEY, "AdminDN", "cn=Directory Manager"));
    c->nadmindn = dn_normalize(c->admindn);
    if (!c->nadmindn) c->nadmindn = xstrdup("cn=directory manager");
    c->adminpw = xstrdup(kf_unscramble(cfg(DS_KEY, "AdminPassword", "")));
    c->ldif = xstrdup(kf_native_path(cfg(DS_KEY, "LDIFFile", kf_path_join(G.root, "ldap/gibson.ldif"))));
    c->seed = xstrdup(kf_path_join(G.root, "seed/directory.ldif"));
    return c;
}

/* configurations are never freed (a restart leaks a few hundred bytes), so a
 * connection may keep using the one it read */
static Conf *conf(void) {
    pthread_mutex_lock(&conf_mu);
    Conf *c = CF;
    pthread_mutex_unlock(&conf_mu);
    return c;
}
static void conf_reload(void) {
    Conf *c = conf_load();
    pthread_mutex_lock(&conf_mu);
    CF = c;
    pthread_mutex_unlock(&conf_mu);
}

/* ================================================================ entries */
static LEntry *entry_new(const char *dn, const char *ndn) {
    LEntry *e = xmalloc(sizeof *e);
    e->dn = xstrdup(dn);
    e->ndn = xstrdup(ndn);
    return e;
}
static void entry_free(LEntry *e) {
    if (!e) return;
    for (int i = 0; i < e->nattrs; i++) {
        for (int j = 0; j < e->attrs[i].nvals; j++) free(e->attrs[i].vals[j].v);
        free(e->attrs[i].vals);
        free(e->attrs[i].name);
    }
    free(e->attrs); free(e->dn); free(e->ndn); free(e);
}
static LEntry *entry_copy(const LEntry *s) {
    LEntry *e = entry_new(s->dn, s->ndn);
    e->cap = e->nattrs = s->nattrs;
    e->attrs = xmalloc(sizeof(LAttr) * (e->cap ? e->cap : 1));
    for (int i = 0; i < s->nattrs; i++) {
        LAttr *a = &e->attrs[i];
        a->name = xstrdup(s->attrs[i].name);
        a->nvals = a->cap = s->attrs[i].nvals;
        a->vals = xmalloc(sizeof(LVal) * (a->cap ? a->cap : 1));
        for (int j = 0; j < a->nvals; j++) {
            a->vals[j].v = xstrndup(s->attrs[i].vals[j].v, s->attrs[i].vals[j].n);
            a->vals[j].n = s->attrs[i].vals[j].n;
        }
    }
    return e;
}
static LAttr *attr_find(const LEntry *e, const char *name) {
    for (int i = 0; i < e->nattrs; i++) if (ldap_attr_eq(e->attrs[i].name, name)) return &e->attrs[i];
    return NULL;
}
static LAttr *attr_get(LEntry *e, const char *name) {
    LAttr *a = attr_find(e, name);
    if (a) return a;
    if (e->nattrs == e->cap) { e->cap = e->cap ? e->cap * 2 : 8; e->attrs = xrealloc(e->attrs, sizeof(LAttr) * e->cap); }
    a = &e->attrs[e->nattrs++];
    memset(a, 0, sizeof *a);
    a->name = xstrdup(name);
    return a;
}
static void attr_remove(LEntry *e, const char *name) {
    for (int i = 0; i < e->nattrs; i++) {
        if (!ldap_attr_eq(e->attrs[i].name, name)) continue;
        for (int j = 0; j < e->attrs[i].nvals; j++) free(e->attrs[i].vals[j].v);
        free(e->attrs[i].vals); free(e->attrs[i].name);
        memmove(&e->attrs[i], &e->attrs[i + 1], sizeof(LAttr) * (e->nattrs - i - 1));
        e->nattrs--;
        return;
    }
}
static int val_index(LAttr *a, const char *v, size_t n) {
    for (int j = 0; j < a->nvals; j++) if (ldap_value_eq(a->name, a->vals[j].v, a->vals[j].n, v, n)) return j;
    return -1;
}
static void val_add(LAttr *a, const char *v, size_t n) {
    if (a->nvals == a->cap) { a->cap = a->cap ? a->cap * 2 : 4; a->vals = xrealloc(a->vals, sizeof(LVal) * a->cap); }
    a->vals[a->nvals].v = xstrndup(v, n);
    a->vals[a->nvals].n = n;
    a->nvals++;
}
static void val_del(LAttr *a, int j) {
    free(a->vals[j].v);
    memmove(&a->vals[j], &a->vals[j + 1], sizeof(LVal) * (a->nvals - j - 1));
    a->nvals--;
}

static int find_index(const char *ndn) {
    for (int i = 0; i < NE; i++) if (!strcmp(E[i]->ndn, ndn)) return i;
    return -1;
}
static LEntry *find_entry(const char *ndn) { int i = find_index(ndn); return i < 0 ? NULL : E[i]; }
static void dit_append(LEntry *e) {
    if (NE == CAPE) { CAPE = CAPE ? CAPE * 2 : 64; E = xrealloc(E, sizeof(LEntry *) * CAPE); }
    E[NE++] = e;
}
static void dit_clear(void) {
    for (int i = 0; i < NE; i++) entry_free(E[i]);
    NE = 0;
}
static int has_children(const char *ndn) {
    for (int i = 0; i < NE; i++) if (ndn_depth_below(E[i]->ndn, ndn) == 1) return 1;
    return 0;
}
static int count_children(const char *ndn) {
    int n = 0;
    for (int i = 0; i < NE; i++) if (ndn_depth_below(E[i]->ndn, ndn) == 1) n++;
    return n;
}
/* deepest existing ancestor of ndn (raw DN), for matchedDN */
static const char *matched_dn(const char *dn) {
    char *p = dn_parent(dn);
    while (*p) {
        char *np = dn_normalize(p);
        LEntry *e = np ? find_entry(np) : NULL;
        free(np);
        if (e) { char *r = kstrdup(e->dn); free(p); return r; }
        char *q = dn_parent(p);
        free(p);
        p = q;
    }
    free(p);
    return "";
}

static int is_operational(const char *name) {
    static const char *OPS[] = {"createTimestamp", "modifyTimestamp", "creatorsName", "modifiersName", "entryDN",
                                "hasSubordinates", "numSubordinates", "subschemaSubentry", NULL};
    for (int i = 0; OPS[i]; i++) if (!strcasecmp(OPS[i], name)) return 1;
    return 0;
}

static char *gentime(void) {
    time_t t = time(NULL);
    struct tm tm; gmtime_r(&t, &tm);
    return kprintf("%04d%02d%02d%02d%02d%02dZ", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec);
}
static void set_single(LEntry *e, const char *name, const char *v) {
    LAttr *a = attr_get(e, name);
    while (a->nvals) val_del(a, 0);
    val_add(a, v, strlen(v));
}

/* ================================================================ passwords */
static char *hash_password(const char *pw, size_t n) {
    if (n && pw[0] == '{') return xstrndup(pw, n);        /* already {SCHEME}... */
    if (!conf()->sha) return xstrndup(pw, n);
    unsigned char h[20];
    ldap_sha1((const unsigned char *)pw, n, h);
    char *b = ldap_b64(h, 20);
    char *r = xmalloc(strlen(b) + 6);
    sprintf(r, "{SHA}%s", b);
    free(b);
    return r;
}
static int password_matches(const char *stored, size_t sn, const char *pw, size_t pn) {
    if (sn > 5 && !strncasecmp(stored, "{SHA}", 5)) {
        size_t dl; unsigned char *d = ldap_unb64(stored + 5, &dl);
        unsigned char h[20];
        ldap_sha1((const unsigned char *)pw, pn, h);
        int ok = d && dl == 20 && !memcmp(d, h, 20);
        free(d);
        return ok;
    }
    if (sn > 6 && !strncasecmp(stored, "{SSHA}", 6)) {
        size_t dl; unsigned char *d = ldap_unb64(stored + 6, &dl);
        int ok = 0;
        if (d && dl > 20) {
            unsigned char *buf = xmalloc(pn + dl - 20);
            memcpy(buf, pw, pn); memcpy(buf + pn, d + 20, dl - 20);
            unsigned char h[20];
            ldap_sha1(buf, pn + dl - 20, h);
            ok = !memcmp(d, h, 20);
            free(buf);
        }
        free(d);
        return ok;
    }
    if (sn > 7 && !strncasecmp(stored, "{CLEAR}", 7)) return sn - 7 == pn && !memcmp(stored + 7, pw, pn);
    if (sn && stored[0] == '{') return 0;                 /* {CRYPT} etc.: not supported */
    return sn == pn && !memcmp(stored, pw, pn);
}

/* ================================================================ LDIF */
static int ldif_safe(const char *v, size_t n) {
    if (!n) return 1;
    if (v[0] == ' ' || v[0] == ':' || v[0] == '<' || v[n - 1] == ' ') return 0;
    for (size_t i = 0; i < n; i++) {
        unsigned char c = (unsigned char)v[i];
        if (c < 0x20 || c > 0x7e) return 0;
    }
    return 1;
}
static void ldif_line(FILE *f, const char *name, const char *v, size_t n) {
    if (ldif_safe(v, n)) {
        /* fold at 76 columns, Netscape style */
        size_t col = fprintf(f, "%s: ", name);
        for (size_t i = 0; i < n; i++) {
            if (col >= 76) { fputs("\n ", f); col = 1; }
            fputc(v[i], f);
            col++;
        }
        fputc('\n', f);
    } else {
        char *b = ldap_b64((const unsigned char *)v, n);
        size_t col = fprintf(f, "%s:: ", name);
        for (char *p = b; *p; p++) {
            if (col >= 76) { fputs("\n ", f); col = 1; }
            fputc(*p, f);
            col++;
        }
        fputc('\n', f);
        free(b);
    }
}
static int dn_depth(const char *ndn) { return ndn_depth_below(ndn, ""); }
static int cmp_depth(const void *a, const void *b) {
    const LEntry *x = *(LEntry *const *)a, *y = *(LEntry *const *)b;
    return dn_depth(x->ndn) - dn_depth(y->ndn);
}

static void disk_note(const char *path) {
    struct stat st;
    if (stat(path, &st)) { disk.valid = 0; return; }
    disk.dev = st.st_dev; disk.ino = st.st_ino; disk.size = st.st_size;
    disk.sec = st.st_mtim.tv_sec; disk.nsec = st.st_mtim.tv_nsec; disk.valid = 1;
}
static int disk_changed(const char *path) {
    struct stat st;
    if (stat(path, &st)) return 0;
    return !disk.valid || st.st_dev != disk.dev || st.st_ino != disk.ino || st.st_size != disk.size ||
           st.st_mtim.tv_sec != disk.sec || st.st_mtim.tv_nsec != disk.nsec;
}

/* write lock held */
static int dit_save(void) {
    Conf *c = conf();
    char *dir = kstrdup(c->ldif);
    char *sl = strrchr(dir, '/');
    if (sl) { *sl = 0; kf_mkdirs(dir); }
    char *tmp = kprintf("%s.%d.tmp", c->ldif, (int)getpid());
    FILE *f = fopen(tmp, "w");
    if (!f) return 0;
    LEntry **sorted = xmalloc(sizeof(LEntry *) * (NE ? NE : 1));
    memcpy(sorted, E, sizeof(LEntry *) * NE);
    /* parents before children (stable: insertion sort keeps the original order within a depth) */
    for (int i = 1; i < NE; i++) {
        LEntry *x = sorted[i]; int j = i - 1;
        while (j >= 0 && cmp_depth(&sorted[j], &x) > 0) { sorted[j + 1] = sorted[j]; j--; }
        sorted[j + 1] = x;
    }
    time_t t = time(NULL);
    fprintf(f, "# %s - directory contents (LDIF)\n# Written %s#\nversion: 1\n\n", DS_VENDOR_VERSION, ctime(&t));
    for (int i = 0; i < NE; i++) {
        LEntry *e = sorted[i];
        ldif_line(f, "dn", e->dn, strlen(e->dn));
        for (int a = 0; a < e->nattrs; a++)
            for (int v = 0; v < e->attrs[a].nvals; v++) ldif_line(f, e->attrs[a].name, e->attrs[a].vals[v].v, e->attrs[a].vals[v].n);
        fputc('\n', f);
    }
    free(sorted);
    int ok = !ferror(f);
    if (fclose(f)) ok = 0;
    if (!ok || rename(tmp, c->ldif)) { unlink(tmp); return 0; }
    disk_note(c->ldif);
    return 1;
}

/* parse LDIF text into the DIT (write lock held). suffix_from/to rewrite DNs
 * when seeding a directory whose base DN differs from the seed's. */
static int ldif_parse(char *text, const char *suffix_from, const char *suffix_to) {
    int count = 0;
    LEntry *cur = NULL;
    /* unfold continuation lines in place */
    char *w = text;
    for (char *r = text; *r; ) {
        if (*r == '\r') { r++; continue; }
        if (*r == '\n' && r[1] == ' ') { r += 2; continue; }
        *w++ = *r++;
    }
    *w = 0;
#define FLUSH() do { if (cur) { if (find_index(cur->ndn) >= 0) entry_free(cur); else { dit_append(cur); count++; } cur = NULL; } } while (0)
    char *p = text;
    for (;;) {
        char *nl = strchr(p, '\n');
        size_t ll = nl ? (size_t)(nl - p) : strlen(p);
        if (!ll) FLUSH();
        else if (p[0] != '#') {
            char *line = kstrndup(p, ll);
            char *colon = strchr(line, ':');
            if (colon) {
                *colon = 0;
                char *name = kf_trim(line);
                char *val = colon + 1;
                size_t vn = 0;
                char *bin = NULL;
                int skip = 0;
                if (*val == ':') {
                    bin = (char *)ldap_unb64(kf_trim(val + 1), &vn);
                    if (!bin) skip = 1; else val = bin;
                } else if (*val == '<') skip = 1;              /* URLs: not supported */
                else { while (*val == ' ') val++; vn = strlen(val); }
                if (skip || (!strcasecmp(name, "version") && !cur)) ;
                else if (!strcasecmp(name, "dn")) {
                    FLUSH();
                    char *dn = kstrndup(val, vn);
                    if (suffix_from && suffix_to) {
                        size_t ld = strlen(dn), lf = strlen(suffix_from);
                        if (!strcasecmp(dn, suffix_from)) dn = kstrdup(suffix_to);
                        else if (ld > lf && !strcasecmp(dn + ld - lf, suffix_from) && dn[ld - lf - 1] == ',')
                            dn = kprintf("%.*s%s", (int)(ld - lf), dn, suffix_to);
                    }
                    char *ndn = dn_normalize(dn);
                    cur = ndn ? entry_new(dn, ndn) : NULL;
                    free(ndn);
                } else if (cur && strcasecmp(name, "changetype")) {
                    LAttr *a = attr_get(cur, name);
                    if (val_index(a, val, vn) < 0) val_add(a, val, vn);
                }
                free(bin);
            }
        }
        if (!nl) break;
        p = nl + 1;
    }
    FLUSH();
#undef FLUSH
    return count;
}

/* write lock held */
static void dit_load(void) {
    Conf *c = conf();
    dit_clear();
    size_t len;
    char *text = kf_read_file(c->ldif, &len);
    if (text) {
        ldif_parse(text, NULL, NULL);
        free(text);
        disk_note(c->ldif);
    } else {
        char *seed = kf_read_file(c->seed, &len);
        const char *from = "o=Gibson Mainframe Co,c=US";
        char *nfrom = dn_normalize(from);
        int same = nfrom && !strcmp(nfrom, c->nbase);
        free(nfrom);
        if (seed) { ldif_parse(seed, same ? NULL : from, same ? NULL : c->base); free(seed); }
    }
    /* make sure the naming context exists */
    if (*c->nbase && find_index(c->nbase) < 0) {
        LEntry *e = entry_new(c->base, c->nbase);
        char **T, **V;
        char *rdn = dn_first_rdn(c->base);
        int n = rdn_split(rdn, &T, &V);
        free(rdn);
        val_add(attr_get(e, "objectClass"), "top", 3);
        for (int i = 0; i < n; i++) {
            const char *t = ldap_attr_canon(T[i]);
            const char *oc = !strcasecmp(t, "o") ? "organization" : !strcasecmp(t, "ou") ? "organizationalUnit" :
                             !strcasecmp(t, "dc") ? "dcObject" : !strcasecmp(t, "c") ? "country" : "extensibleObject";
            val_add(attr_get(e, "objectClass"), oc, strlen(oc));
            if (!strcasecmp(t, "dc")) val_add(attr_get(e, "objectClass"), "organization", 12), val_add(attr_get(e, "o"), V[i], strlen(V[i]));
            val_add(attr_get(e, T[i]), V[i], strlen(V[i]));
        }
        if (n > 0) { ldap_strv_free(T, n); ldap_strv_free(V, n); }
        dit_append(e);
    }
    if (!text) dit_save();
    dit_loaded = 1;
}

/* pick up changes another KoldFusion process (e.g. kfserver --run) wrote */
static void dit_sync(void) {
    Conf *c = conf();
    if (dit_loaded && !disk_changed(c->ldif)) return;
    pthread_rwlock_wrlock(&dit_lock);
    if (!dit_loaded || disk_changed(c->ldif)) dit_load();
    pthread_rwlock_unlock(&dit_lock);
}

/* ================================================================ filters */
static int soundex(const char *w, size_t n, char out[5]) {
    static const char *codes = "01230120022455012623010202";
    size_t i = 0; int k = 0;
    while (i < n && !isalpha((unsigned char)w[i])) i++;
    if (i >= n) return 0;
    /* unlike classic Soundex the first letter is coded too, so Carol ~= Karol */
    char last = codes[toupper((unsigned char)w[i]) - 'A'];
    out[k++] = last != '0' ? last : (char)toupper((unsigned char)w[i]);
    for (i++; i < n && k < 4; i++) {
        if (!isalpha((unsigned char)w[i])) continue;
        char cd = codes[toupper((unsigned char)w[i]) - 'A'];
        if (cd != '0' && cd != last) out[k++] = cd;
        last = cd;
    }
    while (k < 4) out[k++] = '0';
    out[4] = 0;
    return 1;
}
static char *soundex_words(const char *s, size_t n) {
    LBuf b; lb_init(&b);
    size_t i = 0;
    while (i < n) {
        while (i < n && !isalnum((unsigned char)s[i])) i++;
        size_t w0 = i;
        while (i < n && isalnum((unsigned char)s[i])) i++;
        char sx[5];
        if (i > w0 && soundex(s + w0, i - w0, sx)) { lb_put(&b, sx, 4); lb_put(&b, " ", 1); }
    }
    lb_put(&b, "", 1);
    return (char *)b.p;
}

static int is_intstr(const char *s, size_t n) {
    size_t i = 0;
    if (i < n && (s[i] == '-' || s[i] == '+')) i++;
    if (i == n) return 0;
    for (; i < n; i++) if (!isdigit((unsigned char)s[i])) return 0;
    return 1;
}

static int order_cmp(const char *attr, const char *a, size_t an, const char *b, size_t bn) {
    if (is_intstr(a, an) && is_intstr(b, bn) && an < 19 && bn < 19) {
        long x = strtol(kstrndup(a, an), NULL, 10), y = strtol(kstrndup(b, bn), NULL, 10);
        return x < y ? -1 : x > y;
    }
    size_t xl, yl;
    char *x = ldap_value_norm(attr, a, an, &xl), *y = ldap_value_norm(attr, b, bn, &yl);
    int r = strcmp(x, y);
    free(x); free(y);
    return r;
}

/* RDN attribute values count as attribute values for dnAttributes matching */
static int dn_has_ava(const char *dn, const char *attr, const char *v, size_t vn) {
    char *p = xstrdup(dn);
    int found = 0;
    while (*p && !found) {
        char *rdn = dn_first_rdn(p);
        char **T, **V;
        int n = rdn_split(rdn, &T, &V);
        for (int i = 0; i < n && !found; i++)
            if ((!attr || ldap_attr_eq(T[i], attr)) && ldap_value_eq(T[i], V[i], strlen(V[i]), v, vn)) found = 1;
        if (n > 0) { ldap_strv_free(T, n); ldap_strv_free(V, n); }
        free(rdn);
        char *q = dn_parent(p); free(p); p = q;
    }
    free(p);
    return found;
}

static int vmatch_any(const LEntry *e, const char *attr, BerSlice val, int caseexact) {
    LAttr *a = attr_find(e, attr);
    if (!a) return 0;
    for (int j = 0; j < a->nvals; j++) {
        if (caseexact) { if (a->vals[j].n == val.n && !memcmp(a->vals[j].v, val.p, val.n)) return 1; }
        else if (ldap_value_eq(a->name, a->vals[j].v, a->vals[j].n, (const char *)val.p, val.n)) return 1;
    }
    return 0;
}

/* 1 true, 0 false, -1 undefined; filter already validated */
static int filter_eval(const LEntry *e, BerSlice f, int depth) {
    unsigned tag; BerSlice c;
    if (depth > 64 || !ber_next(&f, &tag, &c)) return -1;
    switch (tag) {
    case LDAP_FILTER_AND: {
        int r = 1;
        while (c.n) {
            BerSlice one = c; unsigned t; BerSlice x;
            ber_next(&c, &t, &x);
            one.n = (size_t)(c.p - one.p);
            int v = filter_eval(e, one, depth + 1);
            if (v == 0) return 0;
            if (v < 0) r = -1;
        }
        return r;
    }
    case LDAP_FILTER_OR: {
        int r = 0;
        while (c.n) {
            BerSlice one = c; unsigned t; BerSlice x;
            ber_next(&c, &t, &x);
            one.n = (size_t)(c.p - one.p);
            int v = filter_eval(e, one, depth + 1);
            if (v == 1) return 1;
            if (v < 0) r = -1;
        }
        return r;
    }
    case LDAP_FILTER_NOT: {
        int v = filter_eval(e, c, depth + 1);
        return v < 0 ? -1 : !v;
    }
    case LDAP_FILTER_PRESENT: {
        char *attr = kstrndup((const char *)c.p, c.n);
        if (!strcasecmp(attr, "objectClass")) return 1;
        if (!strcasecmp(attr, "entryDN") || !strcasecmp(attr, "hasSubordinates") || !strcasecmp(attr, "numSubordinates")) return 1;
        return attr_find(e, attr) != NULL;
    }
    case LDAP_FILTER_EQUALITY: case LDAP_FILTER_GE: case LDAP_FILTER_LE: case LDAP_FILTER_APPROX: {
        unsigned t; BerSlice ad, av;
        ber_next(&c, &t, &ad); ber_next(&c, &t, &av);
        char *attr = kstrndup((const char *)ad.p, ad.n);
        if (!strcasecmp(attr, "entryDN") && tag == LDAP_FILTER_EQUALITY) {
            char *nv = dn_normalize(kstrndup((const char *)av.p, av.n));
            int r = nv && !strcmp(nv, e->ndn);
            free(nv);
            return r;
        }
        LAttr *a = attr_find(e, attr);
        if (!a) return 0;
        if (tag == LDAP_FILTER_EQUALITY) {
            if (!strcasecmp(attr, "userPassword")) {
                for (int j = 0; j < a->nvals; j++) if (password_matches(a->vals[j].v, a->vals[j].n, (const char *)av.p, av.n)) return 1;
                return 0;
            }
            return vmatch_any(e, attr, av, 0);
        }
        if (tag == LDAP_FILTER_APPROX) {
            char *want = soundex_words((const char *)av.p, av.n);
            int hit = 0;
            for (int j = 0; j < a->nvals && !hit; j++) {
                if (ldap_value_eq(a->name, a->vals[j].v, a->vals[j].n, (const char *)av.p, av.n)) { hit = 1; break; }
                char *have = soundex_words(a->vals[j].v, a->vals[j].n);
                if (*want && (!strcmp(have, want) || strstr(have, want))) hit = 1;
                free(have);
            }
            free(want);
            return hit;
        }
        for (int j = 0; j < a->nvals; j++) {
            int r = order_cmp(a->name, a->vals[j].v, a->vals[j].n, (const char *)av.p, av.n);
            if (tag == LDAP_FILTER_GE ? r >= 0 : r <= 0) return 1;
        }
        return 0;
    }
    case LDAP_FILTER_SUBSTR: {
        unsigned t; BerSlice ad, seq, part;
        ber_next(&c, &t, &ad); ber_next(&c, &t, &seq);
        char *attr = kstrndup((const char *)ad.p, ad.n);
        LAttr *a = attr_find(e, attr);
        if (!a) return 0;
        for (int j = 0; j < a->nvals; j++) {
            size_t vl;
            char *v = ldap_value_norm(a->name, a->vals[j].v, a->vals[j].n, &vl);
            const char *pos = v;
            int ok = 1;
            BerSlice s = seq;
            while (ok && ber_next(&s, &t, &part)) {
                size_t pl;
                char *pn = ldap_value_norm(a->name, (const char *)part.p, part.n, &pl);
                if (t == 0x80) { if (strncmp(pos, pn, pl)) ok = 0; else pos += pl; }
                else if (t == 0x81) { const char *h = strstr(pos, pn); if (!h) ok = 0; else pos = h + pl; }
                else { size_t rest = strlen(pos); if (rest < pl || strcmp(pos + rest - pl, pn)) ok = 0; }
                free(pn);
            }
            free(v);
            if (ok) return 1;
        }
        return 0;
    }
    case LDAP_FILTER_EXT: {
        unsigned t; BerSlice x, val = {NULL, 0};
        char *rule = NULL, *type = NULL; int dnattrs = 0;
        while (c.n && ber_next(&c, &t, &x)) {
            if (t == 0x81) rule = kstrndup((const char *)x.p, x.n);
            else if (t == 0x82) type = kstrndup((const char *)x.p, x.n);
            else if (t == 0x83) val = x;
            else if (t == 0x84) dnattrs = x.n && x.p[0];
        }
        int exact = rule && (!strcmp(rule, "2.5.13.5") || !strcasecmp(rule, "caseExactMatch"));
        if (rule && !exact && strcmp(rule, "2.5.13.2") && strcasecmp(rule, "caseIgnoreMatch") &&
            strcmp(rule, "2.5.13.0") && strcasecmp(rule, "objectIdentifierMatch")) return -1;   /* unknown rule */
        if (type) { if (vmatch_any(e, type, val, exact)) return 1; }
        else for (int i = 0; i < e->nattrs; i++) if (vmatch_any(e, e->attrs[i].name, val, exact)) return 1;
        if (dnattrs && dn_has_ava(e->dn, type, (const char *)val.p, val.n)) return 1;
        return 0;
    }
    }
    return -1;
}

static void filter_to_str(Buf *b, BerSlice f, int depth) {
    unsigned tag; BerSlice c;
    if (depth > 64 || !ber_next(&f, &tag, &c)) { buf_puts(b, "(?)"); return; }
    switch (tag) {
    case LDAP_FILTER_AND: case LDAP_FILTER_OR:
        buf_puts(b, tag == LDAP_FILTER_AND ? "(&" : "(|");
        while (c.n) {
            BerSlice one = c; unsigned t; BerSlice x;
            if (!ber_next(&c, &t, &x)) break;
            one.n = (size_t)(c.p - one.p);
            filter_to_str(b, one, depth + 1);
        }
        buf_putc(b, ')');
        return;
    case LDAP_FILTER_NOT: buf_puts(b, "(!"); filter_to_str(b, c, depth + 1); buf_putc(b, ')'); return;
    case LDAP_FILTER_PRESENT: buf_printf(b, "(%.*s=*)", (int)c.n, c.p); return;
    case LDAP_FILTER_SUBSTR: {
        unsigned t; BerSlice ad, seq, part;
        ber_next(&c, &t, &ad); ber_next(&c, &t, &seq);
        buf_printf(b, "(%.*s=", (int)ad.n, ad.p);
        int first = 1;
        while (ber_next(&seq, &t, &part)) {
            if (t != 0x80 && first) buf_putc(b, '*');
            buf_put(b, (const char *)part.p, part.n);
            if (t != 0x82) buf_putc(b, '*');
            first = 0;
        }
        buf_putc(b, ')');
        return;
    }
    case LDAP_FILTER_EXT: buf_puts(b, "(extensible)"); return;
    default: {
        unsigned t; BerSlice ad, av;
        if (!ber_next(&c, &t, &ad) || !ber_next(&c, &t, &av)) { buf_puts(b, "(?)"); return; }
        const char *op = tag == LDAP_FILTER_EQUALITY ? "=" : tag == LDAP_FILTER_GE ? ">=" : tag == LDAP_FILTER_LE ? "<=" : "~=";
        buf_printf(b, "(%.*s%s%.*s)", (int)ad.n, ad.p, op, (int)av.n, av.p);
    }
    }
}

/* ================================================================ connections */
typedef struct Conn {
    int fd, id;
    char *binddn, *nbinddn;      /* malloc'd; "" = anonymous */
    int is_root;
    char peer[64];
} Conn;

static void dslog(Conn *cn, const char *fmt, ...) __attribute__((format(printf, 2, 3)));
static void dslog(Conn *cn, const char *fmt, ...) {
    if (!conf()->log) return;
    char msg[2048];
    va_list ap; va_start(ap, fmt);
    vsnprintf(msg, sizeof msg, fmt, ap);
    va_end(ap);
    for (unsigned char *p = (unsigned char *)msg; *p; p++) if (*p < 0x20 || *p == 0x7f) *p = '?';
    kf_log("directory.log", "Information", "conn=%d %s", cn ? cn->id : 0, msg);
}

static void send_msg(Conn *cn, LBuf *b) { ldap_send_all(cn->fd, b->p, b->len); }

static void put_result(LBuf *b, long msgid, unsigned restag, int code, const char *matched, const char *diag) {
    size_t m = ber_begin(b, BER_SEQUENCE);
    ber_put_int(b, BER_INTEGER, msgid);
    size_t r = ber_begin(b, restag);
    ber_put_int(b, BER_ENUMERATED, code);
    ber_put_cstr(b, BER_OCTETSTRING, matched ? matched : "");
    ber_put_cstr(b, BER_OCTETSTRING, diag ? diag : "");
    ber_end(b, r);
    ber_end(b, m);
}
static void send_result(Conn *cn, long msgid, unsigned restag, int code, const char *matched, const char *diag) {
    LBuf b; lb_init(&b);
    put_result(&b, msgid, restag, code, matched, diag);
    send_msg(cn, &b);
    lb_free(&b);
}

/* may this connection write to the entry ndn? (read lock held) */
static int may_write(Conn *cn, const char *ndn, int self_ok) {
    if (cn->is_root) return 1;
    if (!*cn->nbinddn) return 0;
    if (self_ok && !strcmp(cn->nbinddn, ndn)) return 1;
    Conf *c = conf();
    char *gdn = dn_normalize(kprintf("cn=Directory Administrators,ou=Groups,%s", c->base));
    LEntry *g = gdn ? find_entry(gdn) : NULL;
    free(gdn);
    if (!g) return 0;
    const char *mattrs[] = {"uniqueMember", "member", NULL};
    for (int k = 0; mattrs[k]; k++) {
        LAttr *a = attr_find(g, mattrs[k]);
        for (int j = 0; a && j < a->nvals; j++) {
            char *nm = dn_normalize(kstrndup(a->vals[j].v, a->vals[j].n));
            int hit = nm && !strcmp(nm, cn->nbinddn);
            free(nm);
            if (hit) return 1;
        }
    }
    return 0;
}

/* ---------------------------------------------------------------- bind */
static void do_bind(Conn *cn, long msgid, BerSlice op) {
    unsigned t; BerSlice ver, name, auth;
    long version;
    if (!ber_next(&op, &t, &ver) || t != BER_INTEGER || !ber_get_int(ver, &version) ||
        !ber_next(&op, &t, &name) || t != BER_OCTETSTRING || !ber_next(&op, &t, &auth)) {
        send_result(cn, msgid, LDAP_RES_BIND, LDAP_PROTOCOL_ERROR, NULL, "decoding error");
        return;
    }
    /* any bind resets the connection to anonymous first */
    free(cn->binddn); free(cn->nbinddn);
    cn->binddn = xstrdup(""); cn->nbinddn = xstrdup(""); cn->is_root = 0;
    if (version != 2 && version != 3) {
        send_result(cn, msgid, LDAP_RES_BIND, LDAP_PROTOCOL_ERROR, NULL, "requested protocol version not supported");
        return;
    }
    if (t != 0x80) {
        dslog(cn, "BIND method=sasl err=7");
        send_result(cn, msgid, LDAP_RES_BIND, LDAP_AUTH_METHOD_NOT_SUPPORTED, NULL, "SASL authentication is not supported");
        return;
    }
    char *dn = kstrndup((const char *)name.p, name.n);
    if (!name.n && !auth.n) {
        dslog(cn, "BIND dn=\"\" method=simple (anonymous) err=0");
        send_result(cn, msgid, LDAP_RES_BIND, LDAP_SUCCESS, NULL, NULL);
        return;
    }
    if (!auth.n) {
        dslog(cn, "BIND dn=\"%s\" err=53 (no password)", dn);
        send_result(cn, msgid, LDAP_RES_BIND, LDAP_UNWILLING_TO_PERFORM, NULL, "unauthenticated bind (DN with no password) disallowed");
        return;
    }
    char *ndn = dn_normalize(dn);
    if (!ndn) {
        send_result(cn, msgid, LDAP_RES_BIND, LDAP_INVALID_DN_SYNTAX, NULL, "invalid DN");
        return;
    }
    Conf *c = conf();
    int ok = 0, root = 0;
    if (!strcmp(ndn, c->nadmindn)) {
        root = ok = strlen(c->adminpw) == auth.n && !memcmp(c->adminpw, auth.p, auth.n);
    } else {
        dit_sync();
        pthread_rwlock_rdlock(&dit_lock);
        LEntry *e = find_entry(ndn);
        LAttr *a = e ? attr_find(e, "userPassword") : NULL;
        for (int j = 0; a && j < a->nvals && !ok; j++)
            ok = password_matches(a->vals[j].v, a->vals[j].n, (const char *)auth.p, auth.n);
        pthread_rwlock_unlock(&dit_lock);
    }
    if (ok) {
        free(cn->binddn); free(cn->nbinddn);
        cn->binddn = xstrdup(dn); cn->nbinddn = ndn; cn->is_root = root;
        dslog(cn, "BIND dn=\"%s\" method=simple err=0", dn);
        send_result(cn, msgid, LDAP_RES_BIND, LDAP_SUCCESS, NULL, NULL);
    } else {
        free(ndn);
        dslog(cn, "BIND dn=\"%s\" method=simple err=49", dn);
        send_result(cn, msgid, LDAP_RES_BIND, LDAP_INVALID_CREDENTIALS, NULL, NULL);
    }
}

/* ---------------------------------------------------------------- search */
typedef struct AttrSel { int all_user, all_oper, none; int n; char **names; } AttrSel;

static int sel_wants(AttrSel *s, const char *name, int oper) {
    if (s->none) return 0;
    for (int i = 0; i < s->n; i++) if (ldap_attr_eq(s->names[i], name)) return 1;
    return oper ? s->all_oper : s->all_user;
}

static void put_attr(LBuf *b, const char *name, const char *v, size_t n, int typesonly) {
    size_t a = ber_begin(b, BER_SEQUENCE);
    ber_put_cstr(b, BER_OCTETSTRING, name);
    size_t s = ber_begin(b, BER_SET);
    if (!typesonly) ber_put_str(b, BER_OCTETSTRING, v, n);
    ber_end(b, s);
    ber_end(b, a);
}

static void put_entry(Conn *cn, LBuf *b, long msgid, const LEntry *e, AttrSel *sel, int typesonly) {
    size_t m = ber_begin(b, BER_SEQUENCE);
    ber_put_int(b, BER_INTEGER, msgid);
    size_t r = ber_begin(b, LDAP_RES_SEARCH_ENTRY);
    ber_put_cstr(b, BER_OCTETSTRING, e->dn);
    size_t l = ber_begin(b, BER_SEQUENCE);
    int self = *cn->nbinddn && !strcmp(cn->nbinddn, e->ndn);
    for (int i = 0; i < e->nattrs; i++) {
        const LAttr *a = &e->attrs[i];
        int oper = is_operational(a->name);
        if (!sel_wants(sel, a->name, oper)) continue;
        if (!strcasecmp(a->name, "userPassword") && !cn->is_root && !self) continue;
        size_t s = ber_begin(b, BER_SEQUENCE);
        ber_put_cstr(b, BER_OCTETSTRING, a->name);
        size_t set = ber_begin(b, BER_SET);
        if (!typesonly) for (int j = 0; j < a->nvals; j++) ber_put_str(b, BER_OCTETSTRING, a->vals[j].v, a->vals[j].n);
        ber_end(b, set);
        ber_end(b, s);
    }
    if (sel_wants(sel, "entryDN", 1)) put_attr(b, "entryDN", e->dn, strlen(e->dn), typesonly);
    if (sel_wants(sel, "numSubordinates", 1) || sel_wants(sel, "hasSubordinates", 1)) {
        int nc = count_children(e->ndn);
        if (sel_wants(sel, "hasSubordinates", 1)) put_attr(b, "hasSubordinates", nc ? "TRUE" : "FALSE", nc ? 4 : 5, typesonly);
        if (sel_wants(sel, "numSubordinates", 1)) { char *s = kprintf("%d", nc); put_attr(b, "numSubordinates", s, strlen(s), typesonly); }
    }
    ber_end(b, l);
    ber_end(b, r);
    ber_end(b, m);
}

static LEntry *root_dse(void) {
    Conf *c = conf();
    LEntry *e = entry_new("", "");
    val_add(attr_get(e, "objectClass"), "top", 3);
    val_add(attr_get(e, "objectClass"), "extensibleObject", 16);
    val_add(attr_get(e, "namingContexts"), c->base, strlen(c->base));
    val_add(attr_get(e, "supportedLDAPVersion"), "2", 1);
    val_add(attr_get(e, "supportedLDAPVersion"), "3", 1);
    val_add(attr_get(e, "supportedExtension"), "1.3.6.1.4.1.4203.1.11.3", 23);
    val_add(attr_get(e, "vendorName"), "Gibson Mainframe Co.", 20);
    val_add(attr_get(e, "vendorVersion"), DS_VENDOR_VERSION, strlen(DS_VENDOR_VERSION));
    val_add(attr_get(e, "dataversion"), "019991231000000", 15);
    return e;
}

static void do_search(Conn *cn, long msgid, BerSlice op) {
    unsigned t; BerSlice base, scope, deref, size, time_, typesonly, filter, attrs;
    long lscope, lsize;
    if (!ber_next(&op, &t, &base) || t != BER_OCTETSTRING ||
        !ber_next(&op, &t, &scope) || t != BER_ENUMERATED || !ber_get_int(scope, &lscope) ||
        !ber_next(&op, &t, &deref) || t != BER_ENUMERATED ||
        !ber_next(&op, &t, &size) || t != BER_INTEGER || !ber_get_int(size, &lsize) ||
        !ber_next(&op, &t, &time_) || t != BER_INTEGER ||
        !ber_next(&op, &t, &typesonly) || t != BER_BOOLEAN) {
        send_result(cn, msgid, LDAP_RES_SEARCH_DONE, LDAP_PROTOCOL_ERROR, NULL, "decoding error");
        return;
    }
    BerSlice fstart = op;
    if (!ber_next(&op, &t, &filter)) { send_result(cn, msgid, LDAP_RES_SEARCH_DONE, LDAP_PROTOCOL_ERROR, NULL, "decoding error"); return; }
    fstart.n = (size_t)(op.p - fstart.p);
    if (!ldap_filter_valid(fstart, 0)) {
        send_result(cn, msgid, LDAP_RES_SEARCH_DONE, LDAP_PROTOCOL_ERROR, NULL, "bad search filter");
        return;
    }
    if (!ber_next(&op, &t, &attrs) || t != BER_SEQUENCE || lscope < 0 || lscope > 2) {
        send_result(cn, msgid, LDAP_RES_SEARCH_DONE, LDAP_PROTOCOL_ERROR, NULL, "decoding error");
        return;
    }
    int tonly = typesonly.n && typesonly.p[0];
    AttrSel sel = {0, 0, 0, 0, NULL};
    sel.names = kmalloc(sizeof(char *) * (attrs.n / 2 + 1));
    while (attrs.n) {
        BerSlice a;
        if (!ber_next(&attrs, &t, &a) || t != BER_OCTETSTRING) { send_result(cn, msgid, LDAP_RES_SEARCH_DONE, LDAP_PROTOCOL_ERROR, NULL, "decoding error"); return; }
        char *nm = kstrndup((const char *)a.p, a.n);
        if (!strcmp(nm, "*")) sel.all_user = 1;
        else if (!strcmp(nm, "+")) sel.all_oper = 1;
        else if (!strcmp(nm, "1.1")) sel.none = 1;
        else sel.names[sel.n++] = nm;
    }
    if (!sel.n && !sel.all_oper && !sel.none) sel.all_user = 1;
    if (sel.none && (sel.n || sel.all_user || sel.all_oper)) sel.none = 0;

    char *dn = kstrndup((const char *)base.p, base.n);
    Buf fs; buf_init(&fs); filter_to_str(&fs, fstart, 0);
    Conf *c = conf();
    if (!*cn->nbinddn && !c->anon) {
        dslog(cn, "SRCH base=\"%s\" err=50 (anonymous access disabled)", dn);
        send_result(cn, msgid, LDAP_RES_SEARCH_DONE, LDAP_INSUFFICIENT_ACCESS, NULL, "anonymous access is not allowed");
        return;
    }
    if (!base.n && lscope == 0) {
        LEntry *dse = root_dse();
        LBuf b; lb_init(&b);
        if (filter_eval(dse, fstart, 0) == 1) put_entry(cn, &b, msgid, dse, &sel, tonly);
        put_result(&b, msgid, LDAP_RES_SEARCH_DONE, LDAP_SUCCESS, NULL, NULL);
        send_msg(cn, &b);
        lb_free(&b);
        entry_free(dse);
        dslog(cn, "SRCH base=\"\" scope=0 filter=\"%s\" (root DSE)", buf_cstr(&fs));
        return;
    }
    char *nbase = dn_normalize(dn);
    if (!nbase) {
        send_result(cn, msgid, LDAP_RES_SEARCH_DONE, LDAP_INVALID_DN_SYNTAX, NULL, "invalid DN");
        return;
    }
    long limit = c->sizelimit > 0 && !cn->is_root ? c->sizelimit : 0;
    if (lsize > 0 && (!limit || lsize < limit)) limit = lsize;
    dit_sync();
    LBuf b; lb_init(&b);
    int n = 0, code = LDAP_SUCCESS;
    const char *matched = NULL;
    pthread_rwlock_rdlock(&dit_lock);
    if (*nbase && find_index(nbase) < 0) {
        code = LDAP_NO_SUCH_OBJECT;
        matched = matched_dn(dn);
    } else {
        for (int i = 0; i < NE; i++) {
            int d = ndn_depth_below(E[i]->ndn, nbase);
            if (d < 0 || (lscope == 0 && d != 0) || (lscope == 1 && d != 1)) continue;
            if (filter_eval(E[i], fstart, 0) != 1) continue;
            if (limit && n >= limit) { code = LDAP_SIZELIMIT_EXCEEDED; break; }
            put_entry(cn, &b, msgid, E[i], &sel, tonly);
            n++;
        }
    }
    pthread_rwlock_unlock(&dit_lock);
    put_result(&b, msgid, LDAP_RES_SEARCH_DONE, code, matched, code == LDAP_NO_SUCH_OBJECT ? "" : NULL);
    send_msg(cn, &b);
    lb_free(&b);
    dslog(cn, "SRCH base=\"%s\" scope=%ld filter=\"%s\" nentries=%d err=%d", dn, lscope, buf_cstr(&fs), n, code);
    free(nbase);
}

/* ---------------------------------------------------------------- writes */
static const char *write_denied_msg(Conn *cn) {
    return *cn->nbinddn ? "insufficient access rights" : "anonymous users may not modify the directory";
}

/* RDN values must be present in the entry; returns 0 if the RDN is unparsable */
static int ensure_rdn_values(LEntry *e) {
    char *rdn = dn_first_rdn(e->dn);
    char **T, **V;
    int n = rdn_split(rdn, &T, &V);
    free(rdn);
    if (n <= 0) return 0;
    for (int i = 0; i < n; i++) {
        LAttr *a = attr_get(e, T[i]);
        if (val_index(a, V[i], strlen(V[i])) < 0) val_add(a, V[i], strlen(V[i]));
    }
    ldap_strv_free(T, n); ldap_strv_free(V, n);
    return 1;
}
static int rdn_values_present(LEntry *e) {
    char *rdn = dn_first_rdn(e->dn);
    char **T, **V;
    int n = rdn_split(rdn, &T, &V);
    free(rdn);
    int ok = 1;
    for (int i = 0; i < n; i++) {
        LAttr *a = attr_find(e, T[i]);
        if (!a || val_index(a, V[i], strlen(V[i])) < 0) ok = 0;
    }
    if (n > 0) { ldap_strv_free(T, n); ldap_strv_free(V, n); }
    return ok;
}

/* read SET OF values into attr a (hashing passwords); returns result code */
static int add_values(LAttr *a, BerSlice set, int dup_is_error) {
    unsigned t; BerSlice v;
    while (set.n) {
        if (!ber_next(&set, &t, &v) || t != BER_OCTETSTRING) return LDAP_PROTOCOL_ERROR;
        char *val = (char *)v.p; size_t vn = v.n;
        char *h = NULL;
        if (!strcasecmp(ldap_attr_canon(a->name), "userPassword")) { h = hash_password(val, vn); val = h; vn = strlen(h); }
        if (val_index(a, val, vn) >= 0) { free(h); if (dup_is_error) return LDAP_TYPE_OR_VALUE_EXISTS; continue; }
        val_add(a, val, vn);
        free(h);
    }
    return LDAP_SUCCESS;
}

static void stamp(LEntry *e, Conn *cn, int create) {
    char *now = gentime();
    if (create) { set_single(e, "createTimestamp", now); set_single(e, "creatorsName", cn->binddn); }
    set_single(e, "modifyTimestamp", now);
    set_single(e, "modifiersName", cn->binddn);
}

static void do_add(Conn *cn, long msgid, BerSlice op) {
    unsigned t; BerSlice name, attrs;
    if (!ber_next(&op, &t, &name) || t != BER_OCTETSTRING || !ber_next(&op, &t, &attrs) || t != BER_SEQUENCE) {
        send_result(cn, msgid, LDAP_RES_ADD, LDAP_PROTOCOL_ERROR, NULL, "decoding error");
        return;
    }
    char *dn = kstrndup((const char *)name.p, name.n);
    char *ndn = dn_normalize(dn);
    if (!ndn || !*ndn) { free(ndn); send_result(cn, msgid, LDAP_RES_ADD, LDAP_INVALID_DN_SYNTAX, NULL, "invalid DN"); return; }
    LEntry *e = entry_new(dn, ndn);
    int code = LDAP_SUCCESS; const char *diag = NULL;
    while (attrs.n && code == LDAP_SUCCESS) {
        BerSlice one, type, set;
        if (!ber_next(&attrs, &t, &one) || t != BER_SEQUENCE || !ber_next(&one, &t, &type) || t != BER_OCTETSTRING ||
            !type.n || !ber_next(&one, &t, &set) || t != BER_SET) { code = LDAP_PROTOCOL_ERROR; diag = "decoding error"; break; }
        char *an = kstrndup((const char *)type.p, type.n);
        if (is_operational(an)) continue;                      /* NO-USER-MODIFICATION: silently dropped */
        if (!set.n) { code = LDAP_PROTOCOL_ERROR; diag = kprintf("no values for attribute type %s", an); break; }
        LAttr *a = attr_get(e, an);
        code = add_values(a, set, 1);
        if (code == LDAP_TYPE_OR_VALUE_EXISTS) diag = kprintf("duplicate value in attribute %s", an);
    }
    if (code == LDAP_SUCCESS && !attr_find(e, "objectClass")) { code = LDAP_OBJECT_CLASS_VIOLATION; diag = "no objectClass attribute"; }
    if (code == LDAP_SUCCESS && !ensure_rdn_values(e)) { code = LDAP_INVALID_DN_SYNTAX; diag = "invalid RDN"; }
    if (code != LDAP_SUCCESS) {
        entry_free(e); free(ndn);
        dslog(cn, "ADD dn=\"%s\" err=%d", dn, code);
        send_result(cn, msgid, LDAP_RES_ADD, code, NULL, diag);
        return;
    }
    stamp(e, cn, 1);
    dit_sync();
    pthread_rwlock_wrlock(&dit_lock);
    Conf *c = conf();
    const char *matched = NULL;
    char *pdn = dn_parent(dn);
    char *npdn = dn_normalize(pdn);
    free(pdn);
    if (find_index(ndn) >= 0) { code = LDAP_ALREADY_EXISTS; diag = NULL; }
    else if (strcmp(ndn, c->nbase) && (!npdn || find_index(npdn) < 0)) { code = LDAP_NO_SUCH_OBJECT; matched = matched_dn(dn); diag = "parent does not exist"; }
    else if (!may_write(cn, npdn ? npdn : "", 0)) { code = LDAP_INSUFFICIENT_ACCESS; diag = write_denied_msg(cn); }
    else {
        dit_append(e);
        if (!dit_save()) { NE--; code = LDAP_OTHER; diag = "unable to write the directory database"; }
        else e = NULL;
    }
    pthread_rwlock_unlock(&dit_lock);
    free(npdn);
    if (e) entry_free(e);
    free(ndn);
    dslog(cn, "ADD dn=\"%s\" err=%d", dn, code);
    send_result(cn, msgid, LDAP_RES_ADD, code, matched, diag);
}

static void do_delete(Conn *cn, long msgid, BerSlice dnslice) {
    char *dn = kstrndup((const char *)dnslice.p, dnslice.n);
    char *ndn = dn_normalize(dn);
    if (!ndn || !*ndn) { free(ndn); send_result(cn, msgid, LDAP_RES_DELETE, LDAP_INVALID_DN_SYNTAX, NULL, "invalid DN"); return; }
    int code = LDAP_SUCCESS; const char *diag = NULL, *matched = NULL;
    dit_sync();
    pthread_rwlock_wrlock(&dit_lock);
    int i = find_index(ndn);
    if (i < 0) { code = LDAP_NO_SUCH_OBJECT; matched = matched_dn(dn); }
    else if (!may_write(cn, ndn, 0)) { code = LDAP_INSUFFICIENT_ACCESS; diag = write_denied_msg(cn); }
    else if (has_children(ndn)) { code = LDAP_NOT_ALLOWED_ON_NONLEAF; diag = "subordinate objects must be deleted first"; }
    else {
        LEntry *e = E[i];
        memmove(&E[i], &E[i + 1], sizeof(LEntry *) * (NE - i - 1));
        NE--;
        if (!dit_save()) {
            memmove(&E[i + 1], &E[i], sizeof(LEntry *) * (NE - i));
            E[i] = e; NE++;
            code = LDAP_OTHER; diag = "unable to write the directory database";
        } else entry_free(e);
    }
    pthread_rwlock_unlock(&dit_lock);
    free(ndn);
    dslog(cn, "DEL dn=\"%s\" err=%d", dn, code);
    send_result(cn, msgid, LDAP_RES_DELETE, code, matched, diag);
}

static void do_modify(Conn *cn, long msgid, BerSlice op) {
    unsigned t; BerSlice name, changes;
    if (!ber_next(&op, &t, &name) || t != BER_OCTETSTRING || !ber_next(&op, &t, &changes) || t != BER_SEQUENCE) {
        send_result(cn, msgid, LDAP_RES_MODIFY, LDAP_PROTOCOL_ERROR, NULL, "decoding error");
        return;
    }
    char *dn = kstrndup((const char *)name.p, name.n);
    char *ndn = dn_normalize(dn);
    if (!ndn) { send_result(cn, msgid, LDAP_RES_MODIFY, LDAP_INVALID_DN_SYNTAX, NULL, "invalid DN"); return; }
    int code = LDAP_SUCCESS; const char *diag = NULL, *matched = NULL;
    dit_sync();
    pthread_rwlock_wrlock(&dit_lock);
    int idx = find_index(ndn);
    LEntry *e = NULL;
    if (idx < 0) { code = LDAP_NO_SUCH_OBJECT; matched = matched_dn(dn); }
    else if (!may_write(cn, ndn, 1)) { code = LDAP_INSUFFICIENT_ACCESS; diag = write_denied_msg(cn); }
    else e = entry_copy(E[idx]);
    while (e && changes.n && code == LDAP_SUCCESS) {
        BerSlice ch, opv, mod, type, set;
        long mop;
        if (!ber_next(&changes, &t, &ch) || t != BER_SEQUENCE || !ber_next(&ch, &t, &opv) || t != BER_ENUMERATED ||
            !ber_get_int(opv, &mop) || !ber_next(&ch, &t, &mod) || t != BER_SEQUENCE ||
            !ber_next(&mod, &t, &type) || t != BER_OCTETSTRING || !type.n || !ber_next(&mod, &t, &set) || t != BER_SET) {
            code = LDAP_PROTOCOL_ERROR; diag = "decoding error"; break;
        }
        char *an = kstrndup((const char *)type.p, type.n);
        if (is_operational(an)) { code = LDAP_CONSTRAINT_VIOLATION; diag = kprintf("%s: no user modification allowed", an); break; }
        if (mop == 0) {                                     /* add */
            if (!set.n) { code = LDAP_PROTOCOL_ERROR; diag = kprintf("modify/add: %s: no values given", an); break; }
            code = add_values(attr_get(e, an), set, 1);
            if (code) diag = kprintf("modify/add: %s: value #0 already exists", an);
        } else if (mop == 1) {                              /* delete */
            LAttr *a = attr_find(e, an);
            if (!a) { code = LDAP_NO_SUCH_ATTRIBUTE; diag = kprintf("modify/delete: %s: no such attribute", an); break; }
            if (!set.n) { attr_remove(e, an); continue; }
            BerSlice v;
            while (set.n) {
                if (!ber_next(&set, &t, &v)) { code = LDAP_PROTOCOL_ERROR; break; }
                int j = -1;
                if (!strcasecmp(ldap_attr_canon(a->name), "userPassword")) {
                    for (int k = 0; k < a->nvals && j < 0; k++)
                        if (password_matches(a->vals[k].v, a->vals[k].n, (const char *)v.p, v.n) ||
                            (a->vals[k].n == v.n && !memcmp(a->vals[k].v, v.p, v.n))) j = k;
                } else j = val_index(a, (const char *)v.p, v.n);
                if (j < 0) { code = LDAP_NO_SUCH_ATTRIBUTE; diag = kprintf("modify/delete: %s: no such value", an); break; }
                val_del(a, j);
            }
            if (code == LDAP_SUCCESS && !a->nvals) attr_remove(e, an);
        } else if (mop == 2) {                              /* replace */
            attr_remove(e, an);
            if (set.n) {
                code = add_values(attr_get(e, an), set, 1);
                if (code) diag = kprintf("modify/replace: %s: duplicate value", an);
            }
        } else { code = LDAP_PROTOCOL_ERROR; diag = "unknown modify operation"; }
    }
    if (e && code == LDAP_SUCCESS && !attr_find(e, "objectClass")) { code = LDAP_OBJECT_CLASS_VIOLATION; diag = "objectClass may not be removed"; }
    if (e && code == LDAP_SUCCESS && !rdn_values_present(e)) { code = LDAP_NOT_ALLOWED_ON_RDN; diag = "the RDN value may not be removed"; }
    if (e && code == LDAP_SUCCESS) {
        stamp(e, cn, 0);
        LEntry *old = E[idx];
        E[idx] = e;
        if (!dit_save()) { E[idx] = old; code = LDAP_OTHER; diag = "unable to write the directory database"; }
        else { entry_free(old); e = NULL; }
    }
    pthread_rwlock_unlock(&dit_lock);
    if (e) entry_free(e);
    free(ndn);
    dslog(cn, "MOD dn=\"%s\" err=%d", dn, code);
    send_result(cn, msgid, LDAP_RES_MODIFY, code, matched, diag);
}

/* rebuild the raw DN of a descendant after its ancestor olddn was renamed to newdn */
static char *rebase_dn(const char *dn, int levels, const char *newdn) {
    Buf b; buf_init(&b);
    char *p = xstrdup(dn);
    for (int i = 0; i < levels; i++) {
        char *r = dn_first_rdn(p);
        buf_puts(&b, r); buf_putc(&b, ',');
        free(r);
        char *q = dn_parent(p); free(p); p = q;
    }
    free(p);
    buf_puts(&b, newdn);
    return buf_cstr(&b);
}

static void do_moddn(Conn *cn, long msgid, BerSlice op) {
    unsigned t; BerSlice name, newrdn, delold, sup = {NULL, 0};
    int has_sup = 0;
    if (!ber_next(&op, &t, &name) || t != BER_OCTETSTRING || !ber_next(&op, &t, &newrdn) || t != BER_OCTETSTRING ||
        !ber_next(&op, &t, &delold) || t != BER_BOOLEAN) {
        send_result(cn, msgid, LDAP_RES_MODDN, LDAP_PROTOCOL_ERROR, NULL, "decoding error");
        return;
    }
    if (op.n) { if (!ber_next(&op, &t, &sup) || t != 0x80) { send_result(cn, msgid, LDAP_RES_MODDN, LDAP_PROTOCOL_ERROR, NULL, "decoding error"); return; } has_sup = 1; }
    char *dn = kstrndup((const char *)name.p, name.n);
    char *rdn = kf_trim(kstrndup((const char *)newrdn.p, newrdn.n));
    int deleteold = delold.n && delold.p[0];
    char *ndn = dn_normalize(dn);
    char **T, **V;
    int nr = rdn_split(rdn, &T, &V);
    if (!ndn || !*ndn || nr <= 0 || strchr(rdn, ',') != NULL) {
        free(ndn); if (nr > 0) { ldap_strv_free(T, nr); ldap_strv_free(V, nr); }
        send_result(cn, msgid, LDAP_RES_MODDN, LDAP_INVALID_DN_SYNTAX, NULL, "invalid DN or RDN");
        return;
    }
    char *parent = has_sup ? kstrndup((const char *)sup.p, sup.n) : NULL;
    if (!parent) { char *p = dn_parent(dn); parent = kstrdup(p); free(p); }
    char *newdn = *parent ? kprintf("%s,%s", rdn, parent) : rdn;
    char *nnew = dn_normalize(newdn);
    char *nparent = dn_normalize(parent);
    int code = LDAP_SUCCESS; const char *diag = NULL, *matched = NULL;
    dit_sync();
    pthread_rwlock_wrlock(&dit_lock);
    int idx = find_index(ndn);
    if (idx < 0) { code = LDAP_NO_SUCH_OBJECT; matched = matched_dn(dn); }
    else if (!nnew || !nparent) { code = LDAP_INVALID_DN_SYNTAX; diag = "invalid new superior"; }
    else if (!may_write(cn, ndn, 0)) { code = LDAP_INSUFFICIENT_ACCESS; diag = write_denied_msg(cn); }
    else if (strcmp(nnew, ndn) && find_index(nnew) >= 0) code = LDAP_ALREADY_EXISTS;
    else if (*nparent && find_index(nparent) < 0) { code = LDAP_NO_SUCH_OBJECT; matched = matched_dn(newdn); diag = "new superior does not exist"; }
    else if (ndn_depth_below(nparent, ndn) >= 0) { code = LDAP_UNWILLING_TO_PERFORM; diag = "cannot move an entry below itself"; }
    else {
        LEntry *e = entry_copy(E[idx]);
        /* old RDN values */
        char *ordn = dn_first_rdn(e->dn);
        char **OT, **OV;
        int no = rdn_split(ordn, &OT, &OV);
        free(ordn);
        free(e->dn); free(e->ndn);
        e->dn = xstrdup(newdn); e->ndn = xstrdup(nnew);
        for (int i = 0; i < nr; i++) {
            LAttr *a = attr_get(e, T[i]);
            if (val_index(a, V[i], strlen(V[i])) < 0) val_add(a, V[i], strlen(V[i]));
        }
        if (deleteold) {
            for (int i = 0; i < no; i++) {
                int innew = 0;
                for (int k = 0; k < nr; k++) if (ldap_attr_eq(OT[i], T[k]) && ldap_value_eq(T[k], OV[i], strlen(OV[i]), V[k], strlen(V[k]))) innew = 1;
                LAttr *a = attr_find(e, OT[i]);
                int j = a ? val_index(a, OV[i], strlen(OV[i])) : -1;
                if (!innew && j >= 0) { val_del(a, j); if (!a->nvals) attr_remove(e, OT[i]); }
            }
        }
        if (no > 0) { ldap_strv_free(OT, no); ldap_strv_free(OV, no); }
        stamp(e, cn, 0);
        /* rename descendants: snapshot their old names for rollback */
        int nd = 0;
        char **olddn = xmalloc(sizeof(char *) * (NE + 1)), **oldndn = xmalloc(sizeof(char *) * (NE + 1));
        int *which = xmalloc(sizeof(int) * (NE + 1));
        for (int i = 0; i < NE; i++) {
            int d = ndn_depth_below(E[i]->ndn, ndn);
            if (d <= 0) continue;
            char *nd2 = rebase_dn(E[i]->dn, d, newdn);
            char *nn2 = dn_normalize(nd2);
            if (!nn2) continue;
            olddn[nd] = E[i]->dn; oldndn[nd] = E[i]->ndn; which[nd++] = i;
            E[i]->dn = xstrdup(nd2); E[i]->ndn = nn2;
        }
        LEntry *old = E[idx];
        E[idx] = e;
        if (!dit_save()) {
            E[idx] = old; entry_free(e);
            for (int k = 0; k < nd; k++) { free(E[which[k]]->dn); free(E[which[k]]->ndn); E[which[k]]->dn = olddn[k]; E[which[k]]->ndn = oldndn[k]; }
            code = LDAP_OTHER; diag = "unable to write the directory database";
        } else {
            entry_free(old);
            for (int k = 0; k < nd; k++) { free(olddn[k]); free(oldndn[k]); }
        }
        free(olddn); free(oldndn); free(which);
    }
    pthread_rwlock_unlock(&dit_lock);
    ldap_strv_free(T, nr); ldap_strv_free(V, nr);
    free(ndn); free(nnew); free(nparent);
    dslog(cn, "MODRDN dn=\"%s\" newrdn=\"%s\" err=%d", dn, rdn, code);
    send_result(cn, msgid, LDAP_RES_MODDN, code, matched, diag);
}

static void do_compare(Conn *cn, long msgid, BerSlice op) {
    unsigned t; BerSlice name, ava, ad, av;
    if (!ber_next(&op, &t, &name) || t != BER_OCTETSTRING || !ber_next(&op, &t, &ava) || t != BER_SEQUENCE ||
        !ber_next(&ava, &t, &ad) || t != BER_OCTETSTRING || !ber_next(&ava, &t, &av) || t != BER_OCTETSTRING) {
        send_result(cn, msgid, LDAP_RES_COMPARE, LDAP_PROTOCOL_ERROR, NULL, "decoding error");
        return;
    }
    char *dn = kstrndup((const char *)name.p, name.n);
    char *attr = kstrndup((const char *)ad.p, ad.n);
    char *ndn = dn_normalize(dn);
    if (!ndn) { send_result(cn, msgid, LDAP_RES_COMPARE, LDAP_INVALID_DN_SYNTAX, NULL, "invalid DN"); return; }
    int code; const char *matched = NULL;
    dit_sync();
    pthread_rwlock_rdlock(&dit_lock);
    LEntry *e = find_entry(ndn);
    if (!e) { code = LDAP_NO_SUCH_OBJECT; matched = matched_dn(dn); }
    else if (!strcasecmp(attr, "userPassword") && !cn->is_root && strcmp(cn->nbinddn, ndn)) code = LDAP_INSUFFICIENT_ACCESS;
    else {
        LAttr *a = attr_find(e, attr);
        if (!a) code = LDAP_NO_SUCH_ATTRIBUTE;
        else {
            int hit = 0;
            for (int j = 0; j < a->nvals && !hit; j++)
                hit = !strcasecmp(attr, "userPassword") ? password_matches(a->vals[j].v, a->vals[j].n, (const char *)av.p, av.n)
                                                       : ldap_value_eq(a->name, a->vals[j].v, a->vals[j].n, (const char *)av.p, av.n);
            code = hit ? LDAP_COMPARE_TRUE : LDAP_COMPARE_FALSE;
        }
    }
    pthread_rwlock_unlock(&dit_lock);
    free(ndn);
    dslog(cn, "CMP dn=\"%s\" attr=\"%s\" err=%d", dn, attr, code);
    send_result(cn, msgid, LDAP_RES_COMPARE, code, matched, NULL);
}

static void do_extended(Conn *cn, long msgid, BerSlice op) {
    unsigned t; BerSlice oid;
    if (!ber_next(&op, &t, &oid) || t != 0x80) {
        send_result(cn, msgid, LDAP_RES_EXTENDED, LDAP_PROTOCOL_ERROR, NULL, "decoding error");
        return;
    }
    char *name = kstrndup((const char *)oid.p, oid.n);
    LBuf b; lb_init(&b);
    size_t m = ber_begin(&b, BER_SEQUENCE);
    ber_put_int(&b, BER_INTEGER, msgid);
    size_t r = ber_begin(&b, LDAP_RES_EXTENDED);
    if (!strcmp(name, "1.3.6.1.4.1.4203.1.11.3")) {           /* Who am I? */
        ber_put_int(&b, BER_ENUMERATED, LDAP_SUCCESS);
        ber_put_cstr(&b, BER_OCTETSTRING, "");
        ber_put_cstr(&b, BER_OCTETSTRING, "");
        char *who = *cn->binddn ? kprintf("dn:%s", cn->binddn) : "";
        ber_put_cstr(&b, 0x8b, who);
    } else {
        ber_put_int(&b, BER_ENUMERATED, LDAP_PROTOCOL_ERROR);
        ber_put_cstr(&b, BER_OCTETSTRING, "");
        ber_put_cstr(&b, BER_OCTETSTRING, !strcmp(name, "1.3.6.1.4.1.1466.20037") ?
                     "StartTLS is not supported (it is 1999: use a secure network)" : "unsupported extended operation");
    }
    ber_end(&b, r);
    ber_end(&b, m);
    send_msg(cn, &b);
    lb_free(&b);
    dslog(cn, "EXT oid=\"%s\"", name);
}

static void notice_of_disconnection(Conn *cn, int code, const char *diag) {
    LBuf b; lb_init(&b);
    size_t m = ber_begin(&b, BER_SEQUENCE);
    ber_put_int(&b, BER_INTEGER, 0);
    size_t r = ber_begin(&b, LDAP_RES_EXTENDED);
    ber_put_int(&b, BER_ENUMERATED, code);
    ber_put_cstr(&b, BER_OCTETSTRING, "");
    ber_put_cstr(&b, BER_OCTETSTRING, diag);
    ber_put_cstr(&b, 0x8a, "1.3.6.1.4.1.1466.20036");
    ber_end(&b, r);
    ber_end(&b, m);
    send_msg(cn, &b);
    lb_free(&b);
}

/* one LDAPMessage; returns 0 to close the connection */
static int handle_message(Conn *cn, LBuf *msg) {
    BerSlice all = {msg->p, msg->len}, seq, idv, op;
    unsigned t;
    long msgid;
    if (!ber_next(&all, &t, &seq) || t != BER_SEQUENCE || all.n ||
        !ber_next(&seq, &t, &idv) || t != BER_INTEGER || !ber_get_int(idv, &msgid) || msgid < 0 ||
        !ber_next(&seq, &t, &op)) {
        notice_of_disconnection(cn, LDAP_PROTOCOL_ERROR, "malformed LDAP message");
        return 0;
    }
    unsigned optag = t;
    /* controls: refuse critical ones we do not implement */
    if (seq.n) {
        BerSlice ctrls;
        if (!ber_next(&seq, &t, &ctrls) || t != 0xa0) { notice_of_disconnection(cn, LDAP_PROTOCOL_ERROR, "malformed controls"); return 0; }
        while (ctrls.n) {
            BerSlice ctl, ct, x;
            if (!ber_next(&ctrls, &t, &ctl) || t != BER_SEQUENCE || !ber_next(&ctl, &t, &ct) || t != BER_OCTETSTRING) {
                notice_of_disconnection(cn, LDAP_PROTOCOL_ERROR, "malformed controls");
                return 0;
            }
            int critical = 0;
            if (ber_peek_tag(&ctl) == BER_BOOLEAN && ber_next(&ctl, &t, &x)) critical = x.n && x.p[0];
            char *oid = kstrndup((const char *)ct.p, ct.n);
            if (critical && strcmp(oid, "2.16.840.1.113730.3.4.2") /* ManageDsaIT: no referrals here anyway */) {
                unsigned rt = optag == LDAP_REQ_BIND ? LDAP_RES_BIND : optag == LDAP_REQ_SEARCH ? LDAP_RES_SEARCH_DONE :
                              optag == LDAP_REQ_MODIFY ? LDAP_RES_MODIFY : optag == LDAP_REQ_ADD ? LDAP_RES_ADD :
                              optag == LDAP_REQ_DELETE ? LDAP_RES_DELETE : optag == LDAP_REQ_MODDN ? LDAP_RES_MODDN :
                              optag == LDAP_REQ_COMPARE ? LDAP_RES_COMPARE : LDAP_RES_EXTENDED;
                if (optag != LDAP_REQ_UNBIND && optag != LDAP_REQ_ABANDON)
                    send_result(cn, msgid, rt, LDAP_UNAVAILABLE_CRITICAL_EXTENSION, NULL, kprintf("critical control %s is not supported", oid));
                return optag != LDAP_REQ_UNBIND;
            }
        }
    }
    __sync_fetch_and_add(&nops, 1);
    switch (optag) {
    case LDAP_REQ_BIND: do_bind(cn, msgid, op); return 1;
    case LDAP_REQ_UNBIND: dslog(cn, "UNBIND"); return 0;
    case LDAP_REQ_SEARCH: do_search(cn, msgid, op); return 1;
    case LDAP_REQ_MODIFY: do_modify(cn, msgid, op); return 1;
    case LDAP_REQ_ADD: do_add(cn, msgid, op); return 1;
    case LDAP_REQ_DELETE: do_delete(cn, msgid, op); return 1;
    case LDAP_REQ_MODDN: do_moddn(cn, msgid, op); return 1;
    case LDAP_REQ_COMPARE: do_compare(cn, msgid, op); return 1;
    case LDAP_REQ_ABANDON: return 1;                         /* everything finishes immediately */
    case LDAP_REQ_EXTENDED: do_extended(cn, msgid, op); return 1;
    default:
        dslog(cn, "unknown operation tag 0x%02x err=2", optag);
        send_result(cn, msgid, LDAP_RES_EXTENDED, LDAP_PROTOCOL_ERROR, NULL, "unknown or unsupported operation");
        return 1;
    }
}

static void *conn_thread(void *arg) {
    Conn *cn = arg;
    LBuf msg; lb_init(&msg);
    dslog(cn, "connection from %s", cn->peer);
    for (;;) {
        int r = ber_read_message(cn->fd, &msg, MAX_MESSAGE);
        if (r == -2) {
            Arena *a = arena_new(); g_arena = a;
            notice_of_disconnection(cn, LDAP_PROTOCOL_ERROR, "malformed or oversized LDAP message");
            dslog(cn, "closed: malformed or oversized message");
            g_arena = NULL; arena_free(a);
            break;
        }
        if (r <= 0) break;
        Arena *a = arena_new();
        g_arena = a;
        int keep = handle_message(cn, &msg);
        g_arena = NULL;
        arena_free(a);
        if (!keep) break;
    }
    lb_free(&msg);
    close(cn->fd);
    free(cn->binddn); free(cn->nbinddn);
    free(cn);
    __sync_fetch_and_sub(&nconns, 1);
    return NULL;
}

static void *accept_loop(void *arg) {
    int lfd = (int)(intptr_t)arg;
    while (running) {
        struct sockaddr_storage sa; socklen_t sl = sizeof sa;
        int fd = accept4(lfd, (struct sockaddr *)&sa, &sl, SOCK_CLOEXEC);
        if (fd < 0) {
            if (!running) break;
            if (errno == EINTR || errno == ECONNABORTED || errno == EMFILE || errno == ENFILE) { usleep(10000); continue; }
            if (errno == EINVAL || errno == EBADF) break;
            continue;
        }
        if (__sync_add_and_fetch(&nconns, 1) > MAX_CONNS) {
            __sync_fetch_and_sub(&nconns, 1);
            close(fd);
            continue;
        }
        struct timeval tv = {300, 0};                        /* idle connections are dropped after 5 minutes */
        setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv);
        struct timeval tvs = {30, 0};
        setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tvs, sizeof tvs);
        Conn *cn = xmalloc(sizeof *cn);
        cn->fd = fd;
        cn->id = (int)__sync_add_and_fetch(&connseq, 1);
        cn->binddn = xstrdup(""); cn->nbinddn = xstrdup("");
        if (sa.ss_family == AF_INET) inet_ntop(AF_INET, &((struct sockaddr_in *)&sa)->sin_addr, cn->peer, sizeof cn->peer);
        else if (sa.ss_family == AF_INET6) inet_ntop(AF_INET6, &((struct sockaddr_in6 *)&sa)->sin6_addr, cn->peer, sizeof cn->peer);
        pthread_t th; pthread_attr_t at;
        pthread_attr_init(&at);
        pthread_attr_setdetachstate(&at, PTHREAD_CREATE_DETACHED);
        pthread_attr_setstacksize(&at, 512 * 1024);
        if (pthread_create(&th, &at, conn_thread, cn)) {
            close(fd); free(cn->binddn); free(cn->nbinddn); free(cn);
            __sync_fetch_and_sub(&nconns, 1);
        }
        pthread_attr_destroy(&at);
    }
    return NULL;
}

/* ================================================================ lifecycle */
static pthread_mutex_t life_mu = PTHREAD_MUTEX_INITIALIZER;

static void publish_scope(void);

/* caller holds life_mu */
static int ds_start(char *err, size_t el) {
    if (running) return 1;
    Conf *c = conf();                                   /* callers load the configuration */
    signal(SIGPIPE, SIG_IGN);
    pthread_rwlock_wrlock(&dit_lock);
    if (!dit_loaded) dit_load();
    pthread_rwlock_unlock(&dit_lock);
    struct addrinfo hints = {0}, *res;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;
    char ps[16]; snprintf(ps, sizeof ps, "%d", c->port);
    if (getaddrinfo(c->bind, ps, &hints, &res)) { snprintf(err, el, "Cannot resolve the bind address %s.", c->bind); return 0; }
    int fd = socket(res->ai_family, SOCK_STREAM | SOCK_CLOEXEC, 0);
    int one = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
    if (fd < 0 || bind(fd, res->ai_addr, res->ai_addrlen) || listen(fd, 64)) {
        snprintf(err, el, "Cannot listen on %s:%d: %s.", c->bind, c->port, strerror(errno));
        if (fd >= 0) close(fd);
        freeaddrinfo(res);
        return 0;
    }
    freeaddrinfo(res);
    listen_fd = fd;
    running = 1;
    started_at = date_now();
    if (pthread_create(&accept_thr, NULL, accept_loop, (void *)(intptr_t)fd)) {
        running = 0; close(fd); listen_fd = -1;
        snprintf(err, el, "Cannot start the listener thread.");
        return 0;
    }
    publish_scope();
    return 1;
}

static void ds_stop(void) {
    if (!running) return;
    running = 0;
    shutdown(listen_fd, SHUT_RDWR);
    close(listen_fd);
    pthread_join(accept_thr, NULL);
    listen_fd = -1;
}

void ldapd_override_port(int port) { override_port = port; }
void ldapd_disable(void) { disabled_flag = 1; }

void ldapd_startup(void) {
    install_ds_defaults();
    conf_reload();
    Conf *c = conf();
    if (!c->enabled) { printf("  Directory server  : disabled\n"); return; }
    char err[512];
    pthread_mutex_lock(&life_mu);
    int ok = ds_start(err, sizeof err);
    pthread_mutex_unlock(&life_mu);
    if (ok) printf("  Directory server  : ldap://%s:%d/%s\n", c->bind, c->port, c->base);
    else {
        printf("  Directory server  : not started - %s\n", err);
        kf_log("server.log", "Warning", "Gibson Directory Server not started: %s", err);
    }
}

void ldapd_set_lazy(void) {
    install_ds_defaults();
    conf_reload();
    lazy_mode = 1;
}

int ldapd_port(void) { Conf *c = conf(); return c ? c->port : 3890; }

/* kfserver --run: start the directory in-process the first time a page talks
 * to it and nothing is listening */
int ldapd_maybe_autostart(const char *host, int port) {
    if (!lazy_mode || running) return 0;
    Conf *c = conf();
    if (!c || !c->enabled || port != c->port) return 0;
    if (kf_stricmp(host, "localhost") && strcmp(host, "127.0.0.1") && kf_stricmp(host, c->bind)) return 0;
    char err[512];
    pthread_mutex_lock(&life_mu);
    int ok = ds_start(err, sizeof err);
    pthread_mutex_unlock(&life_mu);
    return ok;
}

static void publish_into(Struct *server) {
    Conf *c = conf();
    if (!c || !server) return;
    Struct *d = struct_new();
    struct_set(d, "Host", v_strdup(!strcmp(c->bind, "0.0.0.0") ? "127.0.0.1" : c->bind));
    struct_set(d, "Port", v_num(c->port));
    struct_set(d, "BaseDN", v_strdup(c->base));
    struct_set(d, "Enabled", v_bool(c->enabled));
    struct_set(d, "Product", v_str(DS_VENDOR_VERSION));
    struct_set(server, "Directory", v_struct(d));
}
void ldapd_server_scope(Struct *server) {
    if (!conf()) conf_reload();
    publish_into(server);
}
static void publish_scope(void) {
    if (!g_server_scope || !g_server_arena) return;
    Arena *saved = g_arena;
    g_arena = g_server_arena;
    publish_into(g_server_scope);
    g_arena = saved;
}

/* ================================================================ Administrator */
static Val status_struct(int ok, const char *msg) {
    Conf *c = conf();
    Struct *s = struct_new();
    struct_set(s, "OK", v_bool(ok));
    struct_set(s, "Message", v_strdup(msg));
    struct_set(s, "Running", v_bool(running));
    struct_set(s, "Port", v_num(c ? c->port : 0));
    struct_set(s, "BindAddress", v_strdup(c ? c->bind : ""));
    struct_set(s, "BaseDN", v_strdup(c ? c->base : ""));
    struct_set(s, "LDIFFile", v_strdup(c ? c->ldif : ""));
    pthread_rwlock_rdlock(&dit_lock);
    struct_set(s, "Entries", v_num(NE));
    pthread_rwlock_unlock(&dit_lock);
    struct_set(s, "Connections", v_num(nconns));
    struct_set(s, "Operations", v_num((double)nops));
    struct_set(s, "StartedAt", running ? v_date(started_at) : v_str(""));
    struct_set(s, "Product", v_str(DS_VENDOR_VERSION));
    return v_struct(s);
}

/* browse views for the Administrator: read the in-memory directory directly */
static Val admin_children(const char *dn) {
    const char *cols[] = {"DN", "RDN", "ObjectClass", "Children"};
    Query *q = query_new(4, cols);
    char *ndn = dn_normalize(dn);
    if (!ndn) return v_query(q);
    dit_sync();
    pthread_rwlock_rdlock(&dit_lock);
    for (int i = 0; i < NE; i++) {
        if (ndn_depth_below(E[i]->ndn, ndn) != 1) continue;
        int r = query_add_row(q);
        char *rdn = dn_first_rdn(E[i]->dn);
        query_set(q, 0, r, v_strdup(E[i]->dn));
        query_set(q, 1, r, v_strdup(rdn));
        free(rdn);
        LAttr *oc = attr_find(E[i], "objectClass");
        query_set(q, 2, r, v_strdup(oc && oc->nvals ? oc->vals[oc->nvals - 1].v : ""));
        query_set(q, 3, r, v_num(count_children(E[i]->ndn)));
    }
    pthread_rwlock_unlock(&dit_lock);
    free(ndn);
    return v_query(q);
}
static Val admin_entry(const char *dn) {
    const char *cols[] = {"Attribute", "Value"};
    Query *q = query_new(2, cols);
    char *ndn = dn_normalize(dn);
    if (!ndn) return v_query(q);
    dit_sync();
    pthread_rwlock_rdlock(&dit_lock);
    LEntry *e = find_entry(ndn);
    for (int i = 0; e && i < e->nattrs; i++)
        for (int j = 0; j < e->attrs[i].nvals; j++) {
            int r = query_add_row(q);
            query_set(q, 0, r, v_strdup(e->attrs[i].name));
            query_set(q, 1, r, v_str(kstrndup(e->attrs[i].vals[j].v, e->attrs[i].vals[j].n)));
        }
    pthread_rwlock_unlock(&dit_lock);
    free(ndn);
    return v_query(q);
}

/* KFUSION_DIRECTORYSERVER(action [, dn]): status | start | stop | restart | reload | reseed | children | entry */
F(kfusion_directoryserver) {
    const char *p = c->rs->cur_tpl ? c->rs->cur_tpl->path : "";
    char *dir = kf_path_join(G.webroot, "CFIDE/administrator");
    if (strncmp(p, dir, strlen(dir)))
        kf_throw_at(c, call, "Security", "The function KFUSION_DIRECTORYSERVER is reserved for the KoldFusion Administrator.",
                    "Undocumented KFUSION_ functions may only be called by templates in /CFIDE/administrator.");
    const char *action = argc ? fa_str(c, call, argv, 0) : "status";
    char err[512] = "";
    int ok = 1;
    const char *msg = "";
    if (!conf()) { install_ds_defaults(); conf_reload(); }
    if (!kf_stricmp(action, "children")) return admin_children(argc > 1 ? fa_str(c, call, argv, 1) : "");
    if (!kf_stricmp(action, "entry")) return admin_entry(argc > 1 ? fa_str(c, call, argv, 1) : "");
    pthread_mutex_lock(&life_mu);
    if (!kf_stricmp(action, "status")) {
        msg = running ? "The directory server is running." : "The directory server is stopped.";
    } else if (!kf_stricmp(action, "start") || !kf_stricmp(action, "restart")) {
        ds_stop();
        conf_reload();
        if (!conf()->enabled) msg = "The directory server is disabled.";
        else if ((ok = ds_start(err, sizeof err))) msg = kprintf("The directory server is listening on %s:%d.", conf()->bind, conf()->port);
        else msg = kprintf("The directory server could not be started: %s", err);
        publish_scope();
    } else if (!kf_stricmp(action, "stop")) {
        ds_stop();
        msg = "The directory server has been stopped.";
    } else if (!kf_stricmp(action, "reload") || !kf_stricmp(action, "reseed")) {
        pthread_rwlock_wrlock(&dit_lock);
        if (!kf_stricmp(action, "reseed")) unlink(conf()->ldif);
        dit_load();
        int n = NE;
        pthread_rwlock_unlock(&dit_lock);
        msg = kprintf(!kf_stricmp(action, "reseed") ? "The sample directory has been restored (%d entries)." : "The directory has been reloaded (%d entries).", n);
    } else {
        pthread_mutex_unlock(&life_mu);
        kf_throw_at(c, call, "Application", "Invalid action for KFUSION_DIRECTORYSERVER.",
                    "Use status, start, stop, restart, reload, reseed, children or entry.");
    }
    pthread_mutex_unlock(&life_mu);
    return status_struct(ok, msg);
}

const FuncDef LDAP_ADMIN_FUNCS[] = {
    {"kfusion_directoryserver", fn_kfusion_directoryserver, 0, 2},
    {NULL, NULL, 0, 0}
};
