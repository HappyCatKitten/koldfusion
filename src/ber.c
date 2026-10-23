/*
 * ber.c - the Basic Encoding Rules subset LDAPv3 needs (RFC 4511 section 5.1),
 * RFC 2254 string filters, distinguished names, plus SHA-1 and base64 for
 * {SHA} passwords and LDIF.  Shared by the CFLDAP client and the Gibson
 * Directory Server.
 *
 * The decoder is network-facing: every length is checked against what is
 * left, only definite lengths of at most four octets and single-octet tags
 * are accepted, and recursion is depth-limited.
 */
#define _GNU_SOURCE
#include "ldap.h"
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <stdio.h>
#include <ctype.h>
#include <errno.h>
#include <unistd.h>
#include <sys/socket.h>

static void *xrealloc(void *p, size_t n) {
    void *q = realloc(p, n ? n : 1);
    if (!q) { fprintf(stderr, "KoldFusion: out of memory (LDAP)\n"); abort(); }
    return q;
}

const char *ldap_result_name(int code) {
    switch (code) {
    case 0: return "Success";
    case 1: return "Operations Error";
    case 2: return "Protocol Error";
    case 3: return "Time Limit Exceeded";
    case 4: return "Size Limit Exceeded";
    case 5: return "Compare False";
    case 6: return "Compare True";
    case 7: return "Authentication Method Not Supported";
    case 8: return "Strong Authentication Required";
    case 10: return "Referral";
    case 11: return "Administrative Limit Exceeded";
    case 12: return "Unavailable Critical Extension";
    case 13: return "Confidentiality Required";
    case 14: return "SASL Bind In Progress";
    case 16: return "No Such Attribute";
    case 17: return "Undefined Attribute Type";
    case 18: return "Inappropriate Matching";
    case 19: return "Constraint Violation";
    case 20: return "Attribute Or Value Exists";
    case 21: return "Invalid Attribute Syntax";
    case 32: return "No Such Object";
    case 33: return "Alias Problem";
    case 34: return "Invalid DN Syntax";
    case 36: return "Alias Dereferencing Problem";
    case 48: return "Inappropriate Authentication";
    case 49: return "Invalid Credentials";
    case 50: return "Insufficient Access Rights";
    case 51: return "Busy";
    case 52: return "Unavailable";
    case 53: return "Unwilling To Perform";
    case 54: return "Loop Detect";
    case 64: return "Naming Violation";
    case 65: return "Object Class Violation";
    case 66: return "Not Allowed On Non-leaf";
    case 67: return "Not Allowed On RDN";
    case 68: return "Entry Already Exists";
    case 69: return "Object Class Modifications Prohibited";
    case 71: return "Affects Multiple DSAs";
    case 80: return "Other";
    case 81: return "Can't contact LDAP server";
    case 82: return "Local error";
    case 83: return "Encoding error";
    case 84: return "Decoding error";
    case 85: return "Timed out";
    case 87: return "Bad search filter";
    case 89: return "Bad parameter to an ldap routine";
    case 91: return "Can't connect to the LDAP server";
    default: return "Unknown error";
    }
}

/* ================================================================ encoder */
void lb_init(LBuf *b) { b->p = NULL; b->len = b->cap = 0; }
void lb_free(LBuf *b) { free(b->p); lb_init(b); }
static void lb_reserve(LBuf *b, size_t extra) {
    if (b->len + extra <= b->cap) return;
    size_t nc = b->cap ? b->cap * 2 : 256;
    while (nc < b->len + extra) nc *= 2;
    b->p = xrealloc(b->p, nc);
    b->cap = nc;
}
void lb_put(LBuf *b, const void *data, size_t n) {
    lb_reserve(b, n);
    if (n) memcpy(b->p + b->len, data, n);
    b->len += n;
}
static void lb_byte(LBuf *b, unsigned char c) { lb_put(b, &c, 1); }

static void put_len(LBuf *b, size_t n) {
    if (n < 128) { lb_byte(b, (unsigned char)n); return; }
    unsigned char tmp[8]; int k = 0;
    while (n) { tmp[k++] = n & 0xff; n >>= 8; }
    lb_byte(b, 0x80 | k);
    while (k) lb_byte(b, tmp[--k]);
}

size_t ber_begin(LBuf *b, unsigned tag) {
    lb_byte(b, (unsigned char)tag);
    lb_byte(b, 0);                    /* placeholder, fixed by ber_end */
    return b->len - 1;
}
void ber_end(LBuf *b, size_t mark) {
    size_t clen = b->len - mark - 1;
    if (clen < 128) { b->p[mark] = (unsigned char)clen; return; }
    unsigned char tmp[8]; int k = 0;
    size_t n = clen;
    while (n) { tmp[k++] = n & 0xff; n >>= 8; }
    lb_reserve(b, k);
    memmove(b->p + mark + 1 + k, b->p + mark + 1, clen);
    b->len += k;
    b->p[mark] = 0x80 | k;
    for (int i = 0; i < k; i++) b->p[mark + 1 + i] = tmp[k - 1 - i];
}
void ber_put_int(LBuf *b, unsigned tag, long v) {
    unsigned char tmp[sizeof(long) + 1];
    int k = 0;
    /* two's complement, minimal */
    for (;;) {
        tmp[k++] = (unsigned char)(v & 0xff);
        long rest = v >> 8;
        if ((rest == 0 && !(tmp[k - 1] & 0x80)) || (rest == -1 && (tmp[k - 1] & 0x80))) break;
        v = rest;
        if (k == (int)sizeof tmp) break;
    }
    lb_byte(b, (unsigned char)tag);
    put_len(b, k);
    while (k) lb_byte(b, tmp[--k]);
}
void ber_put_str(LBuf *b, unsigned tag, const char *s, size_t n) {
    lb_byte(b, (unsigned char)tag);
    put_len(b, n);
    lb_put(b, s, n);
}
void ber_put_cstr(LBuf *b, unsigned tag, const char *s) { ber_put_str(b, tag, s ? s : "", s ? strlen(s) : 0); }
void ber_put_bool(LBuf *b, unsigned tag, int v) {
    lb_byte(b, (unsigned char)tag);
    lb_byte(b, 1);
    lb_byte(b, v ? 0xff : 0x00);
}

/* ================================================================ decoder */
int ber_next(BerSlice *s, unsigned *tag, BerSlice *content) {
    if (!s || s->n < 2) return 0;
    const unsigned char *p = s->p;
    size_t n = s->n;
    unsigned t = p[0];
    if ((t & 0x1f) == 0x1f) return 0;            /* multi-octet tags: not used by LDAP */
    size_t i = 1;
    size_t len;
    unsigned char l0 = p[i++];
    if (l0 < 0x80) len = l0;
    else {
        int k = l0 & 0x7f;
        if (k == 0 || k > 4) return 0;          /* indefinite or absurd */
        if (n - i < (size_t)k) return 0;
        len = 0;
        for (int j = 0; j < k; j++) len = (len << 8) | p[i++];
    }
    if (len > n - i) return 0;
    if (tag) *tag = t;
    if (content) { content->p = p + i; content->n = len; }
    s->p = p + i + len;
    s->n = n - i - len;
    return 1;
}

int ber_peek_tag(const BerSlice *s) { return (s && s->n) ? s->p[0] : -1; }

int ber_get_int(BerSlice v, long *out) {
    if (v.n < 1 || v.n > sizeof(long)) return 0;
    long r = (v.p[0] & 0x80) ? -1 : 0;
    for (size_t i = 0; i < v.n; i++) r = (long)(((unsigned long)r << 8) | v.p[i]);
    *out = r;
    return 1;
}

char *ber_dup(BerSlice v) {
    char *s = xrealloc(NULL, v.n + 1);
    if (v.n) memcpy(s, v.p, v.n);
    s[v.n] = 0;
    return s;
}

static int read_full(int fd, unsigned char *p, size_t n) {
    size_t got = 0;
    while (got < n) {
        ssize_t r = recv(fd, p + got, n - got, 0);
        if (r == 0) return got ? -1 : 0;
        if (r < 0) { if (errno == EINTR) continue; return -1; }
        got += r;
    }
    return 1;
}

int ber_read_message(int fd, LBuf *out, size_t max) {
    out->len = 0;
    unsigned char hdr[6];
    int r = read_full(fd, hdr, 2);
    if (r <= 0) return r;
    if (hdr[0] != BER_SEQUENCE) return -2;
    size_t len;
    size_t hl = 2;
    if (hdr[1] < 0x80) len = hdr[1];
    else {
        int k = hdr[1] & 0x7f;
        if (k == 0 || k > 4) return -2;
        if (read_full(fd, hdr + 2, k) != 1) return -1;
        len = 0;
        for (int j = 0; j < k; j++) len = (len << 8) | hdr[2 + j];
        hl += k;
    }
    if (len > max) return -2;
    lb_reserve(out, hl + len);
    lb_put(out, hdr, hl);
    if (len && read_full(fd, out->p + hl, len) != 1) return -1;
    out->len = hl + len;
    return 1;
}

int ldap_send_all(int fd, const void *p, size_t n) {
    const unsigned char *c = p;
    while (n) {
        ssize_t w = send(fd, c, n, MSG_NOSIGNAL);
        if (w < 0) { if (errno == EINTR) continue; return 0; }
        c += w; n -= w;
    }
    return 1;
}

/* ================================================================ string filters */
typedef struct FP { const char *s; size_t i; const char *err; int depth; } FP;

static void fp_ws(FP *f) { while (f->s[f->i] == ' ' || f->s[f->i] == '\t' || f->s[f->i] == '\r' || f->s[f->i] == '\n') f->i++; }
static int hexv(int c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

/* unescape a raw value segment: \hh hex (RFC 2254) or \c (RFC 1960 leniency) */
static void put_unescaped(LBuf *out, const char *p, size_t n) {
    for (size_t i = 0; i < n; i++) {
        if (p[i] == '\\' && i + 1 < n) {
            int h1 = hexv((unsigned char)p[i + 1]), h2 = i + 2 < n ? hexv((unsigned char)p[i + 2]) : -1;
            if (h1 >= 0 && h2 >= 0) { lb_byte(out, (unsigned char)(h1 * 16 + h2)); i += 2; }
            else { lb_byte(out, (unsigned char)p[i + 1]); i++; }
        } else lb_byte(out, (unsigned char)p[i]);
    }
}
static void put_value(LBuf *b, unsigned tag, const char *p, size_t n) {
    LBuf v; lb_init(&v);
    put_unescaped(&v, p, n);
    ber_put_str(b, tag, (const char *)v.p, v.len);
    lb_free(&v);
}

static int fp_filter(FP *f, LBuf *b);

static int fp_item(FP *f, LBuf *b) {
    const char *s = f->s;
    fp_ws(f);
    size_t a0 = f->i;
    while (s[f->i] && !strchr("=~<>():", s[f->i])) f->i++;
    size_t a1 = f->i;
    while (a1 > a0 && (s[a1 - 1] == ' ' || s[a1 - 1] == '\t')) a1--;
    /* extensible match: attr[:dn][:rule]:=value */
    size_t ext0 = 0, ext1 = 0; int is_ext = 0;
    if (s[f->i] == ':') {
        ext0 = f->i;
        while (s[f->i] && !(s[f->i] == ':' && s[f->i + 1] == '=') && s[f->i] != ')' && s[f->i] != '(') f->i++;
        if (s[f->i] != ':') { f->err = "Bad extensible match filter"; return 0; }
        ext1 = f->i;
        f->i += 2;
        is_ext = 1;
    }
    int op = 0;   /* '=', '~', '>', '<' */
    if (!is_ext) {
        if (a1 == a0) { f->err = "Missing attribute name in filter"; return 0; }
        char c = s[f->i];
        if (c == '=') { op = '='; f->i++; }
        else if ((c == '~' || c == '>' || c == '<') && s[f->i + 1] == '=') { op = c; f->i += 2; }
        else { f->err = "Missing or unknown filter operator"; return 0; }
    }
    /* value: up to the closing parenthesis; unescaped '(' is an error */
    size_t v0 = f->i;
    while (s[f->i] && s[f->i] != ')') {
        if (s[f->i] == '(') { f->err = "Unescaped parenthesis in filter value"; return 0; }
        if (s[f->i] == '\\' && s[f->i + 1]) f->i++;
        f->i++;
    }
    size_t v1 = f->i;
    while (v0 < v1 && (s[v0] == ' ' || s[v0] == '\t')) v0++;
    while (v1 > v0 && (s[v1 - 1] == ' ' || s[v1 - 1] == '\t') && !(v1 - v0 >= 2 && s[v1 - 2] == '\\')) v1--;

    if (is_ext) {
        size_t m = ber_begin(b, LDAP_FILTER_EXT);
        /* pieces between ext0 and ext1: ":dn", ":rule" */
        int dnattrs = 0; const char *rule = NULL; size_t rlen = 0;
        size_t i = ext0;
        while (i < ext1) {
            i++;   /* skip ':' */
            size_t p0 = i;
            while (i < ext1 && s[i] != ':') i++;
            if (i - p0 == 2 && !strncasecmp(s + p0, "dn", 2)) dnattrs = 1;
            else if (i > p0) { rule = s + p0; rlen = i - p0; }
        }
        if (!rule && a1 == a0) { f->err = "Extensible match needs an attribute or a matching rule"; return 0; }
        if (rule) ber_put_str(b, 0x81, rule, rlen);
        if (a1 > a0) ber_put_str(b, 0x82, s + a0, a1 - a0);
        put_value(b, 0x83, s + v0, v1 - v0);
        if (dnattrs) ber_put_bool(b, 0x84, 1);
        ber_end(b, m);
        return 1;
    }
    /* count unescaped stars */
    int stars = 0;
    for (size_t i = v0; i < v1; i++) { if (s[i] == '\\' && i + 1 < v1) { i++; continue; } if (s[i] == '*') stars++; }
    if (op == '=' && stars && v1 - v0 == (size_t)stars) {        /* present (also tolerate "**") */
        ber_put_str(b, LDAP_FILTER_PRESENT, s + a0, a1 - a0);
        return 1;
    }
    if (op == '=' && stars) {
        size_t m = ber_begin(b, LDAP_FILTER_SUBSTR);
        ber_put_str(b, BER_OCTETSTRING, s + a0, a1 - a0);
        size_t m2 = ber_begin(b, BER_SEQUENCE);
        size_t seg0 = v0; int segno = 0;
        for (size_t i = v0; i <= v1; i++) {
            if (i < v1 && s[i] == '\\' && i + 1 < v1) { i++; continue; }
            if (i == v1 || s[i] == '*') {
                if (i > seg0) {
                    unsigned t = segno == 0 ? 0x80 : (i == v1 ? 0x82 : 0x81);
                    put_value(b, t, s + seg0, i - seg0);
                }
                segno++;
                seg0 = i + 1;
            }
        }
        ber_end(b, m2);
        ber_end(b, m);
        return 1;
    }
    unsigned tag = op == '=' ? LDAP_FILTER_EQUALITY : op == '~' ? LDAP_FILTER_APPROX : op == '>' ? LDAP_FILTER_GE : LDAP_FILTER_LE;
    size_t m = ber_begin(b, tag);
    ber_put_str(b, BER_OCTETSTRING, s + a0, a1 - a0);
    put_value(b, BER_OCTETSTRING, s + v0, v1 - v0);
    ber_end(b, m);
    return 1;
}

static int fp_filter(FP *f, LBuf *b) {
    if (++f->depth > 64) { f->err = "Filter is nested too deeply"; return 0; }
    fp_ws(f);
    if (f->s[f->i] != '(') { f->err = "Filter must start with a parenthesis"; return 0; }
    f->i++;
    fp_ws(f);
    char c = f->s[f->i];
    if (c == '&' || c == '|') {
        f->i++;
        size_t m = ber_begin(b, c == '&' ? LDAP_FILTER_AND : LDAP_FILTER_OR);
        fp_ws(f);
        while (f->s[f->i] == '(') {
            if (!fp_filter(f, b)) return 0;
            fp_ws(f);
        }
        ber_end(b, m);
    } else if (c == '!') {
        f->i++;
        size_t m = ber_begin(b, LDAP_FILTER_NOT);
        if (!fp_filter(f, b)) return 0;
        ber_end(b, m);
        fp_ws(f);
    } else {
        if (!fp_item(f, b)) return 0;
    }
    if (f->s[f->i] != ')') { f->err = "Missing closing parenthesis in filter"; return 0; }
    f->i++;
    f->depth--;
    return 1;
}

int ldap_filter_encode(LBuf *b, const char *filter, const char **err) {
    while (*filter == ' ' || *filter == '\t') filter++;
    char *tmp = NULL;
    if (!*filter) filter = "(objectClass=*)";
    if (*filter != '(') {
        size_t n = strlen(filter);
        tmp = xrealloc(NULL, n + 3);
        tmp[0] = '('; memcpy(tmp + 1, filter, n); tmp[n + 1] = ')'; tmp[n + 2] = 0;
        filter = tmp;
    }
    FP f = {filter, 0, NULL, 0};
    size_t start = b->len;
    int ok = fp_filter(&f, b);
    if (ok) { fp_ws(&f); if (f.s[f.i]) { ok = 0; f.err = "Unexpected text after the filter"; } }
    if (!ok) { b->len = start; if (err) *err = f.err ? f.err : "Bad search filter"; }
    free(tmp);
    return ok;
}

static int ava_valid(BerSlice c) {
    unsigned t; BerSlice x;
    if (!ber_next(&c, &t, &x) || t != BER_OCTETSTRING || !x.n) return 0;
    if (!ber_next(&c, &t, &x) || t != BER_OCTETSTRING) return 0;
    return c.n == 0;
}

int ldap_filter_valid(BerSlice f, int depth) {
    if (depth > 64) return 0;
    unsigned tag; BerSlice c;
    if (!ber_next(&f, &tag, &c) || f.n) return 0;
    switch (tag) {
    case LDAP_FILTER_AND: case LDAP_FILTER_OR:
        while (c.n) {
            BerSlice one = c; unsigned t; BerSlice x;
            if (!ber_next(&c, &t, &x)) return 0;
            one.n = (size_t)(c.p - one.p);
            if (!ldap_filter_valid(one, depth + 1)) return 0;
        }
        return 1;
    case LDAP_FILTER_NOT:
        return ldap_filter_valid(c, depth + 1);
    case LDAP_FILTER_EQUALITY: case LDAP_FILTER_GE: case LDAP_FILTER_LE: case LDAP_FILTER_APPROX:
        return ava_valid(c);
    case LDAP_FILTER_PRESENT:
        return c.n > 0;
    case LDAP_FILTER_SUBSTR: {
        unsigned t; BerSlice x, seq;
        if (!ber_next(&c, &t, &x) || t != BER_OCTETSTRING || !x.n) return 0;
        if (!ber_next(&c, &t, &seq) || t != BER_SEQUENCE || c.n) return 0;
        int n = 0;
        while (seq.n) {
            if (!ber_next(&seq, &t, &x) || (t != 0x80 && t != 0x81 && t != 0x82)) return 0;
            n++;
        }
        return n > 0;
    }
    case LDAP_FILTER_EXT: {
        unsigned t; BerSlice x; int hasval = 0;
        while (c.n) {
            if (!ber_next(&c, &t, &x)) return 0;
            if (t == 0x83) hasval = 1;
            else if (t != 0x81 && t != 0x82 && t != 0x84) return 0;
        }
        return hasval;
    }
    default:
        return 0;
    }
}

/* ================================================================ DNs */
static const struct { const char *alias, *canon; } ALIASES[] = {
    {"commonname", "cn"}, {"surname", "sn"}, {"userid", "uid"}, {"rfc822mailbox", "mail"},
    {"organizationname", "o"}, {"organizationalunitname", "ou"}, {"countryname", "c"},
    {"localityname", "l"}, {"stateorprovincename", "st"}, {"gn", "givenName"},
    {"domaincomponent", "dc"}, {"streetaddress", "street"}, {"mobiletelephonenumber", "mobile"},
    {"facsimiletelephonenumber", "facsimileTelephoneNumber"}, {"objectclasses", "objectClass"},
    {NULL, NULL}
};
const char *ldap_attr_canon(const char *name) {
    for (int i = 0; ALIASES[i].alias; i++) if (!strcasecmp(name, ALIASES[i].alias)) return ALIASES[i].canon;
    return name;
}
int ldap_attr_eq(const char *a, const char *b) {
    if (!strcasecmp(a, b)) return 1;
    return !strcasecmp(ldap_attr_canon(a), ldap_attr_canon(b));
}

static int is_space(int c) { return c == ' ' || c == '\t' || c == '\r' || c == '\n'; }

/* scan to the end of one RDN (unescaped ',' or ';') starting at p; returns index */
static size_t rdn_end(const char *p) {
    size_t i = 0; int q = 0;
    while (p[i]) {
        if (p[i] == '\\' && p[i + 1]) { i += 2; continue; }
        if (p[i] == '"') q = !q;
        else if (!q && (p[i] == ',' || p[i] == ';')) break;
        i++;
    }
    return i;
}

static char *trimdup(const char *p, size_t n) {
    while (n && is_space(*p)) { p++; n--; }
    while (n && is_space(p[n - 1]) && !(n >= 2 && p[n - 2] == '\\')) n--;
    char *s = xrealloc(NULL, n + 1);
    memcpy(s, p, n); s[n] = 0;
    return s;
}

char *dn_first_rdn(const char *dn) { return trimdup(dn, rdn_end(dn)); }
char *dn_parent(const char *dn) {
    size_t e = rdn_end(dn);
    if (!dn[e]) return trimdup("", 0);
    return trimdup(dn + e + 1, strlen(dn + e + 1));
}

void ldap_strv_free(char **v, int n) { if (!v) return; for (int i = 0; i < n; i++) free(v[i]); free(v); }

/* parse "type=value[+type=value]"; values unescaped. returns count, -1 on error */
int rdn_split(const char *rdn, char ***types, char ***values) {
    int n = 0, cap = 4;
    char **T = xrealloc(NULL, cap * sizeof(char *)), **V = xrealloc(NULL, cap * sizeof(char *));
    const char *p = rdn;
    for (;;) {
        while (is_space(*p)) p++;
        const char *t0 = p;
        while (*p && *p != '=' && *p != '+' && *p != ',') p++;
        if (*p != '=') goto bad;
        const char *t1 = p;
        while (t1 > t0 && is_space(t1[-1])) t1--;
        if (t1 == t0) goto bad;
        p++;
        while (is_space(*p)) p++;
        LBuf v; lb_init(&v);
        if (*p == '"') {                                     /* LDAPv2 quoted value */
            p++;
            while (*p && *p != '"') {
                if (*p == '\\' && p[1]) p++;
                lb_byte(&v, (unsigned char)*p++);
            }
            if (*p != '"') { lb_free(&v); goto bad; }
            p++;
            while (is_space(*p)) p++;
        } else {
            size_t lastsig = 0;    /* length up to last significant (non-trailing-space) char */
            while (*p && *p != '+' && *p != ',' && *p != ';') {
                if (*p == '\\') {
                    int h1 = hexv((unsigned char)p[1]), h2 = h1 >= 0 ? hexv((unsigned char)p[2]) : -1;
                    if (h1 >= 0 && h2 >= 0) { lb_byte(&v, (unsigned char)(h1 * 16 + h2)); p += 3; }
                    else if (p[1]) { lb_byte(&v, (unsigned char)p[1]); p += 2; }
                    else { lb_free(&v); goto bad; }
                    lastsig = v.len;
                    continue;
                }
                lb_byte(&v, (unsigned char)*p);
                if (!is_space(*p)) lastsig = v.len;
                p++;
            }
            v.len = lastsig;
        }
        lb_byte(&v, 0);
        if (n == cap) { cap *= 2; T = xrealloc(T, cap * sizeof(char *)); V = xrealloc(V, cap * sizeof(char *)); }
        T[n] = trimdup(t0, t1 - t0);
        V[n] = (char *)v.p;
        n++;
        if (*p == '+') { p++; continue; }
        while (is_space(*p)) p++;
        if (*p) goto bad;
        break;
    }
    *types = T; *values = V;
    return n;
bad:
    ldap_strv_free(T, n); ldap_strv_free(V, n);
    *types = *values = NULL;
    return -1;
}

static void norm_value_into(LBuf *out, const char *v) {
    /* case-fold, collapse runs of spaces, escape specials as \hh */
    const unsigned char *s = (const unsigned char *)v;
    while (is_space(*s)) s++;
    int first = 1, pend_space = 0;
    for (; *s; s++) {
        if (is_space(*s)) { pend_space = 1; continue; }
        if (pend_space && !first) lb_byte(out, ' ');
        pend_space = 0;
        unsigned char c = (unsigned char)tolower(*s);
        if (strchr(",+\"\\<>;=", c) || c < 0x20 || (first && c == '#')) {
            char h[4]; snprintf(h, sizeof h, "\\%02x", c);
            lb_put(out, h, 3);
        } else lb_byte(out, c);
        first = 0;
    }
}

static int cmp_str(const void *a, const void *b) { return strcmp(*(char *const *)a, *(char *const *)b); }

char *dn_normalize(const char *dn) {
    LBuf out; lb_init(&out);
    const char *p = dn;
    while (is_space(*p)) p++;
    int first = 1;
    while (*p) {
        size_t e = rdn_end(p);
        char *raw = trimdup(p, e);
        char **T, **V;
        int n = rdn_split(raw, &T, &V);
        free(raw);
        if (n <= 0) { lb_free(&out); return NULL; }
        char **avas = xrealloc(NULL, n * sizeof(char *));
        for (int i = 0; i < n; i++) {
            LBuf a; lb_init(&a);
            const char *t = T[i];
            if (!strncasecmp(t, "oid.", 4)) t += 4;
            const char *ct = ldap_attr_canon(t);
            for (const char *q = ct; *q; q++) lb_byte(&a, (unsigned char)tolower((unsigned char)*q));
            lb_byte(&a, '=');
            norm_value_into(&a, V[i]);
            lb_byte(&a, 0);
            avas[i] = (char *)a.p;
        }
        if (n > 1) qsort(avas, n, sizeof(char *), cmp_str);
        if (!first) lb_byte(&out, ',');
        for (int i = 0; i < n; i++) { if (i) lb_byte(&out, '+'); lb_put(&out, avas[i], strlen(avas[i])); }
        ldap_strv_free(avas, n);
        ldap_strv_free(T, n); ldap_strv_free(V, n);
        first = 0;
        p += e;
        if (*p) {
            p++;
            while (is_space(*p)) p++;
            if (!*p) { lb_free(&out); return NULL; }   /* trailing comma */
        }
    }
    lb_byte(&out, 0);
    return (char *)out.p;
}

int ndn_depth_below(const char *ndn, const char *nbase) {
    size_t ln = strlen(ndn), lb = strlen(nbase);
    if (!lb) {
        if (!ln) return 0;
        int d = 1;
        for (const char *p = ndn; *p; p++) if (*p == ',') d++;
        return d;
    }
    if (ln == lb) return strcmp(ndn, nbase) ? -1 : 0;
    if (ln < lb + 2 || ndn[ln - lb - 1] != ',' || strcmp(ndn + ln - lb, nbase)) return -1;
    int d = 1;
    for (size_t i = 0; i < ln - lb - 1; i++) if (ndn[i] == ',') d++;
    return d;
}

/* ================================================================ values */
static int is_phone_attr(const char *attr) {
    const char *c = ldap_attr_canon(attr);
    return !strcasecmp(c, "telephoneNumber") || !strcasecmp(c, "mobile") || !strcasecmp(c, "facsimileTelephoneNumber")
        || !strcasecmp(c, "homePhone") || !strcasecmp(c, "pager");
}
int ldap_attr_is_binary_match(const char *attr) {
    return !strcasecmp(attr, "userPassword") || !strcasecmp(attr, "jpegPhoto") || !strcasecmp(attr, "userCertificate");
}

/* normalize for matching: case-insensitive, insignificant spaces collapsed;
 * telephone numbers ignore spaces and hyphens; passwords are octet strings */
static int is_dn_attr(const char *attr) {
    static const char *DNA[] = {"member", "uniqueMember", "owner", "seeAlso", "manager", "secretary", "roleOccupant",
                                "creatorsName", "modifiersName", "entryDN", "aliasedObjectName", "namingContexts", NULL};
    for (int i = 0; DNA[i]; i++) if (!strcasecmp(attr, DNA[i])) return 1;
    return 0;
}

char *ldap_value_norm(const char *attr, const char *s, size_t n, size_t *outlen) {
    LBuf b; lb_init(&b);
    if (is_dn_attr(attr) && !memchr(s, 0, n)) {
        char *tmp = xrealloc(NULL, n + 1);
        memcpy(tmp, s, n); tmp[n] = 0;
        char *nd = dn_normalize(tmp);
        free(tmp);
        if (nd) { if (outlen) *outlen = strlen(nd); return nd; }
    }
    if (ldap_attr_is_binary_match(attr)) lb_put(&b, s, n);
    else if (is_phone_attr(attr)) {
        for (size_t i = 0; i < n; i++) if (!is_space((unsigned char)s[i]) && s[i] != '-') lb_byte(&b, (unsigned char)s[i]);
    } else {
        size_t i = 0;
        while (i < n && is_space((unsigned char)s[i])) i++;
        int pend = 0;
        for (; i < n; i++) {
            unsigned char c = (unsigned char)s[i];
            if (is_space(c)) { pend = 1; continue; }
            if (pend) lb_byte(&b, ' ');
            pend = 0;
            lb_byte(&b, (unsigned char)tolower(c));
        }
    }
    if (outlen) *outlen = b.len;
    lb_byte(&b, 0);
    return (char *)b.p;
}

int ldap_value_eq(const char *attr, const char *a, size_t al, const char *b, size_t bl) {
    size_t x, y;
    char *na = ldap_value_norm(attr, a, al, &x), *nb = ldap_value_norm(attr, b, bl, &y);
    int eq = x == y && !memcmp(na, nb, x);
    free(na); free(nb);
    return eq;
}

/* ================================================================ SHA-1 */
typedef struct { uint32_t h[5]; uint64_t len; unsigned char buf[64]; size_t bl; } Sha1;
#define ROL(x, n) (((x) << (n)) | ((x) >> (32 - (n))))
static void sha1_block(Sha1 *c, const unsigned char *p) {
    uint32_t w[80];
    for (int i = 0; i < 16; i++) w[i] = (uint32_t)p[4 * i] << 24 | (uint32_t)p[4 * i + 1] << 16 | (uint32_t)p[4 * i + 2] << 8 | p[4 * i + 3];
    for (int i = 16; i < 80; i++) w[i] = ROL(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1);
    uint32_t a = c->h[0], b = c->h[1], cc = c->h[2], d = c->h[3], e = c->h[4];
    for (int i = 0; i < 80; i++) {
        uint32_t f, k;
        if (i < 20) { f = (b & cc) | (~b & d); k = 0x5A827999; }
        else if (i < 40) { f = b ^ cc ^ d; k = 0x6ED9EBA1; }
        else if (i < 60) { f = (b & cc) | (b & d) | (cc & d); k = 0x8F1BBCDC; }
        else { f = b ^ cc ^ d; k = 0xCA62C1D6; }
        uint32_t t = ROL(a, 5) + f + e + k + w[i];
        e = d; d = cc; cc = ROL(b, 30); b = a; a = t;
    }
    c->h[0] += a; c->h[1] += b; c->h[2] += cc; c->h[3] += d; c->h[4] += e;
}
void ldap_sha1(const unsigned char *data, size_t len, unsigned char out[20]) {
    Sha1 c = {{0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0}, 0, {0}, 0};
    c.len = (uint64_t)len * 8;
    while (len >= 64) { sha1_block(&c, data); data += 64; len -= 64; }
    unsigned char tail[128] = {0};
    memcpy(tail, data, len);
    tail[len] = 0x80;
    size_t tl = len + 1 + 8 <= 64 ? 64 : 128;
    for (int i = 0; i < 8; i++) tail[tl - 1 - i] = (unsigned char)(c.len >> (8 * i));
    sha1_block(&c, tail);
    if (tl == 128) sha1_block(&c, tail + 64);
    for (int i = 0; i < 5; i++) { out[4 * i] = c.h[i] >> 24; out[4 * i + 1] = c.h[i] >> 16; out[4 * i + 2] = c.h[i] >> 8; out[4 * i + 3] = c.h[i]; }
}

/* ================================================================ base64 */
static const char B64[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
char *ldap_b64(const unsigned char *p, size_t n) {
    char *o = xrealloc(NULL, (n + 2) / 3 * 4 + 1), *q = o;
    for (size_t i = 0; i < n; i += 3) {
        unsigned v = p[i] << 16 | (i + 1 < n ? p[i + 1] << 8 : 0) | (i + 2 < n ? p[i + 2] : 0);
        *q++ = B64[v >> 18 & 63]; *q++ = B64[v >> 12 & 63];
        *q++ = i + 1 < n ? B64[v >> 6 & 63] : '=';
        *q++ = i + 2 < n ? B64[v & 63] : '=';
    }
    *q = 0;
    return o;
}
unsigned char *ldap_unb64(const char *s, size_t *outlen) {
    size_t n = strlen(s);
    unsigned char *o = xrealloc(NULL, n / 4 * 3 + 4);
    size_t k = 0; unsigned v = 0; int bits = 0;
    for (; *s; s++) {
        const char *d = strchr(B64, *s);
        if (*s == '=' ) break;
        if (!d || !*s) { if (is_space((unsigned char)*s)) continue; free(o); return NULL; }
        v = v << 6 | (unsigned)(d - B64);
        bits += 6;
        if (bits >= 8) { bits -= 8; o[k++] = (unsigned char)(v >> bits); }
    }
    o[k] = 0;
    if (outlen) *outlen = k;
    return o;
}
