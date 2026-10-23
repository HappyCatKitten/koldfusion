/*
 * httpc.c - the HTTP client behind CFHTTP and the scheduler.
 *
 * Speaks HTTP/1.1 (or 1.0) over plain sockets or SSL (tls.c), through an
 * HTTP proxy if asked (CONNECT for https://), with Basic authentication,
 * chunked and Content-Length bodies, and up to four redirects - the limit
 * ColdFusion 4.5 documented.
 */
#define _GNU_SOURCE
#include "netio.h"
#include <stdlib.h>
#include <ctype.h>

typedef struct Url { int https; char *host, *path, *userinfo; int port, port_given; } Url;

static int parse_url2(const char *url, Url *u) {
    memset(u, 0, sizeof *u);
    const char *h;
    if (!kf_strnicmp(url, "http://", 7)) { h = url + 7; u->port = 80; }
    else if (!kf_strnicmp(url, "https://", 8)) { h = url + 8; u->port = 443; u->https = 1; }
    else return 0;
    size_t hl = strcspn(h, "/?#");
    char *hp = kstrndup(h, hl);
    const char *rest = h + hl;
    u->path = *rest == '/' ? kstrndup(rest, strcspn(rest, "#")) : kprintf("/%s", kstrndup(rest, strcspn(rest, "#")));
    char *at = strrchr(hp, '@');
    if (at) { *at = 0; u->userinfo = kf_urldecode(hp, strlen(hp)); hp = at + 1; }
    if (*hp == '[') {                                   /* [IPv6]:port */
        char *rb = strchr(hp, ']');
        if (!rb) return 0;
        u->host = kstrndup(hp + 1, rb - hp - 1);
        if (rb[1] == ':' && rb[2]) { u->port = atoi(rb + 2); u->port_given = 1; }
    } else {
        char *colon = strchr(hp, ':');
        if (colon) { *colon = 0; if (colon[1]) { u->port = atoi(colon + 1); u->port_given = 1; } }
        u->host = hp;
    }
    if (!*u->host || u->port <= 0 || u->port > 65535) return 0;
    return 1;
}

static char *host_header(const Url *u) {
    int dflt = u->https ? 443 : 80;
    const char *h = strchr(u->host, ':') ? kprintf("[%s]", u->host) : u->host;
    return u->port == dflt ? kstrdup(h) : kprintf("%s:%d", h, u->port);
}

/* localhost and *.localhost always mean this machine (RFC 6761), whatever the resolver thinks */
static const char *connect_host(const char *h) {
    size_t l = strlen(h);
    if (!kf_stricmp(h, "localhost") || (l > 10 && !kf_stricmp(h + l - 10, ".localhost"))) return "127.0.0.1";
    return h;
}

static char *resolve_location(const Url *base, const char *loc) {
    if (!kf_strnicmp(loc, "http://", 7) || !kf_strnicmp(loc, "https://", 8)) return kstrdup(loc);
    const char *scheme = base->https ? "https" : "http";
    if (loc[0] == '/' && loc[1] == '/') return kprintf("%s:%s", scheme, loc);
    char *origin = kprintf("%s://%s", scheme, host_header(base));
    if (loc[0] == '/') return kprintf("%s%s", origin, loc);
    char *dir = kstrndup(base->path, strcspn(base->path, "?"));
    char *sl = strrchr(dir, '/');
    if (sl) sl[1] = 0;
    return kprintf("%s%s%s", origin, dir, loc);
}

/* read until the header block is complete; returns its length (including the blank line) or -1 */
static long read_head(KfConn *c, char *err, size_t errlen, const char *who) {
    size_t scanned = 0;
    for (;;) {
        char *s = c->rbuf + c->rpos;
        size_t n = c->rlen - c->rpos;
        for (size_t i = scanned; i < n; i++) {
            if (s[i] == '\n' && ((i >= 1 && s[i - 1] == '\n') || (i >= 2 && s[i - 1] == '\r' && s[i - 2] == '\n')))
                return (long)i + 1;
        }
        scanned = n;
        if (n > 256 * 1024) { snprintf(err, errlen, "Connection Failure: %s sent a response header that is too large.", who); return -1; }
        ssize_t r = kc_fill(c);
        if (r > 0) continue;
        if (c->timed_out) snprintf(err, errlen, "Connection Timeout: no response from %s in the time allowed.", who);
        else snprintf(err, errlen, "Connection Failure: %s closed the connection without sending a response.", who);
        return -1;
    }
}

static void add_header(Struct *h, const char *k, const char *v) {
    Val *old = struct_get(h, k);
    if (!old) { struct_set(h, k, v_strdup(v)); return; }
    if (old->t == VT_ARRAY) { array_push(old->u.a, v_strdup(v)); return; }
    Array *a = array_new();
    array_push(a, *old);
    array_push(a, v_strdup(v));
    struct_set(h, k, v_arr(a));
}

static int read_chunked(KfConn *c, Buf *out) {
    for (;;) {
        char *line = kc_read_line(c, 16384);
        if (!line) return -1;
        char *end;
        unsigned long long sz = strtoull(line, &end, 16);
        if (end == line) return -1;
        if (sz == 0) {                      /* trailers, then the blank line */
            for (;;) { char *t = kc_read_line(c, 16384); if (!t) return 0; if (!*t) return 0; }
        }
        if (sz > 1024ULL * 1024 * 1024) return -1;
        if (kc_read_exact(c, (size_t)sz, out)) return -1;
        char *crlf = kc_read_line(c, 16384);
        if (!crlf) return -1;
    }
}

static int read_response(KfConn *c, int head_req, const char *who, HttpClientResult *r, char *err, size_t errlen) {
    for (;;) {
        long hl = read_head(c, err, errlen, who);
        if (hl < 0) return 0;
        char *hdr = kstrndup(c->rbuf + c->rpos, (size_t)hl);
        c->rpos += (size_t)hl;
        char *save = NULL;
        char *first = strtok_r(hdr, "\r\n", &save);
        if (!first || kf_strnicmp(first, "HTTP/", 5)) {
            snprintf(err, errlen, "Connection Failure: %s did not answer with an HTTP response.", who);
            return 0;
        }
        const char *sp = strchr(first, ' ');
        r->status = sp ? atoi(sp + 1) : 0;
        r->status_line = kstrdup(first);
        r->headers = struct_new();
        for (char *line = strtok_r(NULL, "\r\n", &save); line; line = strtok_r(NULL, "\r\n", &save)) {
            char *colon = strchr(line, ':');
            if (!colon) continue;
            *colon = 0;
            add_header(r->headers, kf_trim(line), kf_trim(colon + 1));
        }
        if (r->status >= 100 && r->status < 200) continue;          /* 100 Continue and friends */
        break;
    }
    if (head_req || r->status == 204 || r->status == 304) return 1;
    Val *te = struct_get(r->headers, "Transfer-Encoding");
    Val *cl = struct_get(r->headers, "Content-Length");
    if (te && v_is_simple(*te) && kf_stristr(v_tostr(*te), "chunked")) {
        if (read_chunked(c, &r->body)) {
            snprintf(err, errlen, c->timed_out ? "Connection Timeout: the response from %s did not arrive in the time allowed."
                                               : "Connection Failure: the chunked response from %s was cut short.", who);
            return 0;
        }
    } else if (cl && v_is_simple(*cl)) {
        long long n = atoll(v_tostr(*cl));
        if (n < 0) n = 0;
        if (kc_read_exact(c, (size_t)n, &r->body)) {
            snprintf(err, errlen, c->timed_out ? "Connection Timeout: the response from %s did not arrive in the time allowed."
                                               : "Connection Failure: the response from %s was cut short.", who);
            return 0;
        }
    } else {
        for (;;) {                                          /* until the server closes */
            if (kc_avail(c)) { buf_put(&r->body, c->rbuf + c->rpos, kc_avail(c)); c->rpos = c->rlen; }
            ssize_t n = kc_fill(c);
            if (n == 0) break;
            if (n < 0) {
                if (c->timed_out) {
                    snprintf(err, errlen, "Connection Timeout: the response from %s did not arrive in the time allowed.", who);
                    return 0;
                }
                break;
            }
        }
    }
    return 1;
}

int http_client_ex(const HttpClientOpts *o, HttpClientResult *r, char *err, size_t errlen) {
    double deadline = kf_time_ms() + (o->timeout_s > 0 ? o->timeout_s : 60) * 1000.0;
    const char *url = o->url;
    const char *method = o->method && *o->method ? o->method : "GET";
    const char *body = o->body; size_t bodylen = o->bodylen;
    int verify = o->verify >= 0 ? o->verify : cfg_int("SSL", "VerifyServerCertificates", 1);
    const char *auth_host = NULL;
    memset(r, 0, sizeof *r);
    buf_init(&r->body);
    for (int hop = 0;; hop++) {
        Url u;
        if (!parse_url2(url, &u)) {
            snprintf(err, errlen, "Invalid URL %s: CFHTTP needs a full URL that starts with http:// or https://.", url);
            return 0;
        }
        if (hop == 0 && o->port > 0 && !u.port_given) u.port = o->port;
        if (!auth_host) auth_host = u.host;
        const char *user = o->user, *pass = o->pass;
        if ((!user || !*user) && u.userinfo) {
            char *col = strchr(u.userinfo, ':');
            user = col ? kstrndup(u.userinfo, col - u.userinfo) : u.userinfo;
            pass = col ? col + 1 : "";
        }
        if (kf_stricmp(auth_host, u.host)) user = NULL;           /* never send credentials to another host */
        int use_proxy = o->proxy && *o->proxy;
        const char *chost = connect_host(use_proxy ? o->proxy : u.host);
        int cport = use_proxy ? (o->proxyport > 0 ? o->proxyport : 80) : u.port;
        char *who = kprintf("%s:%d", use_proxy ? o->proxy : u.host, cport);
        KfConn *c = NULL;
        if (!kc_connect(chost, cport, deadline, &c, err, errlen)) return 0;
        if (use_proxy && u.https) {
            char *hh = host_header(&u);
            char *rq = kprintf("CONNECT %s HTTP/1.1\r\nHost: %s\r\nUser-Agent: %s\r\n\r\n", hh, hh,
                               o->useragent && *o->useragent ? o->useragent : "KoldFusion");
            HttpClientResult pr; memset(&pr, 0, sizeof pr); buf_init(&pr.body);
            if (kc_write(c, rq, strlen(rq)) || !read_response(c, 1, who, &pr, err, errlen)) { kc_free(c); return 0; }
            if (pr.status < 200 || pr.status > 299) {
                snprintf(err, errlen, "Connection Failure: the proxy server %s refused to connect to %s (%s).", who, hh, pr.status_line);
                kc_free(c); return 0;
            }
        }
        if (u.https && tls_client_start(c, u.host, verify, deadline, err, errlen)) { kc_free(c); return 0; }
        Buf rq; buf_init(&rq);
        const char *target = use_proxy && !u.https ? url : u.path;
        buf_printf(&rq, "%s %s HTTP/1.%d\r\nHost: %s\r\n", method, target, o->http10 ? 0 : 1, host_header(&u));
        if (!o->headers || !struct_get(o->headers, "User-Agent"))
            buf_printf(&rq, "User-Agent: %s\r\n", o->useragent && *o->useragent ? o->useragent : "KoldFusion");
        buf_puts(&rq, "Connection: close\r\n");
        if (user && *user) {
            char *cred = kprintf("%s:%s", user, pass ? pass : "");
            buf_printf(&rq, "Authorization: Basic %s\r\n", base64_encode((unsigned char *)cred, strlen(cred)));
        }
        if (o->headers)
            for (int i = 0; i < o->headers->n; i++) {
                const char *k = o->headers->e[i].key;
                if (!kf_stricmp(k, "Host") || !kf_stricmp(k, "Connection") || !kf_stricmp(k, "Content-Length")) continue;
                if (!kf_stricmp(k, "Content-Type") && !body) continue;
                buf_printf(&rq, "%s: %s\r\n", k, v_tostr(o->headers->e[i].v));
            }
        if (body) buf_printf(&rq, "Content-Length: %zu\r\n", bodylen);
        buf_puts(&rq, "\r\n");
        if (body) buf_put(&rq, body, bodylen);
        c->wdeadline = deadline;
        if (kc_write(c, rq.s, rq.len)) {
            snprintf(err, errlen, c->timed_out ? "Connection Timeout: %s did not accept the request in time."
                                               : "Connection Failure: the connection to %s was lost while sending the request.", who);
            kc_free(c); return 0;
        }
        r->body.len = 0;
        int ok = read_response(c, !kf_stricmp(method, "HEAD"), who, r, err, errlen);
        kc_free(c);
        if (!ok) return 0;
        r->final_url = kstrdup(url);
        Val *loc = struct_get(r->headers, "Location");
        int st = r->status;
        if (o->follow_redirects && loc && v_is_simple(*loc) && *v_tostr(*loc) && hop < 4 &&
            (st == 301 || st == 302 || st == 303 || st == 307 || st == 308)) {
            url = resolve_location(&u, v_tostr(*loc));
            if (st == 303 || ((st == 301 || st == 302) && kf_stricmp(method, "GET") && kf_stricmp(method, "HEAD"))) {
                method = "GET"; body = NULL; bodylen = 0;            /* what browsers do */
            }
            continue;
        }
        return 1;
    }
}

/* the original entry point, still used by the scheduler */
int http_client(const char *method, const char *url, Struct *hdrs, const char *body, size_t bodylen,
                int timeout_s, const char *proxy, int proxyport, const char *user, const char *pass,
                Buf *resp_body, int *status, char **status_line, Struct **resp_headers, char *err, size_t errlen) {
    HttpClientOpts o = {0};
    o.method = method; o.url = url; o.headers = hdrs; o.body = body; o.bodylen = bodylen;
    o.timeout_s = timeout_s; o.proxy = proxy; o.proxyport = proxyport; o.user = user; o.pass = pass;
    o.follow_redirects = 1; o.verify = -1;
    HttpClientResult r;
    if (!http_client_ex(&o, &r, err, errlen)) return 0;
    if (r.body.len) buf_put(resp_body, r.body.s, r.body.len);
    *status = r.status;
    *status_line = r.status_line;
    *resp_headers = r.headers;
    return 1;
}
