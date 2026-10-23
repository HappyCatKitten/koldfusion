/*
 * ldap.c - CFLDAP, an LDAPv3 client written from scratch (ColdFusion 4.5
 * linked the Netscape Directory SDK for this), and LDAP user directories for
 * Advanced Security.
 *
 *   <CFLDAP ACTION="Query" SERVER="localhost" PORT="3890" NAME="People"
 *           START="o=Gibson Mainframe Co, c=US" SCOPE="Subtree"
 *           FILTER="(sn=S*)" ATTRIBUTES="cn,mail,telephoneNumber" SORT="cn">
 *   <CFLDAP ACTION="Add" DN="uid=bob,ou=People,o=..." ATTRIBUTES="objectclass=top,person;cn=Bob;sn=Jensen" ...>
 *   <CFLDAP ACTION="Modify" MODIFYTYPE="Replace" DN="..." ATTRIBUTES="telephoneNumber=617-555-0100" ...>
 *   <CFLDAP ACTION="ModifyDN" DN="..." ATTRIBUTES="uid=robert" ...>
 *   <CFLDAP ACTION="Delete" DN="..." ...>
 *
 * Query results are a query object whose columns are the requested
 * attributes (plus DN for ATTRIBUTES="*" or when asked for); multi-valued
 * attributes are joined with ", ". Sorting is done client-side, as the
 * Netscape SDK did.
 */
#define _GNU_SOURCE
#include "engine.h"
#include "ldap.h"
#include <stdlib.h>
#include <strings.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <netdb.h>
#include <poll.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/time.h>

#define TAG(nm) void tag_##nm(Ctx *c, Node *n, int *flow)
#define CLIENT_MAX_MESSAGE (16 << 20)

/* ================================================================ connection */
typedef struct LConn {
    int fd;
    long msgid;
    int timeout;
    const char *host;
    int port;
} LConn;

typedef struct LResult {
    int code;
    const char *matched, *diag;
    Array *referrals;          /* of strings */
} LResult;

typedef struct CEntry {
    const char *dn;
    int n;
    const char **names;
    Array **vals;              /* arrays of strings */
} CEntry;

static int tcp_connect_timeout(const char *host, int port, int timeout, char *err, size_t el) {
    struct addrinfo hints = {0}, *res, *ai;
    hints.ai_socktype = SOCK_STREAM;
    char ps[16]; snprintf(ps, sizeof ps, "%d", port);
    int gr = getaddrinfo(host, ps, &hints, &res);
    if (gr) { snprintf(err, el, "Unknown host %s", host); return -1; }
    int fd = -1;
    snprintf(err, el, "Connection refused");
    for (ai = res; ai; ai = ai->ai_next) {
        fd = socket(ai->ai_family, SOCK_STREAM | SOCK_CLOEXEC, 0);
        if (fd < 0) continue;
        int fl = fcntl(fd, F_GETFL, 0);
        fcntl(fd, F_SETFL, fl | O_NONBLOCK);
        int r = connect(fd, ai->ai_addr, ai->ai_addrlen);
        if (r < 0 && errno == EINPROGRESS) {
            struct pollfd pf = {fd, POLLOUT, 0};
            r = poll(&pf, 1, timeout * 1000);
            if (r == 1) {
                int so = 0; socklen_t sl = sizeof so;
                getsockopt(fd, SOL_SOCKET, SO_ERROR, &so, &sl);
                if (so) { errno = so; r = -1; } else r = 0;
            } else { if (r == 0) errno = ETIMEDOUT; r = -1; }
        }
        if (r == 0) {
            fcntl(fd, F_SETFL, fl);
            struct timeval tv = {timeout, 0};
            setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv);
            setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof tv);
            break;
        }
        snprintf(err, el, "%s", errno == ETIMEDOUT ? "Connection timed out" : strerror(errno));
        close(fd);
        fd = -1;
    }
    freeaddrinfo(res);
    return fd;
}

static void lc_close(LConn *lc) {
    if (lc->fd < 0) return;
    /* UnbindRequest */
    LBuf b; lb_init(&b);
    size_t m = ber_begin(&b, BER_SEQUENCE);
    ber_put_int(&b, BER_INTEGER, ++lc->msgid);
    ber_put_str(&b, LDAP_REQ_UNBIND, "", 0);
    ber_end(&b, m);
    ldap_send_all(lc->fd, b.p, b.len);
    lb_free(&b);
    close(lc->fd);
    lc->fd = -1;
}

/* read the next message for msgid; returns op tag, or -1 (I/O, timeout), -2 (garbage) */
static int lc_read(LConn *lc, long msgid, LBuf *msg, BerSlice *op) {
    for (;;) {
        int r = ber_read_message(lc->fd, msg, CLIENT_MAX_MESSAGE);
        if (r == 0) return -1;
        if (r < 0) return r;
        BerSlice all = {msg->p, msg->len}, seq, idv;
        unsigned t; long id;
        if (!ber_next(&all, &t, &seq) || !ber_next(&seq, &t, &idv) || t != BER_INTEGER || !ber_get_int(idv, &id)) return -2;
        unsigned optag;
        if (!ber_next(&seq, &optag, op)) return -2;
        if (id == 0 && optag == LDAP_RES_EXTENDED) return -1;    /* notice of disconnection */
        if (id != msgid) continue;
        return (int)optag;
    }
}

static int parse_result(BerSlice op, LResult *res) {
    unsigned t; BerSlice code, matched, diag;
    long lcode;
    memset(res, 0, sizeof *res);
    if (!ber_next(&op, &t, &code) || t != BER_ENUMERATED || !ber_get_int(code, &lcode) ||
        !ber_next(&op, &t, &matched) || t != BER_OCTETSTRING || !ber_next(&op, &t, &diag) || t != BER_OCTETSTRING) return 0;
    res->code = (int)lcode;
    res->matched = kstrndup((const char *)matched.p, matched.n);
    res->diag = kstrndup((const char *)diag.p, diag.n);
    if (ber_peek_tag(&op) == 0xa3) {
        BerSlice refs, u;
        if (ber_next(&op, &t, &refs)) {
            res->referrals = array_new();
            while (refs.n && ber_next(&refs, &t, &u)) array_push(res->referrals, v_str(kstrndup((const char *)u.p, u.n)));
        }
    }
    return 1;
}

/* send a request whose protocolOp has been encoded into op; wait for the
 * response of the given tag; 0 on transport failure */
static int lc_simple_op(LConn *lc, LBuf *op, unsigned restag, LResult *res) {
    LBuf b; lb_init(&b);
    long id = ++lc->msgid;
    size_t m = ber_begin(&b, BER_SEQUENCE);
    ber_put_int(&b, BER_INTEGER, id);
    lb_put(&b, op->p, op->len);
    ber_end(&b, m);
    int ok = ldap_send_all(lc->fd, b.p, b.len);
    lb_free(&b);
    if (!ok) return 0;
    LBuf msg; lb_init(&msg);
    BerSlice ops;
    int tag = lc_read(lc, id, &msg, &ops);
    ok = tag == (int)restag && parse_result(ops, res);
    if (tag == -2 || (tag >= 0 && !ok)) { res->code = LDAP_DECODING_ERROR; res->diag = "The server's reply could not be decoded."; ok = 1; }
    lb_free(&msg);
    return ok;
}

static int lc_bind(LConn *lc, const char *dn, const char *pw, LResult *res) {
    LBuf op; lb_init(&op);
    size_t m = ber_begin(&op, LDAP_REQ_BIND);
    ber_put_int(&op, BER_INTEGER, 3);
    ber_put_cstr(&op, BER_OCTETSTRING, dn);
    ber_put_cstr(&op, 0x80, pw);
    ber_end(&op, m);
    int ok = lc_simple_op(lc, &op, LDAP_RES_BIND, res);
    lb_free(&op);
    return ok;
}

/* search; entries appended to *out. returns 0 on transport failure */
static int lc_search(LConn *lc, const char *base, int scope, LBuf *filter, Array *attrs, int sizelimit, int timelimit,
                     CEntry ***out, int *nout, int *cap, Array *refs, LResult *res) {
    LBuf b; lb_init(&b);
    long id = ++lc->msgid;
    size_t m = ber_begin(&b, BER_SEQUENCE);
    ber_put_int(&b, BER_INTEGER, id);
    size_t s = ber_begin(&b, LDAP_REQ_SEARCH);
    ber_put_cstr(&b, BER_OCTETSTRING, base);
    ber_put_int(&b, BER_ENUMERATED, scope);
    ber_put_int(&b, BER_ENUMERATED, 0);                  /* neverDerefAliases */
    ber_put_int(&b, BER_INTEGER, sizelimit);
    ber_put_int(&b, BER_INTEGER, timelimit);
    ber_put_bool(&b, BER_BOOLEAN, 0);
    lb_put(&b, filter->p, filter->len);
    size_t al = ber_begin(&b, BER_SEQUENCE);
    for (int i = 0; attrs && i < attrs->n; i++) ber_put_cstr(&b, BER_OCTETSTRING, v_tostr(attrs->v[i]));
    ber_end(&b, al);
    ber_end(&b, s);
    ber_end(&b, m);
    int ok = ldap_send_all(lc->fd, b.p, b.len);
    lb_free(&b);
    if (!ok) return 0;
    LBuf msg; lb_init(&msg);
    for (;;) {
        BerSlice op;
        int tag = lc_read(lc, id, &msg, &op);
        if (tag < 0) {
            lb_free(&msg);
            if (tag == -2) { memset(res, 0, sizeof *res); res->code = LDAP_DECODING_ERROR; res->diag = "The server's reply could not be decoded."; return 1; }
            return 0;
        }
        if (tag == LDAP_RES_SEARCH_ENTRY) {
            unsigned t; BerSlice dn, al2, one, type, set, v;
            if (!ber_next(&op, &t, &dn) || t != BER_OCTETSTRING || !ber_next(&op, &t, &al2) || t != BER_SEQUENCE) continue;
            CEntry *e = kmalloc(sizeof *e);
            e->dn = kstrndup((const char *)dn.p, dn.n);
            int ecap = 8;
            e->names = kmalloc(sizeof(char *) * ecap);
            e->vals = kmalloc(sizeof(Array *) * ecap);
            while (al2.n && ber_next(&al2, &t, &one)) {
                if (!ber_next(&one, &t, &type) || !ber_next(&one, &t, &set)) break;
                if (e->n == ecap) {
                    ecap *= 2;
                    const char **nn = kmalloc(sizeof(char *) * ecap); memcpy(nn, e->names, sizeof(char *) * e->n); e->names = nn;
                    Array **nv = kmalloc(sizeof(Array *) * ecap); memcpy(nv, e->vals, sizeof(Array *) * e->n); e->vals = nv;
                }
                e->names[e->n] = kstrndup((const char *)type.p, type.n);
                Array *vals = array_new();
                while (set.n && ber_next(&set, &t, &v)) array_push(vals, v_str(kstrndup((const char *)v.p, v.n)));
                e->vals[e->n++] = vals;
            }
            if (*nout == *cap) {
                *cap = *cap ? *cap * 2 : 64;
                CEntry **ne = kmalloc(sizeof(CEntry *) * *cap);
                if (*nout) memcpy(ne, *out, sizeof(CEntry *) * *nout);
                *out = ne;
            }
            (*out)[(*nout)++] = e;
        } else if (tag == LDAP_RES_SEARCH_REF) {
            unsigned t; BerSlice u;
            while (op.n && ber_next(&op, &t, &u)) if (refs) array_push(refs, v_str(kstrndup((const char *)u.p, u.n)));
        } else if (tag == LDAP_RES_SEARCH_DONE) {
            if (!parse_result(op, res)) { res->code = LDAP_DECODING_ERROR; res->diag = "The server's reply could not be decoded."; }
            break;
        }
    }
    lb_free(&msg);
    return 1;
}

/* ================================================================ errors */
static void throw_ldap(Ctx *c, const char *action, int code, const char *diag, const char *matched) {
    Buf d; buf_init(&d);
    if (diag && *diag) buf_printf(&d, code >= LDAP_SERVER_DOWN ? "%s. " : "The LDAP server returned: %s. ", diag);
    if (matched && *matched) buf_printf(&d, "The closest matching entry is %s. ", matched);
    buf_puts(&d, "One or more of the required attributes may be missing or incorrect or you do not have permissions "
                 "to execute this operation on the server.");
    KfError *e = kf_error_new("Application",
        kprintf("An error has occured while trying to execute %s :[LDAP: error code %d - %s]", action, code, ldap_result_name(code)),
        kf_html_escape(buf_cstr(&d)));
    e->errorcode = kprintf("%d", code);
    kf_throw_err(c->rs, e);
}

static void throw_attr(Ctx *c, const char *attr, const char *val, const char *valid) {
    kf_throw(c, "Application", "Attribute validation error for tag CFLDAP.",
             kprintf("The value of the attribute %s, which is currently \"%s\", is invalid. Valid values are: %s.",
                     attr, kf_html_escape(val), valid));
}

/* ================================================================ helpers */
typedef struct LdapUrl { const char *host; int port; const char *dn; int scope; } LdapUrl;

static int parse_ldap_url(const char *url, LdapUrl *u) {
    memset(u, 0, sizeof *u);
    u->port = 389; u->scope = -1; u->dn = NULL;
    if (kf_strnicmp(url, "ldap://", 7)) return 0;
    const char *p = url + 7;
    const char *slash = strchr(p, '/');
    char *hp = slash ? kstrndup(p, slash - p) : kstrdup(p);
    char *colon = strrchr(hp, ':');
    if (colon && !strchr(hp, ']')) { *colon = 0; u->port = atoi(colon + 1); }
    u->host = *hp ? hp : "localhost";
    if (slash) {
        char *rest = kstrdup(slash + 1);
        char *q = strchr(rest, '?');
        if (q) {
            *q = 0;
            char *sc = strchr(q + 1, '?');
            if (sc) {
                char *e = strchr(sc + 1, '?'); if (e) *e = 0;
                if (!kf_stricmp(sc + 1, "base")) u->scope = 0;
                else if (!kf_stricmp(sc + 1, "one")) u->scope = 1;
                else if (!kf_stricmp(sc + 1, "sub")) u->scope = 2;
            }
        }
        if (*rest) u->dn = kf_urldecode(rest, strlen(rest));
    }
    return 1;
}

static int open_conn(Ctx *c, LConn *lc, const char *host, int port, int timeout, const char *action, int throw_on_fail) {
    char err[256];
    memset(lc, 0, sizeof *lc);
    lc->host = host; lc->port = port; lc->timeout = timeout;
    lc->fd = tcp_connect_timeout(host, port, timeout, err, sizeof err);
    if (lc->fd < 0 && ldapd_maybe_autostart(host, port))
        lc->fd = tcp_connect_timeout(host, port, timeout, err, sizeof err);
    if (lc->fd < 0 && throw_on_fail) {
        KfError *e = kf_error_new("Application", "Connection to LDAP server failed.",
            kf_html_escape(kprintf("Unable to connect to the LDAP server %s on port %d (%s) to execute %s. "
                                   "Check that the server is running and that the SERVER and PORT attributes are correct.",
                                   host, port, err, action)));
        e->errorcode = kprintf("%d", LDAP_CONNECT_ERROR);
        kf_throw_err(c->rs, e);
    }
    return lc->fd >= 0;
}

/* connect + bind, throwing CF errors */
static void connect_bind(Ctx *c, LConn *lc, const char *host, int port, int timeout, const char *user, const char *pass, const char *action) {
    open_conn(c, lc, host, port, timeout, action, 1);
    if (user && *user) {
        LResult r;
        if (!lc_bind(lc, user, pass ? pass : "", &r)) {
            close(lc->fd); lc->fd = -1;
            throw_ldap(c, action, LDAP_SERVER_DOWN, "The connection was closed during the bind", NULL);
        }
        if (r.code != LDAP_SUCCESS) { close(lc->fd); lc->fd = -1; throw_ldap(c, action, r.code, r.diag, NULL); }
    }
}

static char *colname(const char *attr) {
    char *s = kstrdup(attr);
    for (char *p = s; *p; p++) if (!isalnum((unsigned char)*p) && *p != '_') *p = '_';
    if (isdigit((unsigned char)*s)) s = kprintf("_%s", s);
    return s;
}

static const char *entry_value(CEntry *e, const char *attr, const char *sep) {
    for (int i = 0; i < e->n; i++) {
        if (!ldap_attr_eq(e->names[i], attr)) continue;
        Buf b; buf_init(&b);
        Array *a = e->vals[i];
        for (int j = 0; j < a->n; j++) { if (j) buf_puts(&b, sep); buf_puts(&b, v_tostr(a->v[j])); }
        return buf_cstr(&b);
    }
    return "";
}

/* split "a, b ,c" into trimmed non-empty items */
static Array *split_list(const char *s, const char *delims) {
    Array *out = array_new();
    Array *a = list_to_array_k(s, delims);
    for (int i = 0; i < a->n; i++) {
        char *t = kf_trim(v_tostr(a->v[i]));
        if (*t) array_push(out, v_str(t));
    }
    return out;
}

/* sorting (client side, like the Netscape SDK's ldap_multisort_entries) */
typedef struct SortKey { const char *attr; int desc; } SortKey;
static __thread SortKey *t_sk;
static __thread int t_nsk, t_nocase;
static int cmp_entries(const void *a, const void *b) {
    CEntry *x = *(CEntry *const *)a, *y = *(CEntry *const *)b;
    for (int i = 0; i < t_nsk; i++) {
        const char *vx = !kf_stricmp(t_sk[i].attr, "dn") ? x->dn : entry_value(x, t_sk[i].attr, ", ");
        const char *vy = !kf_stricmp(t_sk[i].attr, "dn") ? y->dn : entry_value(y, t_sk[i].attr, ", ");
        int r = t_nocase ? kf_stricmp(vx, vy) : strcmp(vx, vy);
        if (t_sk[i].desc) r = -r;
        if (r) return r;
    }
    return strcmp(x->dn, y->dn);     /* qsort is not stable: keep ties in a fixed order */
}

/* "name=value;name=value" (DELIMITER) with SEPARATOR between multiple values */
typedef struct AttrMod { const char *name; Array *vals; } AttrMod;
static AttrMod *parse_attr_pairs(Ctx *c, const char *s, const char *delim, const char *sep, int *n) {
    Array *pairs = list_to_array_k(s, delim);
    AttrMod *m = kmalloc(sizeof(AttrMod) * (pairs->n + 1));
    int k = 0;
    for (int i = 0; i < pairs->n; i++) {
        const char *p = v_tostr(pairs->v[i]);
        if (!*kf_trim(p)) continue;
        const char *eq = strchr(p, '=');
        if (!eq)
            kf_throw(c, "Application", "Attribute validation error for tag CFLDAP.",
                     kprintf("The ATTRIBUTES value \"%s\" must be a list of name=value pairs separated by \"%s\".",
                             kf_html_escape(p), kf_html_escape(delim)));
        int j;
        const char *name = kf_trim(kstrndup(p, eq - p));
        for (j = 0; j < k; j++) if (ldap_attr_eq(m[j].name, name)) break;
        if (j == k) { m[k].name = name; m[k].vals = array_new(); k++; }
        const char *val = eq + 1;
        if (!*kf_trim(val)) continue;
        Array *vs = list_to_array_k(val, sep);
        for (int x = 0; x < vs->n; x++) {
            char *t = kf_trim(v_tostr(vs->v[x]));
            if (*t) array_push(m[j].vals, v_str(t));
        }
    }
    *n = k;
    return m;
}

static void put_attr_list(LBuf *b, AttrMod *m, int n) {
    for (int i = 0; i < n; i++) {
        size_t s = ber_begin(b, BER_SEQUENCE);
        ber_put_cstr(b, BER_OCTETSTRING, m[i].name);
        size_t set = ber_begin(b, BER_SET);
        for (int j = 0; j < m[i].vals->n; j++) ber_put_cstr(b, BER_OCTETSTRING, v_tostr(m[i].vals->v[j]));
        ber_end(b, set);
        ber_end(b, s);
    }
}

/* ================================================================ CFLDAP */
static void do_query(Ctx *c, Node *n, const char *server, int port, const char *user, const char *pass, int timeout,
                     int referral_hops, int rebind) {
    const char *name = require_attr(c, n, "name");
    const char *start = require_attr(c, n, "start");
    const char *attrs = require_attr(c, n, "attributes");
    const char *scope_s = attr_str(c, n, "scope", "onelevel");
    int scope;
    if (!kf_stricmp(scope_s, "base")) scope = 0;
    else if (!kf_stricmp(scope_s, "onelevel")) scope = 1;
    else if (!kf_stricmp(scope_s, "subtree")) scope = 2;
    else throw_attr(c, "SCOPE", scope_s, "ONELEVEL, BASE, SUBTREE");
    const char *filter = attr_str(c, n, "filter", "objectclass=*");
    int maxrows = (int)attr_num(c, n, "maxrows", -1);
    int startrow = (int)attr_num(c, n, "startrow", 1);
    if (startrow < 1) startrow = 1;
    const char *sort = attr_str(c, n, "sort", "");
    const char *sortcontrol = attr_str(c, n, "sortcontrol", "asc");
    const char *sep = has_attr(n, "separator") ? attr_str(c, n, "separator", ",") : ", ";

    LBuf fbm; lb_init(&fbm);
    const char *ferr = NULL;
    if (!ldap_filter_encode(&fbm, filter, &ferr)) {
        lb_free(&fbm);
        throw_ldap(c, "query", LDAP_FILTER_ERROR, kprintf("Bad filter %s: %s", filter, ferr), NULL);
    }
    /* keep the encoded filter in the request arena, so errors thrown below leak nothing */
    LBuf fb;
    fb.p = kmalloc(fbm.len); memcpy(fb.p, fbm.p, fbm.len);
    fb.len = fb.cap = fbm.len;
    lb_free(&fbm);

    /* columns and the attributes to ask the server for */
    Array *req = split_list(attrs, ",");
    int all = 0, want_dn = 0;
    Array *ask = array_new();
    for (int i = 0; i < req->n; i++) {
        const char *a = v_tostr(req->v[i]);
        if (!strcmp(a, "*")) all = 1;
        else if (!kf_stricmp(a, "dn")) want_dn = 1;
        else array_push(ask, v_str(a));
    }
    if (all) { want_dn = 1; ask = array_new(); array_push(ask, v_str("*")); }
    /* sort keys */
    int nsk = 0;
    SortKey *sk = NULL;
    if (*sort) {
        Array *ks = split_list(sort, ",");
        sk = kmalloc(sizeof(SortKey) * (ks->n + 1));
        for (int i = 0; i < ks->n; i++) {
            char *k = kstrdup(v_tostr(ks->v[i]));
            char *sp = strpbrk(k, " \t");
            sk[nsk].desc = 0;
            if (sp) {
                char *dir = kf_trim(sp);
                *sp = 0;
                if (!kf_stricmp(dir, "desc")) sk[nsk].desc = 1;
                else if (kf_stricmp(dir, "asc")) throw_attr(c, "SORT", v_tostr(ks->v[i]), "attribute [ASC|DESC]");
            }
            sk[nsk].attr = k;
            if (!all && kf_stricmp(k, "dn")) {
                int have = 0;
                for (int j = 0; j < ask->n; j++) if (ldap_attr_eq(v_tostr(ask->v[j]), k)) have = 1;
                if (!have) array_push(ask, v_str(k));
            }
            nsk++;
        }
    }
    int nocase = 0, desc = 0;
    Array *sc = split_list(sortcontrol, ",");
    for (int i = 0; i < sc->n; i++) {
        const char *t = v_tostr(sc->v[i]);
        if (!kf_stricmp(t, "nocase")) nocase = 1;
        else if (!kf_stricmp(t, "desc")) desc = 1;
        else if (!kf_stricmp(t, "asc")) desc = 0;
        else throw_attr(c, "SORTCONTROL", sortcontrol, "NOCASE, ASC, DESC");
    }
    if (desc) for (int i = 0; i < nsk; i++) sk[i].desc = !sk[i].desc;
    if (!ask->n) array_push(ask, v_str("1.1"));

    int sizelimit = (!nsk && maxrows >= 0) ? startrow - 1 + maxrows : 0;
    if (maxrows == 0) sizelimit = 0;
    CEntry **ents = NULL; int nent = 0, cap = 0;
    Array *refs = array_new();
    LResult res;
    double t0 = kf_time_ms();
    LConn lconn, *lc = &lconn;
    connect_bind(c, lc, server, port, timeout, user, pass, "query");
    if (!lc_search(lc, start, scope, &fb, ask, sizelimit, timeout, &ents, &nent, &cap, refs, &res)) {
        close(lc->fd); lc->fd = -1;
        throw_ldap(c, "query", LDAP_SERVER_DOWN, "The connection to the server was lost", NULL);
    }
    lc_close(lc);
    /* referrals: REFERRAL="hops" follows them, REBIND="Yes" re-uses the credentials */
    if (res.code == LDAP_REFERRAL && res.referrals) for (int i = 0; i < res.referrals->n; i++) array_push(refs, res.referrals->v[i]);
    if (res.code == LDAP_REFERRAL && referral_hops > 0 && refs->n) res.code = LDAP_SUCCESS;
    for (int hop = 0; hop < referral_hops && refs->n; hop++) {
        Array *next = array_new();
        for (int i = 0; i < refs->n; i++) {
            LdapUrl u;
            if (!parse_ldap_url(v_tostr(refs->v[i]), &u)) continue;
            LConn rc;
            if (!open_conn(c, &rc, u.host, u.port, timeout, "query", 0)) continue;
            LResult br;
            if (rebind && user && *user && (!lc_bind(&rc, user, pass, &br) || br.code)) { close(rc.fd); continue; }
            LResult rr;
            if (lc_search(&rc, u.dn ? u.dn : start, u.scope >= 0 ? u.scope : scope, &fb, ask, sizelimit, timeout, &ents, &nent, &cap, next, &rr)) {
                if (rr.code == LDAP_REFERRAL && rr.referrals) for (int k = 0; k < rr.referrals->n; k++) array_push(next, rr.referrals->v[k]);
            }
            lc_close(&rc);
        }
        refs = next;
    }
    double ms = kf_time_ms() - t0;
    if (res.code != LDAP_SUCCESS && res.code != LDAP_SIZELIMIT_EXCEEDED && res.code != LDAP_TIMELIMIT_EXCEEDED)
        throw_ldap(c, "query", res.code, res.diag, res.matched);

    if (nsk && nent > 1) {
        t_sk = sk; t_nsk = nsk; t_nocase = nocase;
        qsort(ents, nent, sizeof(CEntry *), cmp_entries);
    }

    /* build the query */
    Query *q = query_new(0, NULL);
    Array *cols = array_new();          /* attribute names, parallel to query columns (NULL = DN) */
    if (all) {
        query_add_column(q, "DN"); array_push(cols, v_str(""));
        for (int i = 0; i < nent; i++)
            for (int k = 0; k < ents[i]->n; k++) {
                const char *cn = colname(ents[i]->names[k]);
                if (query_col_index(q, cn) < 0) { query_add_column(q, cn); array_push(cols, v_str(ents[i]->names[k])); }
            }
    } else {
        for (int i = 0; i < req->n; i++) {
            const char *a = v_tostr(req->v[i]);
            const char *cn = !kf_stricmp(a, "dn") ? a : colname(a);
            if (query_col_index(q, cn) >= 0) continue;
            query_add_column(q, cn);
            array_push(cols, v_str(!kf_stricmp(a, "dn") ? "" : a));
        }
    }
    int first = startrow - 1, last = maxrows >= 0 ? first + maxrows : nent;
    if (last > nent) last = nent;
    for (int i = first; i < last; i++) {
        int r = query_add_row(q);
        for (int k = 0; k < cols->n; k++) {
            const char *a = v_tostr(cols->v[k]);
            query_set(q, k, r, v_str(*a ? entry_value(ents[i], a, sep) : ents[i]->dn));
        }
    }
    (void)want_dn;
    q->name = kstrdup(name);
    q->sql = kprintf("LDAP search: base \"%s\", scope %s, filter %s, attributes %s", start, scope_s, filter, attrs);
    q->datasource = kprintf("ldap://%s:%d", lc->host, lc->port);
    q->exectime_ms = ms;
    RState *rs = c->rs;
    if (rs->show_query_info) {
        DebugQuery *dq = kmalloc(sizeof(DebugQuery));
        dq->name = q->name; dq->datasource = q->datasource; dq->sql = q->sql; dq->ms = ms;
        dq->records = q->nrows;
        dq->template = rs->cur_tpl ? rs->cur_tpl->path : "";
        dq->next = rs->dq; rs->dq = dq;
    }
    assign_path(c, name, v_query(q));
}

static void check_result(Ctx *c, LConn *lc, int ok, LResult *r, const char *action) {
    if (!ok) { close(lc->fd); lc->fd = -1; throw_ldap(c, action, LDAP_SERVER_DOWN, "The connection to the server was lost", NULL); }
    if (r->code != LDAP_SUCCESS) { lc_close(lc); throw_ldap(c, action, r->code, r->diag, r->matched); }
}

TAG(ldap) {
    (void)flow;
    tag_security_check(c, "cfldap");
    const char *action = attr_str(c, n, "action", "query");
    const char *act;
    if (!kf_stricmp(action, "query")) act = "query";
    else if (!kf_stricmp(action, "add")) act = "add";
    else if (!kf_stricmp(action, "modify")) act = "modify";
    else if (!kf_stricmp(action, "modifydn")) act = "modifyDN";
    else if (!kf_stricmp(action, "delete")) act = "delete";
    else throw_attr(c, "ACTION", action, "QUERY, ADD, MODIFY, MODIFYDN, DELETE");
    const char *server = require_attr(c, n, "server");
    int port = (int)attr_num(c, n, "port", 389);
    if (port <= 0 || port > 65535) throw_attr(c, "PORT", attr_str(c, n, "port", ""), "a port number between 1 and 65535");
    int timeout = (int)attr_num(c, n, "timeout", 60);
    if (timeout >= 1000) timeout /= 1000;                  /* CFMX-era pages give milliseconds */
    if (timeout <= 0) timeout = 60;
    const char *user = attr_str(c, n, "username", "");
    const char *pass = attr_str(c, n, "password", "");
    int referral = (int)attr_num(c, n, "referral", 0);
    int rebind = attr_bool(c, n, "rebind", 0);
    if (has_attr(n, "secure"))
        kf_throw(c, "Application", "Error processing CFLDAP",
                 kprintf("Secure LDAP connections (SECURE=\"%s\") require the Netscape SSL libraries, which are not installed "
                         "on this KoldFusion server.", kf_html_escape(attr_str(c, n, "secure", ""))));
    const char *delim = attr_str(c, n, "delimiter", ";");
    const char *sep = attr_str(c, n, "separator", ",");
    if (!*delim) delim = ";";
    if (!*sep) sep = ",";

    if (!strcmp(act, "query")) {
        do_query(c, n, server, port, user, pass, timeout, referral, rebind);
        return;
    }
    /* validate everything before connecting: nothing below may throw while a socket is open
     * or the request buffer is allocated */
    const char *dn = require_attr(c, n, "dn");
    const char *newrdn = NULL, *mt = NULL;
    AttrMod *mods = NULL;
    int na = 0, mop = 2;
    if (!strcmp(act, "modifyDN")) newrdn = kf_trim(require_attr(c, n, "attributes"));
    else if (strcmp(act, "delete")) {
        mods = parse_attr_pairs(c, require_attr(c, n, "attributes"), delim, sep, &na);
        if (!strcmp(act, "modify")) {
            mt = attr_str(c, n, "modifytype", "replace");
            if (!kf_stricmp(mt, "add")) mop = 0;
            else if (!kf_stricmp(mt, "delete")) mop = 1;
            else if (!kf_stricmp(mt, "replace")) mop = 2;
            else throw_attr(c, "MODIFYTYPE", mt, "ADD, DELETE, REPLACE");
        }
    }
    LConn lc;
    connect_bind(c, &lc, server, port, timeout, user, pass, act);
    LBuf op; lb_init(&op);
    LResult r;
    unsigned restag;
    if (!strcmp(act, "delete")) {
        ber_put_cstr(&op, LDAP_REQ_DELETE, dn);
        restag = LDAP_RES_DELETE;
    } else if (!strcmp(act, "modifyDN")) {
        size_t m = ber_begin(&op, LDAP_REQ_MODDN);
        ber_put_cstr(&op, BER_OCTETSTRING, dn);
        ber_put_cstr(&op, BER_OCTETSTRING, newrdn);
        ber_put_bool(&op, BER_BOOLEAN, 1);
        ber_end(&op, m);
        restag = LDAP_RES_MODDN;
    } else {
        if (!strcmp(act, "add")) {
            size_t m = ber_begin(&op, LDAP_REQ_ADD);
            ber_put_cstr(&op, BER_OCTETSTRING, dn);
            size_t l = ber_begin(&op, BER_SEQUENCE);
            put_attr_list(&op, mods, na);
            ber_end(&op, l);
            ber_end(&op, m);
            restag = LDAP_RES_ADD;
        } else {
            size_t m = ber_begin(&op, LDAP_REQ_MODIFY);
            ber_put_cstr(&op, BER_OCTETSTRING, dn);
            size_t l = ber_begin(&op, BER_SEQUENCE);
            for (int i = 0; i < na; i++) {
                size_t ch = ber_begin(&op, BER_SEQUENCE);
                ber_put_int(&op, BER_ENUMERATED, mop);
                put_attr_list(&op, &mods[i], 1);
                ber_end(&op, ch);
            }
            ber_end(&op, l);
            ber_end(&op, m);
            restag = LDAP_RES_MODIFY;
        }
    }
    int ok = lc_simple_op(&lc, &op, restag, &r);
    lb_free(&op);
    check_result(c, &lc, ok, &r, act);
    lc_close(&lc);
}

/* ================================================================ Advanced Security */
static char *filter_escape(const char *s) {
    Buf b; buf_init(&b);
    for (; *s; s++) {
        if (*s == '*' || *s == '(' || *s == ')' || *s == '\\' || (unsigned char)*s < 0x20) buf_printf(&b, "\\%02x", (unsigned char)*s);
        else buf_putc(&b, *s);
    }
    return buf_cstr(&b);
}
static char *dn_value_escape(const char *s) {
    Buf b; buf_init(&b);
    for (const char *p = s; *p; p++) {
        if (strchr(",+\"\\<>;=", *p) || (p == s && (*p == '#' || *p == ' ')) || (!p[1] && *p == ' ')) buf_putc(&b, '\\');
        buf_putc(&b, *p);
    }
    return buf_cstr(&b);
}

/* small cache so the cookie re-check on every request does not cost an LDAP bind */
typedef struct AuthCache { char key[512]; unsigned char pw[16]; char *groups; double at; int ok; } AuthCache;
static AuthCache acache[64];
static pthread_mutex_t acache_mu = PTHREAD_MUTEX_INITIALIZER;

int ldap_dir_authenticate(const char *dirkey, const char *user, const char *pass, char **groups) {
    *groups = "";
    if (!user || !*user || !pass || !*pass) return 0;     /* an empty password would be an anonymous bind */
    unsigned char pw[16];
    md5((const unsigned char *)pass, strlen(pass), pw);
    char key[512];
    snprintf(key, sizeof key, "%s|%s", dirkey, user);
    double now = kf_time_ms();
    pthread_mutex_lock(&acache_mu);
    for (int i = 0; i < 64; i++) {
        if (acache[i].at && now - acache[i].at < 60000 && !strcmp(acache[i].key, key) && !memcmp(acache[i].pw, pw, 16)) {
            int ok = acache[i].ok;
            *groups = kstrdup(acache[i].groups ? acache[i].groups : "");
            pthread_mutex_unlock(&acache_mu);
            return ok;
        }
    }
    pthread_mutex_unlock(&acache_mu);

    const char *loc = reg_get(dirkey, "Location", "localhost");
    LdapUrl u;
    if (!kf_strnicmp(loc, "ldap://", 7)) parse_ldap_url(loc, &u);
    else {
        u.host = kstrdup(kf_trim(loc)); u.port = 389;
        char *colon = strrchr((char *)u.host, ':');
        if (colon) { *colon = 0; u.port = atoi(colon + 1); }
    }
    const char *root = reg_get(dirkey, "Root", "");
    const char *svc = reg_get(dirkey, "Username", "");
    const char *svcpw = kf_unscramble(reg_get(dirkey, "Password", ""));
    const char *ls = reg_get(dirkey, "LookupStart", ""), *le = reg_get(dirkey, "LookupEnd", "");
    const char *uattr = reg_get(dirkey, "UserAttribute", "uid");
    if (!*uattr) uattr = "uid";
    LConn lc;
    char err[256];
    memset(&lc, 0, sizeof lc);
    lc.host = u.host; lc.port = u.port; lc.timeout = 10;
    lc.fd = tcp_connect_timeout(u.host, u.port, 10, err, sizeof err);
    if (lc.fd < 0 && ldapd_maybe_autostart(u.host, u.port)) lc.fd = tcp_connect_timeout(u.host, u.port, 10, err, sizeof err);
    if (lc.fd < 0) { kf_log("application.log", "Error", "LDAP user directory %s: cannot connect to %s:%d (%s)", dirkey, u.host, u.port, err); return 0; }
    LResult r;
    const char *userdn = NULL;
    int ok = 0;
    Buf gb; buf_init(&gb);
    if (*ls || *le) userdn = kprintf("%s%s%s", ls, dn_value_escape(user), le);
    else {
        if (*svc && (!lc_bind(&lc, svc, svcpw, &r) || r.code)) goto done;
        LBuf f; lb_init(&f);
        ldap_filter_encode(&f, kprintf("(%s=%s)", uattr, filter_escape(user)), NULL);
        Array *a = array_new(); array_push(a, v_str("1.1"));
        CEntry **ents = NULL; int ne = 0, cap = 0;
        int sok = lc_search(&lc, root, 2, &f, a, 2, 10, &ents, &ne, &cap, NULL, &r);
        lb_free(&f);
        if (!sok || r.code || ne != 1) goto done;
        userdn = ents[0]->dn;
    }
    if (!lc_bind(&lc, userdn, pass, &r) || r.code) goto done;
    ok = 1;
    /* groups: groupOfUniqueNames (Netscape) or groupOfNames entries listing the user */
    {
        char *esc = filter_escape(userdn);
        LBuf f; lb_init(&f);
        ldap_filter_encode(&f, kprintf("(|(uniqueMember=%s)(member=%s))", esc, esc), NULL);
        Array *a = array_new(); array_push(a, v_str("cn"));
        CEntry **ents = NULL; int ne = 0, cap = 0;
        if (lc_search(&lc, root, 2, &f, a, 0, 10, &ents, &ne, &cap, NULL, &r))
            for (int i = 0; i < ne; i++) {
                const char *cn = entry_value(ents[i], "cn", ",");
                if (*cn) { if (gb.len) buf_putc(&gb, ','); buf_puts(&gb, cn); }
            }
        lb_free(&f);
    }
done:
    lc_close(&lc);
    *groups = buf_cstr(&gb);
    pthread_mutex_lock(&acache_mu);
    int slot = 0;
    for (int i = 0; i < 64; i++) if (acache[i].at < acache[slot].at) slot = i;
    free(acache[slot].groups);
    snprintf(acache[slot].key, sizeof acache[slot].key, "%s", key);
    memcpy(acache[slot].pw, pw, 16);
    acache[slot].groups = strdup(*groups);
    acache[slot].ok = ok;
    acache[slot].at = now;
    pthread_mutex_unlock(&acache_mu);
    return ok;
}
