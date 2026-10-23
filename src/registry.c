/*
 * registry.c - the KoldFusion "registry"
 *
 * ColdFusion 4.5 kept every setting in the Windows registry under
 * HKEY_LOCAL_MACHINE\SOFTWARE\Allaire\ColdFusion\CurrentVersion (and on Unix
 * in a flat-file emulation called cf.registry). We keep ours in a single
 * REGEDIT4-format file so you can double-click it in your imagination.
 */
#define _GNU_SOURCE
#include "engine.h"
#include <stdlib.h>
#include <ctype.h>
#include <pthread.h>
#include <time.h>

typedef struct REnt { char *name; char *value; int dword; } REnt;
typedef struct RKey { char *path; REnt *e; int n, cap; } RKey;

static RKey *keys; static int nkeys, capkeys;
static pthread_rwlock_t rw = PTHREAD_RWLOCK_INITIALIZER;
static char *reg_path;
static long version;
static time_t loaded_mtime;

#include <sys/stat.h>
static time_t file_mtime_of(const char *p) { struct stat st; return stat(p, &st) == 0 ? st.st_mtime : 0; }

static void free_all_keys(void) {
    for (int i = 0; i < nkeys; i++) {
        for (int j = 0; j < keys[i].n; j++) { free(keys[i].e[j].name); free(keys[i].e[j].value); }
        free(keys[i].e); free(keys[i].path);
    }
    nkeys = 0;
}

static void load_file(void);
/* another process (a second server, kfserver --run) may have written the
 * file; pick up its changes before we read or modify. Caller holds the write lock. */
static void refresh_locked(void) {
    time_t m = file_mtime_of(reg_path);
    if (m && m != loaded_mtime) { free_all_keys(); load_file(); loaded_mtime = m; }
}

static int key_index(const char *path) {
    for (int i = 0; i < nkeys; i++) if (!kf_stricmp(keys[i].path, path)) return i;
    return -1;
}

static char *norm_key(const char *k) {
    /* collapse forward slashes, strip trailing backslash */
    char *r = strdup(k);
    for (char *p = r; *p; p++) if (*p == '/') *p = '\\';
    size_t n = strlen(r);
    while (n && r[n - 1] == '\\') r[--n] = 0;
    return r;
}

static int key_create(const char *path) {
    int i = key_index(path);
    if (i >= 0) return i;
    /* ensure parents exist */
    char *p = strdup(path);
    char *bs = strrchr(p, '\\');
    if (bs) { *bs = 0; key_create(p); }
    free(p);
    if (nkeys == capkeys) { capkeys = capkeys ? capkeys * 2 : 64; keys = realloc(keys, sizeof(RKey) * capkeys); }
    memset(&keys[nkeys], 0, sizeof(RKey));
    keys[nkeys].path = strdup(path);
    return nkeys++;
}

static REnt *ent_find(RKey *k, const char *name) {
    for (int i = 0; i < k->n; i++) if (!kf_stricmp(k->e[i].name, name)) return &k->e[i];
    return NULL;
}

static void ent_set(RKey *k, const char *name, const char *value, int dword) {
    REnt *e = ent_find(k, name);
    if (!e) {
        if (k->n == k->cap) { k->cap = k->cap ? k->cap * 2 : 8; k->e = realloc(k->e, sizeof(REnt) * k->cap); }
        e = &k->e[k->n++];
        e->name = strdup(name);
        e->value = NULL;
    }
    free(e->value);
    e->value = strdup(value ? value : "");
    e->dword = dword;
}

static char *unescape(const char *s, const char **end) {
    /* s points just after opening quote */
    size_t n = 0, cap = 64;
    char *r = malloc(cap);
    while (*s && *s != '"') {
        char c = *s++;
        if (c == '\\' && *s) {
            char d = *s++;
            c = d == 'n' ? '\n' : d == 'r' ? '\r' : d == 't' ? '\t' : d;
        }
        if (n + 2 >= cap) { cap *= 2; r = realloc(r, cap); }
        r[n++] = c;
    }
    r[n] = 0;
    if (*s == '"') s++;
    *end = s;
    return r;
}

static void load_file(void) {
    size_t len;
    char *data = kf_read_file(reg_path, &len);
    if (!data) return;
    int cur = -1;
    char *line = data;
    while (line && *line) {
        char *nl = strchr(line, '\n');
        if (nl) *nl = 0;
        size_t ll = strlen(line);
        if (ll && line[ll - 1] == '\r') line[--ll] = 0;
        if (line[0] == '[') {
            char *e = strrchr(line, ']');
            if (e) { *e = 0; char *k = norm_key(line + 1); cur = key_create(k); free(k); }
        } else if (line[0] == '"' && cur >= 0) {
            const char *p;
            char *name = unescape(line + 1, &p);
            if (*p == '=') {
                p++;
                if (*p == '"') {
                    char *val = unescape(p + 1, &p);
                    ent_set(&keys[cur], name, val, 0);
                    free(val);
                } else if (!strncmp(p, "dword:", 6)) {
                    unsigned long v = strtoul(p + 6, NULL, 16);
                    char tmp[32]; snprintf(tmp, sizeof tmp, "%lu", v);
                    ent_set(&keys[cur], name, tmp, 1);
                }
            }
            free(name);
        }
        line = nl ? nl + 1 : NULL;
    }
    free(data);
}

static void put_escaped(FILE *f, const char *s) {
    for (; *s; s++) {
        if (*s == '"' || *s == '\\') { fputc('\\', f); fputc(*s, f); }
        else if (*s == '\n') fputs("\\n", f);
        else if (*s == '\r') fputs("\\r", f);
        else if (*s == '\t') fputs("\\t", f);
        else fputc(*s, f);
    }
}

static int cmp_keys(const void *a, const void *b) {
    return kf_stricmp(((const RKey *)a)->path, ((const RKey *)b)->path);
}

static void save_locked(void) {
    char tmp[4096];
    snprintf(tmp, sizeof tmp, "%s.tmp", reg_path);
    FILE *f = fopen(tmp, "w");
    if (!f) return;
    qsort(keys, nkeys, sizeof(RKey), cmp_keys);
    fprintf(f, "REGEDIT4\n\n");
    for (int i = 0; i < nkeys; i++) {
        fprintf(f, "[%s]\n", keys[i].path);
        for (int j = 0; j < keys[i].n; j++) {
            REnt *e = &keys[i].e[j];
            fputc('"', f); put_escaped(f, e->name); fputs("\"=", f);
            if (e->dword) fprintf(f, "dword:%08lx\n", strtoul(e->value, NULL, 10));
            else { fputc('"', f); put_escaped(f, e->value); fputs("\"\n", f); }
        }
        fputc('\n', f);
    }
    fclose(f);
    rename(tmp, reg_path);
    loaded_mtime = file_mtime_of(reg_path);
}

void reg_save(void) {
    pthread_rwlock_wrlock(&rw);
    save_locked();
    pthread_rwlock_unlock(&rw);
}

long reg_version(void) { return version; }

void reg_init(const char *path) {
    reg_path = strdup(path);
    pthread_rwlock_wrlock(&rw);
    load_file();
    loaded_mtime = file_mtime_of(reg_path);
    pthread_rwlock_unlock(&rw);
}

/* called before reads at most once a second */
static time_t last_check;
static void maybe_refresh(void) {
    time_t now = time(NULL);
    if (now == last_check) return;
    last_check = now;
    pthread_rwlock_wrlock(&rw);
    refresh_locked();
    pthread_rwlock_unlock(&rw);
}

char *reg_get(const char *key, const char *entry, const char *def) {
    maybe_refresh();
    char *k = norm_key(key);
    char *r = NULL;
    pthread_rwlock_rdlock(&rw);
    int i = key_index(k);
    if (i >= 0) {
        REnt *e = ent_find(&keys[i], entry);
        if (e) r = kstrdup(e->value);
    }
    pthread_rwlock_unlock(&rw);
    free(k);
    if (!r && def) r = kstrdup(def);
    return r;
}

int reg_get_int(const char *key, const char *entry, int def) {
    char *v = reg_get(key, entry, NULL);
    if (!v || !*v) return def;
    return atoi(v);
}

int reg_exists(const char *key, const char *entry) {
    char *k = norm_key(key);
    pthread_rwlock_rdlock(&rw);
    int i = key_index(k), r = 0;
    if (i >= 0) r = entry ? ent_find(&keys[i], entry) != NULL : 1;
    pthread_rwlock_unlock(&rw);
    free(k);
    return r;
}

void reg_set(const char *key, const char *entry, const char *value, int dword) {
    char *k = norm_key(key);
    pthread_rwlock_wrlock(&rw);
    refresh_locked();
    int i = key_create(k);
    if (entry) ent_set(&keys[i], entry, value, dword);
    version++;
    save_locked();
    pthread_rwlock_unlock(&rw);
    free(k);
}

void reg_delete_entry(const char *key, const char *entry) {
    char *k = norm_key(key);
    pthread_rwlock_wrlock(&rw);
    refresh_locked();
    int i = key_index(k);
    if (i >= 0) {
        RKey *rk = &keys[i];
        for (int j = 0; j < rk->n; j++) {
            if (!kf_stricmp(rk->e[j].name, entry)) {
                free(rk->e[j].name); free(rk->e[j].value);
                memmove(&rk->e[j], &rk->e[j + 1], sizeof(REnt) * (rk->n - j - 1));
                rk->n--;
                break;
            }
        }
        version++;
        save_locked();
    }
    pthread_rwlock_unlock(&rw);
    free(k);
}

void reg_delete_key(const char *key) {
    char *k = norm_key(key);
    size_t kl = strlen(k);
    pthread_rwlock_wrlock(&rw);
    refresh_locked();
    for (int i = 0; i < nkeys; ) {
        if (!kf_stricmp(keys[i].path, k) || (!kf_strnicmp(keys[i].path, k, kl) && keys[i].path[kl] == '\\')) {
            for (int j = 0; j < keys[i].n; j++) { free(keys[i].e[j].name); free(keys[i].e[j].value); }
            free(keys[i].e); free(keys[i].path);
            keys[i] = keys[--nkeys];
            continue;
        }
        i++;
    }
    version++;
    save_locked();
    pthread_rwlock_unlock(&rw);
    free(k);
}

Query *reg_list(const char *key, int want_keys, int want_values) {
    maybe_refresh();
    const char *cols[] = {"Entry", "Type", "Value"};
    Query *q = query_new(3, cols);
    char *k = norm_key(key);
    size_t kl = strlen(k);
    pthread_rwlock_rdlock(&rw);
    if (want_keys) {
        for (int i = 0; i < nkeys; i++) {
            const char *p = keys[i].path;
            if (!kf_strnicmp(p, k, kl) && p[kl] == '\\' && !strchr(p + kl + 1, '\\')) {
                int r = query_add_row(q);
                query_set(q, 0, r, v_strdup(p + kl + 1));
                query_set(q, 1, r, v_str("Key"));
                query_set(q, 2, r, v_str(""));
            }
        }
    }
    if (want_values) {
        int i = key_index(k);
        if (i >= 0) {
            for (int j = 0; j < keys[i].n; j++) {
                int r = query_add_row(q);
                query_set(q, 0, r, v_strdup(keys[i].e[j].name));
                query_set(q, 1, r, v_str(keys[i].e[j].dword ? "DWord" : "String"));
                query_set(q, 2, r, v_strdup(keys[i].e[j].value));
            }
        }
    }
    pthread_rwlock_unlock(&rw);
    free(k);
    return q;
}

char *cfg_key(const char *sub) {
    if (!sub || !*sub) return kstrdup(KF_REG_ROOT);
    return kprintf("%s\\%s", KF_REG_ROOT, sub);
}
char *cfg(const char *sub, const char *entry, const char *def) { return reg_get(cfg_key(sub), entry, def); }
int cfg_int(const char *sub, const char *entry, int def) { return reg_get_int(cfg_key(sub), entry, def); }
void cfg_set(const char *sub, const char *entry, const char *value) { reg_set(cfg_key(sub), entry, value, 0); }
