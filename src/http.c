/*
 * http.c - the built-in web server and the HTTP client used by CFHTTP.
 *
 * ColdFusion 4.5 sat behind IIS/Netscape/Apache via a connector stub. We
 * fold the web server in: static files are served directly, .cfm/.cfml/.dbm
 * go to the engine. HTTP/1.1 with persistent connections (and HTTP/1.0
 * keep-alive, as Netscape 4 and IE 4 spoke it), plus an SSL listener when
 * OpenSSL can be loaded at run time (tls.c). The CFHTTP client is in httpc.c.
 *
 * One thread per connection. Every read and write has a deadline (netio.c),
 * so idle keep-alive connections and slow clients cannot pin threads forever.
 */
#define _GNU_SOURCE
#include "engine.h"
#include "netio.h"
#include <stdlib.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <netdb.h>
#include <pthread.h>
#include <semaphore.h>
#include <signal.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <time.h>
#include <unistd.h>
#include <dirent.h>
#include <math.h>
#include <poll.h>

#define SERVER_SOFTWARE "KoldFusion/4.5.1 (Unix)"
#define MAX_BODY (64 * 1024 * 1024)

static sem_t req_sem;
static pthread_mutex_t stats_mu = PTHREAD_MUTEX_INITIALIZER;
static int listen_fd = -1, ssl_listen_fd = -1;
static int open_conns;                       /* connections being served (stats_mu) */
Struct *g_server_scope;
Arena *g_server_arena;

void templates_release(RState *rs);
void add_set_cookie(RState *rs, const char *name, const char *value, const char *expires, const char *path,
                    const char *domain, int secure);

/* ================================================================ tracking */
typedef struct Active { int used; double started; pthread_t th; char path[256]; int flagged; } Active;
static Active active[512];
static pthread_mutex_t active_mu = PTHREAD_MUTEX_INITIALIZER;

static int active_add(const char *path) {
    pthread_mutex_lock(&active_mu);
    for (int i = 0; i < 512; i++) {
        if (!active[i].used) {
            active[i].used = 1; active[i].started = kf_time_ms(); active[i].th = pthread_self(); active[i].flagged = 0;
            snprintf(active[i].path, sizeof active[i].path, "%s", path);
            pthread_mutex_unlock(&active_mu);
            return i;
        }
    }
    pthread_mutex_unlock(&active_mu);
    return -1;
}
static void active_remove(int i) {
    if (i < 0) return;
    pthread_mutex_lock(&active_mu);
    active[i].used = 0;
    pthread_mutex_unlock(&active_mu);
}

Query *active_requests(void) {
    const char *cols[] = {"Template", "Seconds"};
    Query *q = query_new(2, cols);
    pthread_mutex_lock(&active_mu);
    double now = kf_time_ms();
    for (int i = 0; i < 512; i++) {
        if (!active[i].used) continue;
        int r = query_add_row(q);
        query_set(q, 0, r, v_strdup(active[i].path));
        query_set(q, 1, r, v_num(floor((now - active[i].started) / 1000)));
    }
    pthread_mutex_unlock(&active_mu);
    return q;
}

/* the "Restart at N unresponsive requests" watchdog */
static void *watchdog(void *arg) {
    (void)arg;
    for (;;) {
        sleep(5);
        Arena *a = arena_new(); g_arena = a;
        int timeout_on = cfg_int(REG_SERVER, "TimeoutRequests", 1);
        int timeout = cfg_int(REG_SERVER, "RequestTimeout", 30);
        int restart_on = cfg_int(REG_SERVER, "RestartUnresponsive", 1);
        int restart_at = cfg_int(REG_SERVER, "RestartAt", 10);
        g_arena = NULL; arena_free(a);
        if (!timeout_on) continue;
        int stuck = 0;
        double now = kf_time_ms();
        pthread_mutex_lock(&active_mu);
        for (int i = 0; i < 512; i++) {
            if (active[i].used && now - active[i].started > timeout * 2000.0) {
                stuck++;
                if (!active[i].flagged) {
                    active[i].flagged = 1;
                    G.unresponsive++;
                    kf_log("server.log", "Warning", "Request %s has not responded for more than %d seconds.",
                           active[i].path, timeout * 2);
                }
            }
        }
        pthread_mutex_unlock(&active_mu);
        if (restart_on && stuck >= restart_at) {
            kf_log("server.log", "Error", "%d unresponsive requests: restarting the KoldFusion Application Server.", stuck);
            G.restart_requested = 1;
            if (listen_fd >= 0) shutdown(listen_fd, SHUT_RDWR);
        }
    }
    return NULL;
}

/* ================================================================ helpers */
char *http_date(time_t t) {
    struct tm tm; gmtime_r(&t, &tm);
    char buf[64];
    strftime(buf, sizeof buf, "%a, %d %b %Y %H:%M:%S GMT", &tm);
    return kstrdup(buf);
}

const char *mime_type_for(const char *path) {
    static const struct { const char *ext, *type; } M[] = {
        {".htm", "text/html"}, {".html", "text/html"}, {".txt", "text/plain"}, {".css", "text/css"},
        {".js", "application/x-javascript"}, {".gif", "image/gif"}, {".jpg", "image/jpeg"}, {".jpeg", "image/jpeg"},
        {".png", "image/png"}, {".ico", "image/x-icon"}, {".class", "application/java-vm"}, {".jar", "application/java-archive"},
        {".xml", "text/xml"}, {".wddx", "text/xml"}, {".pdf", "application/pdf"}, {".zip", "application/zip"},
        {".mid", "audio/midi"}, {".wav", "audio/wav"}, {".swf", "application/x-shockwave-flash"},
        {".log", "text/plain"}, {".csv", "text/plain"}, {".cfm.txt", "text/plain"}, {".svg", "image/svg+xml"},
        {NULL, NULL}};
    const char *dot = strrchr(path, '.');
    if (!dot) return "application/octet-stream";
    for (int i = 0; M[i].ext; i++) if (!kf_stricmp(dot, M[i].ext)) return M[i].type;
    return "application/octet-stream";
}

static const char *status_text(int code) {
    switch (code) {
    case 200: return "OK"; case 201: return "Created"; case 204: return "No Content";
    case 301: return "Moved Permanently"; case 302: return "Object Moved"; case 304: return "Not Modified";
    case 100: return "Continue"; case 206: return "Partial Content"; case 303: return "See Other";
    case 307: return "Temporary Redirect";
    case 400: return "Bad Request"; case 401: return "Unauthorized"; case 403: return "Forbidden";
    case 404: return "Object Not Found"; case 405: return "Method Not Allowed"; case 408: return "Request Timeout";
    case 411: return "Length Required"; case 413: return "Request Entity Too Large"; case 417: return "Expectation Failed";
    case 500: return "Internal Server Error"; case 501: return "Not Implemented"; case 503: return "Service Unavailable";
    case 505: return "HTTP Version Not Supported";
    }
    return "Unknown";
}

/* Web server settings (Administrator > Web Server & SSL), read once per connection */
typedef struct WebCfg { int keepalive, ka_timeout, ka_max, header_timeout, max_conns; } WebCfg;
static void web_cfg(WebCfg *w) {
    w->keepalive = cfg_int(REG_SERVER, "KeepAlive", 1);
    w->ka_timeout = cfg_int(REG_SERVER, "KeepAliveTimeout", 15);
    w->ka_max = cfg_int(REG_SERVER, "KeepAliveMaxRequests", 100);
    w->header_timeout = cfg_int(REG_SERVER, "HeaderTimeout", 20);
    w->max_conns = cfg_int(REG_SERVER, "MaxConnections", 400);
    if (w->ka_timeout < 1) w->ka_timeout = 1;
    if (w->ka_max < 1) w->ka_max = 1;
    if (w->header_timeout < 1) w->header_timeout = 1;
    if (w->max_conns < 1) w->max_conns = 1;
}
static __thread WebCfg t_web;                 /* the current connection's settings */

void http_install_defaults(void) {
    static const char *D[][2] = {{"KeepAlive", "1"}, {"KeepAliveTimeout", "15"}, {"KeepAliveMaxRequests", "100"},
                                 {"HeaderTimeout", "20"}, {"MaxConnections", "400"}, {NULL, NULL}};
    for (int i = 0; D[i][0]; i++)
        if (!reg_exists(cfg_key(REG_SERVER), D[i][0])) cfg_set(REG_SERVER, D[i][0], D[i][1]);
}

/* Every response goes out through here: the status line in the client's HTTP
 * version, Date, Server, a Content-Length that is always right (no body is
 * sent for HEAD, 204 and 304), and the Connection/Keep-Alive headers. */
static void send_response(KfConn *c, HttpReq *req, int code, const char *reason, const char *extra,
                          const char *ctype, const char *body, size_t blen) {
    Buf h; buf_init(&h);
    int v11 = req && req->http11;
    buf_printf(&h, "HTTP/1.%d %d %s\r\nServer: %s\r\nDate: %s\r\n", v11, code, reason && *reason ? reason : status_text(code),
               SERVER_SOFTWARE, http_date(time(NULL)));
    if (extra) buf_puts(&h, extra);
    int nobody = code == 204 || code == 304 || (code >= 100 && code < 200);
    if (!nobody) {
        if (ctype) buf_printf(&h, "Content-Type: %s\r\n", ctype);
        buf_printf(&h, "Content-Length: %zu\r\n", blen);
    }
    if (req && req->keep_alive) {
        if (!v11) buf_puts(&h, "Connection: keep-alive\r\n");
        buf_printf(&h, "Keep-Alive: timeout=%d, max=%d\r\n", t_web.ka_timeout, t_web.ka_max - req->nreq);
    } else buf_puts(&h, "Connection: close\r\n");
    buf_puts(&h, "\r\n");
    int with_body = !nobody && !(req && req->head) && body && blen;
    kc_set_write_budget(c, h.len + (with_body ? blen : 0));
    int rc;
    if (with_body && blen <= 64 * 1024) { buf_put(&h, body, blen); rc = kc_write(c, h.s, h.len); }
    else {
        rc = kc_write(c, h.s, h.len);
        if (!rc && with_body) rc = kc_write(c, body, blen);
    }
    if (req) {
        req->resp_status = code;
        req->resp_bytes = with_body ? blen : 0;
        if (rc) req->keep_alive = 0;
    }
}

static void simple_response(KfConn *c, HttpReq *req, int code, const char *title, const char *body) {
    char *html = kprintf("<HTML><HEAD><TITLE>%s</TITLE></HEAD>\n<BODY BGCOLOR=\"#FFFFFF\">\n<H2>HTTP %d - %s</H2>\n"
                         "<FONT FACE=\"Arial, Helvetica\" SIZE=\"2\">%s</FONT>\n<HR NOSHADE SIZE=1>\n"
                         "<FONT FACE=\"Arial, Helvetica\" SIZE=\"1\"><I>%s</I></FONT>\n</BODY></HTML>\n",
                         title, code, title, body, SERVER_SOFTWARE);
    send_response(c, req, code, NULL, NULL, "text/html", html, strlen(html));
}

static void redirect_response(KfConn *c, HttpReq *req, const char *loc) {
    const char *esc = kf_html_escape(loc);
    char *html = kprintf("<HTML><HEAD><TITLE>Object Moved</TITLE></HEAD><BODY>This object may be found "
                         "<A HREF=\"%s\">here</A>.</BODY></HTML>\n", esc);
    send_response(c, req, 302, NULL, kprintf("Location: %s\r\n", loc), "text/html", html, strlen(html));
}

/* ================================================================ parsing */
static void parse_urlencoded(Struct *into, const char *s, size_t n, Buf *fieldnames) {
    size_t i = 0;
    while (i < n) {
        size_t j = i;
        while (j < n && s[j] != '&') j++;
        size_t eq = i;
        while (eq < j && s[eq] != '=') eq++;
        if (eq > i) {
            char *k = kf_urldecode(s + i, eq - i);
            char *v = eq < j ? kf_urldecode(s + eq + 1, j - eq - 1) : kstrdup("");
            Val *old = struct_get(into, k);
            if (old && v_is_simple(*old)) struct_set(into, k, v_str(kprintf("%s,%s", v_tostr(*old), v)));
            else {
                struct_set(into, k, v_str(v));
                if (fieldnames) { if (fieldnames->len) buf_putc(fieldnames, ','); buf_puts(fieldnames, kf_upper(k)); }
            }
        }
        i = j + 1;
    }
}

static int list_contains_nocase(const char *list, const char *item) {
    Array *a = list_to_array_k(list, ",");
    for (int i = 0; i < a->n; i++) if (!kf_stricmp(v_tostr(a->v[i]), item)) return 1;
    return 0;
}

static const char *memmem_s(const char *h, size_t hl, const char *n, size_t nl) {
    return memmem(h, hl, n, nl);
}

static void parse_multipart(RState *rs, const char *ctype, const char *body, size_t len, Buf *fieldnames) {
    const char *b = kf_stristr(ctype, "boundary=");
    if (!b) return;
    b += 9;
    char *boundary = kprintf("--%s", *b == '"' ? kstrndup(b + 1, strcspn(b + 1, "\"")) : kstrndup(b, strcspn(b, "; ")));
    size_t bl = strlen(boundary);
    const char *p = memmem_s(body, len, boundary, bl);
    char *tmpdir = kf_path_join(G.root, "temp");
    kf_mkdirs(tmpdir);
    while (p) {
        p += bl;
        if (p + 2 <= body + len && p[0] == '-' && p[1] == '-') break;
        if (p + 2 <= body + len && p[0] == '\r') p += 2;
        const char *hend = memmem_s(p, body + len - p, "\r\n\r\n", 4);
        if (!hend) break;
        char *hdrs = kstrndup(p, hend - p);
        const char *data = hend + 4;
        const char *next = memmem_s(data, body + len - data, boundary, bl);
        if (!next) break;
        size_t dlen = next - data;
        if (dlen >= 2 && data[dlen - 2] == '\r') dlen -= 2;
        const char *nm = kf_stristr(hdrs, "name=\"");
        if (nm) {
            nm += 6;
            char *name = kstrndup(nm, strcspn(nm, "\""));
            const char *fn = kf_stristr(hdrs, "filename=\"");
            if (fn) {
                fn += 10;
                char *filename = kstrndup(fn, strcspn(fn, "\""));
                const char *ct = kf_stristr(hdrs, "content-type:");
                char *ctype2 = ct ? kf_trim(kstrndup(ct + 13, strcspn(ct + 13, "\r\n"))) : "application/octet-stream";
                char *tmp = kprintf("%s/kfupload%ld_%d.tmp", tmpdir, (long)time(NULL), rand());
                kf_write_file(tmp, data, dlen, 0);
                if (!rs->formfiles) rs->formfiles = struct_new();
                Struct *info = struct_new();
                struct_set(info, "tmpfile", v_str(tmp));
                struct_set(info, "clientfile", v_str(filename));
                struct_set(info, "contenttype", v_str(ctype2));
                struct_set(info, "size", v_num((double)dlen));
                struct_set(rs->formfiles, name, v_struct(info));
                struct_set(rs->form, name, v_str(tmp));
            } else {
                Val *old = struct_get(rs->form, name);
                char *v = kstrndup(data, dlen);
                if (old) struct_set(rs->form, name, v_str(kprintf("%s,%s", v_tostr(*old), v)));
                else struct_set(rs->form, name, v_str(v));
            }
            if (!list_contains_nocase(buf_cstr(fieldnames), name)) {
                if (fieldnames->len) buf_putc(fieldnames, ',');
                buf_puts(fieldnames, kf_upper(name));
            }
        }
        p = next;
    }
}

static void parse_cookies(Struct *into, const char *hdr) {
    char *s = kstrdup(hdr);
    for (char *tok = strtok(s, ";"); tok; tok = strtok(NULL, ";")) {
        char *t = kf_trim(tok);
        char *eq = strchr(t, '=');
        if (!eq) continue;
        *eq = 0;
        struct_set(into, kf_trim(t), v_str(kf_urldecode(eq + 1, strlen(eq + 1))));
    }
}

/* ================================================================ CFFORM server-side validation */
/* ColdFusion validates hidden fields named field_required, field_integer,
 * field_float, field_range, field_date, field_eurodate, field_time before the
 * action page runs. */
static int form_validation(RState *rs, Buf *errs) {
    Struct *f = rs->form;
    int bad = 0;
    for (int i = 0; i < f->n; i++) {
        const char *k = f->e[i].key;
        const char *us = strrchr(k, '_');
        if (!us || us == k) continue;
        const char *rule = us + 1;
        char *field = kstrndup(k, us - k);
        Val *fv = struct_get(f, field);
        const char *val = fv ? v_tostr(*fv) : "";
        const char *msg = v_tostr(f->e[i].v);
        int ok = 1;
        double d;
        if (!kf_stricmp(rule, "required")) ok = fv && *kf_trim(val);
        else if (!*val) continue;
        else if (!kf_stricmp(rule, "integer")) ok = v_isnumeric_str(val, &d) && d == floor(d);
        else if (!kf_stricmp(rule, "float")) ok = v_isnumeric_str(val, NULL);
        else if (!kf_stricmp(rule, "date") || !kf_stricmp(rule, "eurodate") || !kf_stricmp(rule, "time")) ok = date_parse(val, &d);
        else if (!kf_stricmp(rule, "range")) {
            double mn = -1e300, mx = 1e300;
            const char *p = kf_stristr(msg, "MIN="); if (p) mn = atof(p + 4);
            p = kf_stristr(msg, "MAX="); if (p) mx = atof(p + 4);
            ok = v_isnumeric_str(val, &d) && d >= mn && d <= mx;
            if (!ok) msg = kprintf("The value entered for %s must be between %s and %s.", field, fmt_number(mn), fmt_number(mx));
        } else continue;
        if (!ok) {
            bad++;
            if (!*msg || !kf_stricmp(rule, "range") == 0) {}
            if (!*msg) msg = kprintf("The value entered for the %s field is not valid (%s).", kf_upper(field), rule);
            buf_printf(errs, "<LI>%s\n", kf_html_escape(msg));
        }
    }
    return bad;
}

/* ================================================================ zoom */
/* Server Settings > Page zoom: 1999 pages were designed for 800x600 at 96 dpi; on
 * today's screens they are tiny, so every HTML page is served with a CSS zoom
 * (175% by default). Framesets are left alone; their frames are zoomed. */
/* scale the pixel sizes in <FRAMESET COLS="175,*"> so zoomed frames still fit */
static const char *zoom_frameset(const char *body, size_t len, size_t *outlen, int zoom) {
    Buf b; buf_init(&b);
    size_t i = 0;
    while (i < len) {
        if (body[i] == '<' && i + 9 < len && !kf_strnicmp(body + i, "<frameset", 9)) {
            const char *gt = memchr(body + i, '>', len - i);
            size_t end = gt ? (size_t)(gt - body) + 1 : len;
            for (size_t k = i; k < end; ) {
                if ((!kf_strnicmp(body + k, "cols", 4) || !kf_strnicmp(body + k, "rows", 4)) && k + 4 < end) {
                    size_t q = k + 4;
                    while (q < end && (body[q] == ' ' || body[q] == '=')) q++;
                    char quote = (body[q] == '"' || body[q] == '\'') ? body[q] : 0;
                    buf_put(&b, body + k, q - k + (quote ? 1 : 0));
                    q += quote ? 1 : 0;
                    while (q < end && body[q] != quote && body[q] != '>' && !(quote == 0 && isspace((unsigned char)body[q]))) {
                        if (isdigit((unsigned char)body[q])) {
                            size_t d = q; long v = 0;
                            while (d < end && isdigit((unsigned char)body[d])) v = v * 10 + (body[d++] - '0');
                            if (d < end && (body[d] == '%' || body[d] == '*')) buf_put(&b, body + q, d - q);   /* relative: keep */
                            else buf_printf(&b, "%ld", (v * zoom + 50) / 100);
                            q = d;
                        } else buf_putc(&b, body[q++]);
                    }
                    k = q;
                } else buf_putc(&b, body[k++]);
            }
            i = end;
        } else buf_putc(&b, body[i++]);
    }
    *outlen = b.len;
    return buf_cstr(&b);
}

/* Server Settings > Page zoom: 1999 pages were designed for 800x600 at 96 dpi; on
 * today's screens they are tiny, so every HTML page is served with a CSS zoom
 * (175% by default). Pop-up windows opened by the page are scaled to match, and
 * framesets get their pixel widths scaled while their frames do the zooming. */
static int display_zoom(void) {
    int zoom = cfg_int(REG_SERVER, "DisplayZoom", 175);
    return zoom <= 0 ? 100 : zoom;
}

/* The zoom is injected into static HTML, so it is part of the cache validator: Last-Modified of an HTML file
 * is never older than the moment the zoom setting took its current value (kept in the registry so it
 * survives restarts), and the ETag carries the zoom. */
static time_t zoom_since(int zoom) {
    static pthread_mutex_t mu = PTHREAD_MUTEX_INITIALIZER;
    static int cached_zoom = -1;
    static time_t cached_since;
    pthread_mutex_lock(&mu);
    if (zoom != cached_zoom) {
        int z = 0; long t = 0;
        const char *v = cfg(REG_SERVER, "DisplayZoomSince", "");
        if (sscanf(v, "%d:%ld", &z, &t) == 2 && z == zoom) cached_since = (time_t)t;
        else {
            cached_since = time(NULL);
            cfg_set(REG_SERVER, "DisplayZoomSince", kprintf("%d:%ld", zoom, (long)cached_since));
        }
        cached_zoom = zoom;
    }
    time_t r = cached_since;
    pthread_mutex_unlock(&mu);
    return r;
}

static const char *apply_zoom(const char *body, size_t len, size_t *outlen) {
    *outlen = len;
    int zoom = display_zoom();
    if (zoom == 100) return body;
    const char *head = NULL;
    for (size_t i = 0; i + 9 < len && i < 4096; i++) {
        if (body[i] != '<') continue;
        if (!kf_strnicmp(body + i, "<frameset", 9)) return zoom_frameset(body, len, outlen, zoom);
        if (!head && !kf_strnicmp(body + i, "<head", 5)) {
            const char *gt = memchr(body + i, '>', len - i);
            if (gt) head = gt + 1;
        }
    }
    char *inject = kprintf(
        "<style type=\"text/css\">html{zoom:%d%%}</style>"
        "<script type=\"text/javascript\">(function(z){var o=window.open,r=window.resizeTo;"
        "window.open=function(u,n,f){if(f)f=String(f).replace(/(width|height)=(\\d+)/gi,function(m,k,v){return k+'='+Math.round(v*z)});"
        "return o.call(window,u,n,f)};if(r)window.resizeTo=function(w,h){return r.call(window,Math.round(w*z),Math.round(h*z))};"
        /* a BODY BACKGROUND tile is painted on the canvas, which the zoom doesn't reach: give it an explicit size */
        "document.addEventListener('DOMContentLoaded',function(){var b=document.body,m=b&&getComputedStyle(b).backgroundImage.match(/^url\\(\"?(.*?)\"?\\)$/);"
        "if(!m||b.style.backgroundSize)return;var i=new Image();i.onload=function(){b.style.backgroundSize=i.width+'px '+i.height+'px'};i.src=m[1]})})(%g);</script>",
        zoom, zoom / 100.0);
    size_t at = head ? (size_t)(head - body) : 0;
    Buf b; buf_init(&b);
    buf_put(&b, body, at);
    buf_puts(&b, inject);
    buf_put(&b, body + at, len - at);
    *outlen = b.len;
    return buf_cstr(&b);
}

/* ================================================================ response */
static char *suppress_whitespace(const char *s, size_t n, size_t *outlen) {
    Buf o; buf_init(&o);
    int inpre = 0;
    for (size_t i = 0; i < n; ) {
        if (s[i] == '<') {
            if (!kf_strnicmp(s + i, "<pre", 4) || !kf_strnicmp(s + i, "<textarea", 9)) inpre = 1;
            else if (!kf_strnicmp(s + i, "</pre", 5) || !kf_strnicmp(s + i, "</textarea", 10)) inpre = 0;
        }
        if (!inpre && isspace((unsigned char)s[i])) {
            size_t j = i; int nl = 0;
            while (j < n && isspace((unsigned char)s[j])) { if (s[j] == '\n') nl = 1; j++; }
            buf_putc(&o, nl ? '\n' : ' ');
            i = j;
            continue;
        }
        buf_putc(&o, s[i++]);
    }
    *outlen = o.len;
    return buf_cstr(&o);
}

static void send_engine_response(KfConn *conn, RState *rs) {
    HttpReq *req = rs->http;
    Buf h; buf_init(&h);
    int status = rs->status ? rs->status : 200;
    const char *st = rs->status_text && *rs->status_text ? rs->status_text : status_text(status);
    if (rs->location) buf_printf(&h, "Location: %s\r\n", rs->location);
    if (rs->setcookies)
        for (int i = 0; i < rs->setcookies->n; i++) buf_printf(&h, "Set-Cookie: %s\r\n", v_tostr(rs->setcookies->v[i]));
    if (rs->headers)
        for (int i = 0; i < rs->headers->n; i++) {
            const char *k = rs->headers->e[i].key;
            /* the server owns the message framing: a CFHEADER must not corrupt a kept-alive connection */
            if (!kf_stricmp(k, "Content-Length") || !kf_stricmp(k, "Connection") || !kf_stricmp(k, "Transfer-Encoding") ||
                !kf_stricmp(k, "Keep-Alive"))
                continue;
            buf_printf(&h, "%s: %s\r\n", k, v_tostr(rs->headers->e[i].v));
        }
    if (status >= 100 && status < 200) status = 200, st = "OK";          /* a final response is required */

    if (rs->content_file) {
        size_t len;
        char *data = kf_read_file(rs->content_file, &len);
        if (!data) { data = strdup(""); len = 0; }
        send_response(conn, req, status, st, buf_cstr(&h), rs->content_type ? rs->content_type : mime_type_for(rs->content_file),
                      data, len);
        free(data);
        if (rs->content_delete) unlink(rs->content_file);
        return;
    }
    const char *body = buf_cstr(&rs->page);
    size_t blen = rs->page.len;
    if (rs->htmlhead.len) {
        const char *hp = kf_stristr(body, "</head>");
        Buf nb; buf_init(&nb);
        if (hp) { buf_put(&nb, body, hp - body); buf_put(&nb, rs->htmlhead.s, rs->htmlhead.len); buf_puts(&nb, hp); }
        else { buf_put(&nb, rs->htmlhead.s, rs->htmlhead.len); buf_put(&nb, body, blen); }
        body = buf_cstr(&nb); blen = nb.len;
    }
    const char *ctype = rs->content_type ? rs->content_type : "text/html";
    if (rs->suppress_ws && !kf_strnicmp(ctype, "text/html", 9)) body = suppress_whitespace(body, blen, &blen);
    if (!kf_strnicmp(ctype, "text/html", 9)) body = apply_zoom(body, blen, &blen);
    send_response(conn, req, status, st, buf_cstr(&h), ctype, body, blen);
}

/* ================================================================ dispatch */
static int is_cfml(const char *path) {
    const char *dot = strrchr(path, '.');
    return dot && (!kf_stricmp(dot, ".cfm") || !kf_stricmp(dot, ".cfml") || !kf_stricmp(dot, ".dbm"));
}

static char *find_index(const char *dir) {
    static const char *IDX[] = {"index.cfm", "default.cfm", "index.htm", "index.html", "default.htm", "default.html", NULL};
    for (int i = 0; IDX[i]; i++) {
        char *p = kf_path_join(dir, IDX[i]);
        if (access(p, R_OK) == 0) return p;
    }
    return NULL;
}

static void directory_listing(KfConn *c, HttpReq *req, const char *urlpath, const char *dir) {
    DIR *d = opendir(dir);
    Buf b; buf_init(&b);
    buf_printf(&b, "<HTML><HEAD><TITLE>%s - /</TITLE></HEAD><BODY BGCOLOR=\"#FFFFFF\"><H1>%s - %s</H1><HR><PRE>",
               "localhost", "localhost", kf_html_escape(urlpath));
    buf_puts(&b, "<A HREF=\"../\">[To Parent Directory]</A><BR><BR>");
    struct dirent *de;
    while (d && (de = readdir(d))) {
        if (de->d_name[0] == '.') continue;
        char *p = kf_path_join(dir, de->d_name);
        struct stat st;
        if (stat(p, &st)) continue;
        struct tm tm; localtime_r(&st.st_mtime, &tm);
        char ts[64]; strftime(ts, sizeof ts, "%m/%d/%y %I:%M %p", &tm);
        if (S_ISDIR(st.st_mode)) buf_printf(&b, "%s        &lt;dir&gt; <A HREF=\"%s/\">%s</A><BR>", ts, de->d_name, de->d_name);
        else buf_printf(&b, "%s %12ld <A HREF=\"%s\">%s</A><BR>", ts, (long)st.st_size, de->d_name, de->d_name);
    }
    if (d) closedir(d);
    buf_puts(&b, "</PRE><HR></BODY></HTML>");
    const char *html = apply_zoom(b.s, b.len, &b.len);
    send_response(c, req, 200, NULL, NULL, "text/html", html, b.len);
}

/* HTTP dates come in three formats (RFC 1123, RFC 850, asctime); IE 4 adds "; length=NNN" */
static int parse_http_date(const char *s, time_t *out) {
    static const char *F[] = {"%a, %d %b %Y %H:%M:%S", "%A, %d-%b-%y %H:%M:%S", "%a %b %d %H:%M:%S %Y", NULL};
    while (*s == ' ') s++;
    for (int i = 0; F[i]; i++) {
        struct tm tm; memset(&tm, 0, sizeof tm);
        if (strptime(s, F[i], &tm)) { *out = timegm(&tm); return 1; }
    }
    return 0;
}

static int etag_matches(const char *list, const char *etag) {
    if (!strcmp(kf_trim(list), "*")) return 1;
    const char *want = etag[0] == 'W' ? etag + 2 : etag;
    char *copy = kstrdup(list), *save = NULL;
    for (char *t = strtok_r(copy, ",", &save); t; t = strtok_r(NULL, ",", &save)) {
        char *e = kf_trim(t);
        if (e[0] == 'W' && e[1] == '/') e += 2;               /* weak comparison, as If-None-Match requires */
        if (!strcmp(e, want)) return 1;
    }
    return 0;
}

static void serve_static(KfConn *c, HttpReq *req, const char *path) {
    struct stat st;
    if (stat(path, &st)) { simple_response(c, req, 404, "Object Not Found", "The requested file was not found."); return; }
    const char *mime = mime_type_for(path);
    int html = !strcmp(mime, "text/html");
    int zoom = html ? display_zoom() : 0;
    time_t lm_t = st.st_mtime;
    if (html && zoom != 100) { time_t zs = zoom_since(zoom); if (zs > lm_t) lm_t = zs; }
    char *etag = kprintf("\"%lx-%lx-%x\"", (long)st.st_mtime, (long)st.st_size, zoom);
    char *validators = kprintf("Last-Modified: %s\r\nETag: %s\r\n", http_date(lm_t), etag);
    Val *inm = struct_get(req->headers, "if-none-match");
    Val *ims = struct_get(req->headers, "if-modified-since");
    int not_modified = 0;
    time_t t;
    if (inm) not_modified = etag_matches(v_tostr(*inm), etag);
    else if (ims && parse_http_date(v_tostr(*ims), &t) && lm_t <= t) not_modified = 1;
    if (not_modified && (!strcmp(req->method, "GET") || req->head)) {
        send_response(c, req, 304, NULL, validators, NULL, NULL, 0);
        return;
    }
    if (req->head && !html) {                                  /* the length is all a HEAD needs */
        send_response(c, req, 200, NULL, validators, mime, NULL, (size_t)st.st_size);
        return;
    }
    size_t len;
    char *raw = kf_read_file(path, &len);
    if (!raw) { simple_response(c, req, 403, "Forbidden", "You do not have permission to read this file."); return; }
    const char *data = raw;
    if (html) data = apply_zoom(raw, len, &len);
    send_response(c, req, 200, NULL, validators, mime, data, len);
    free(raw);
}

static void setup_cgi(RState *rs, HttpReq *req, const char *script_name, const char *filepath) {
    Struct *c = rs->cgi;
    Val *v;
#define HDR(h) ((v = struct_get(req->headers, h)) ? v_tostr(*v) : "")
    struct_set(c, "SERVER_SOFTWARE", v_str(SERVER_SOFTWARE));
    struct_set(c, "SERVER_NAME", v_strdup(req->server_name));
    struct_set(c, "GATEWAY_INTERFACE", v_str("CGI/1.1"));
    struct_set(c, "SERVER_PROTOCOL", v_strdup(req->version));
    struct_set(c, "SERVER_PORT", v_str(kprintf("%d", req->server_port)));
    struct_set(c, "REQUEST_METHOD", v_strdup(req->method));
    struct_set(c, "PATH_INFO", v_strdup(script_name));
    struct_set(c, "PATH_TRANSLATED", v_strdup(filepath));
    struct_set(c, "SCRIPT_NAME", v_strdup(script_name));
    struct_set(c, "QUERY_STRING", v_strdup(req->query ? req->query : ""));
    struct_set(c, "REMOTE_HOST", v_strdup(req->remote_addr));
    struct_set(c, "REMOTE_ADDR", v_strdup(req->remote_addr));
    struct_set(c, "AUTH_TYPE", v_str(""));
    struct_set(c, "REMOTE_USER", v_str(""));
    struct_set(c, "AUTH_USER", v_str(""));
    struct_set(c, "AUTH_PASSWORD", v_str(""));
    struct_set(c, "CONTENT_TYPE", v_strdup(HDR("content-type")));
    struct_set(c, "CONTENT_LENGTH", v_str(kprintf("%zu", req->bodylen)));
    struct_set(c, "HTTP_ACCEPT", v_strdup(HDR("accept")));
    struct_set(c, "HTTP_USER_AGENT", v_strdup(HDR("user-agent")));
    struct_set(c, "HTTP_REFERER", v_strdup(HDR("referer")));
    struct_set(c, "HTTP_COOKIE", v_strdup(HDR("cookie")));
    struct_set(c, "HTTP_HOST", v_strdup(HDR("host")));
    struct_set(c, "HTTP_ACCEPT_LANGUAGE", v_strdup(HDR("accept-language")));
    struct_set(c, "HTTP_ACCEPT_ENCODING", v_strdup(HDR("accept-encoding")));
    struct_set(c, "HTTP_CONNECTION", v_strdup(HDR("connection")));
    struct_set(c, "HTTP_IF_MODIFIED_SINCE", v_strdup(HDR("if-modified-since")));
    tls_set_cgi(c, req);                     /* HTTPS, SERVER_PORT_SECURE, CERT_* */
    struct_set(c, "CF_TEMPLATE_PATH", v_strdup(filepath));
    struct_set(c, "WEB_SERVER_API", v_str("KFHTTPD"));
#undef HDR
}

static void load_debug_settings(RState *rs) {
    rs->show_vars = cfg_int("Debug", "ShowVariables", 0);
    rs->show_proc_time = cfg_int("Debug", "ShowProcessingTime", 0);
    rs->detail_view = cfg_int("Debug", "DetailView", 0);
    rs->show_sql = cfg_int("Debug", "ShowSQL", 1);
    rs->show_query_info = cfg_int("Debug", "ShowQueryInfo", 0);
    rs->show_tpl_path = cfg_int("Debug", "ShowTemplatePath", 1);
    rs->show_debug = rs->show_vars || rs->show_proc_time || rs->show_query_info;
    rs->suppress_ws = cfg_int(REG_SERVER, "SuppressWhitespace", 0);
    rs->strict_attrs = cfg_int(REG_SERVER, "StrictAttributeValidation", 0);
    rs->lockmode_server = cfg("Locking", "ServerScope", "none")[0];
    rs->lockmode_app = cfg("Locking", "ApplicationScope", "none")[0];
    rs->lockmode_session = cfg("Locking", "SessionScope", "none")[0];
}

void kf_handle_cfml(KfConn *conn, HttpReq *req, const char *script_name, const char *filepath) {
    RState *rs = kmalloc(sizeof(RState));
    rs->http = req;
    rs->docroot = req->docroot ? req->docroot : G.webroot;
    rs->arena = g_arena;
    rs->status = 200;
    rs->start_ms = kf_time_ms();
    rs->form = struct_new(); rs->url = struct_new(); rs->cgi = struct_new(); rs->cookie = struct_new();
    rs->request = struct_new(); rs->server = g_server_scope;
    buf_init(&rs->page); buf_init(&rs->htmlhead);
    load_debug_settings(rs);
    setup_cgi(rs, req, script_name, filepath);
    if (req->query) parse_urlencoded(rs->url, req->query, strlen(req->query), NULL);
    Val *ck = struct_get(req->headers, "cookie");
    if (ck) parse_cookies(rs->cookie, v_tostr(*ck));
    Buf fieldnames; buf_init(&fieldnames);
    if (!strcmp(req->method, "POST")) {
        const char *ct = req->content_type ? req->content_type : "";
        if (kf_stristr(ct, "multipart/form-data")) parse_multipart(rs, ct, req->body, req->bodylen, &fieldnames);
        else parse_urlencoded(rs->form, req->body ? req->body : "", req->bodylen, &fieldnames);
        struct_set(rs->form, "FieldNames", v_str(buf_cstr(&fieldnames)));
    }
    /* request timeout: Administrator default, ?RequestTimeout= override */
    double to = cfg_int(REG_SERVER, "TimeoutRequests", 1) ? cfg_int(REG_SERVER, "RequestTimeout", 30) : 0;
    Val *rt = struct_get(rs->url, "RequestTimeout");
    double d;
    if (rt && v_tonum(*rt, &d) && d > 0) to = d;
    rs->timeout_s = to;
    rs->deadline_ms = to > 0 ? rs->start_ms + to * 1000 : 0;
    if (cfg_int(REG_SERVER, "MaxRequestMemoryMB", 256) > 0)
        arena_set_limit(g_arena, (size_t)cfg_int(REG_SERVER, "MaxRequestMemoryMB", 256) * 1024 * 1024);

    Buf errs; buf_init(&errs);
    /* handled after Application.cfm runs, so a CFERROR TYPE="Validation" page can take over */
    if (!strcmp(req->method, "POST") && form_validation(rs, &errs)) rs->validation_errors = buf_cstr(&errs);
    int ai = active_add(script_name);
    run_request(rs, filepath);
    active_remove(ai);
    if (rs->sess) {
        if (cfg_int("Locking", "SingleThreadedSessions", 0)) pthread_mutex_unlock(&rs->sess->mu);
        sess_release(rs->sess);
    }
    if (rs->client_enabled && rs->appname) client_save(rs, rs->appname);
    if (rs->ftp) { extern void ftp_cleanup(RState *); ftp_cleanup(rs); }
    templates_release(rs);
    send_engine_response(conn, rs);
    double ms = kf_time_ms() - rs->start_ms;
    if (cfg_int("Logging", "LogSlowPages", 0) && ms > cfg_int("Logging", "SlowPageSeconds", 30) * 1000.0)
        kf_log("server.log", "Warning", "%s took %.0f seconds to process.", filepath, ms / 1000);
    if (rs->formfiles)
        for (int i = 0; i < rs->formfiles->n; i++) {
            Val *t = struct_get(rs->formfiles->e[i].v.u.st, "tmpfile");
            if (t) unlink(v_tostr(*t));
        }
}

/* ================================================================ reading requests */
enum { RQ_OK = 0, RQ_CLOSED = -1, RQ_BAD = -2, RQ_TOO_LARGE = -3, RQ_TIMEOUT = -4, RQ_NOT_IMPL = -5, RQ_VERSION = -6,
       RQ_EXPECT = -7, RQ_HDR_TOO_LARGE = -8 };
#define MAX_HEADER (64 * 1024)

static int is_token_char(int ch) {
    return ch > 32 && ch < 127 && !strchr("()<>@,;:\\\"/[]?={}", ch);
}

/* does a comma-separated header value (Connection, Expect, Transfer-Encoding) contain the token? */
static int has_token(const char *v, const char *tok) {
    size_t tl = strlen(tok);
    for (const char *p = v; *p; ) {
        while (*p == ' ' || *p == '\t' || *p == ',') p++;
        size_t n = strcspn(p, ",");
        size_t m = n;
        while (m && (p[m - 1] == ' ' || p[m - 1] == '\t')) m--;
        if (m == tl && !kf_strnicmp(p, tok, tl)) return 1;
        p += n;
    }
    return 0;
}

/* body deadline: generous for honest uploads (64 KB/s minimum), finite for a slow-POST attack */
static double body_deadline(size_t len) { return kf_time_ms() + 30000.0 + (double)len / 65.536; }

static int read_chunked_body(KfConn *c, Buf *body) {
    for (;;) {
        char *line = kc_read_line(c, 1024);
        if (!line) return c->timed_out ? RQ_TIMEOUT : RQ_BAD;
        char *end;
        errno = 0;
        unsigned long long sz = strtoull(line, &end, 16);
        if (end == line || errno || (*end && *end != ';' && *end != ' ' && *end != '\t')) return RQ_BAD;
        if (sz > MAX_BODY || body->len + sz > MAX_BODY) return RQ_TOO_LARGE;
        if (sz == 0) {
            size_t trailer = 0;
            for (;;) {                                         /* trailer fields are read and ignored */
                char *t = kc_read_line(c, MAX_HEADER);
                if (!t) return c->timed_out ? RQ_TIMEOUT : RQ_BAD;
                if (!*t) return RQ_OK;
                if ((trailer += strlen(t)) > MAX_HEADER) return RQ_HDR_TOO_LARGE;
            }
        }
        c->rdeadline = body_deadline(body->len + sz);
        if (kc_read_exact(c, (size_t)sz, body)) return c->timed_out ? RQ_TIMEOUT : RQ_BAD;
        char *crlf = kc_read_line(c, 2);
        if (!crlf || *crlf) return crlf ? RQ_BAD : (c->timed_out ? RQ_TIMEOUT : RQ_BAD);
    }
}

/* Read one request from the connection, leaving anything after it (a pipelined request) in the buffer.
 * first_byte_deadline: how long to wait for the request to start (the keep-alive idle timeout);
 * once it has started the whole header block must arrive within HeaderTimeout seconds. */
static int read_request(KfConn *c, HttpReq *req, double first_byte_deadline) {
    c->rdeadline = first_byte_deadline;
    for (;;) {                                                 /* skip the CRLF old browsers send after a POST body */
        while (kc_avail(c) && (c->rbuf[c->rpos] == '\r' || c->rbuf[c->rpos] == '\n')) c->rpos++;
        if (kc_avail(c)) break;
        if (kc_fill(c) <= 0) return RQ_CLOSED;
    }
    c->rdeadline = kf_time_ms() + t_web.header_timeout * 1000.0;
    size_t scanned = 0, hdr_len = 0;
    for (;;) {
        const char *s = c->rbuf + c->rpos;
        size_t n = kc_avail(c);
        for (size_t i = scanned; i < n; i++)
            if (s[i] == '\n' && ((i >= 1 && s[i - 1] == '\n') || (i >= 2 && s[i - 1] == '\r' && s[i - 2] == '\n'))) {
                hdr_len = i + 1;
                break;
            }
        if (hdr_len) break;
        scanned = n;
        if (n > MAX_HEADER) return RQ_HDR_TOO_LARGE;
        if (kc_fill(c) <= 0) return c->timed_out ? RQ_TIMEOUT : RQ_CLOSED;
    }
    if (hdr_len > MAX_HEADER) return RQ_HDR_TOO_LARGE;
    char *hdrs = kstrndup(c->rbuf + c->rpos, hdr_len);
    c->rpos += hdr_len;
    if (memchr(hdrs, 0, hdr_len)) return RQ_BAD;

    /* request line: METHOD SP request-target [SP HTTP/1.x] */
    char *save = NULL;
    char *line = strtok_r(hdrs, "\n", &save);
    if (!line) return RQ_BAD;
    size_t ll = strlen(line);
    if (ll && line[ll - 1] == '\r') line[--ll] = 0;
    char *sp1 = strchr(line, ' ');
    if (!sp1) return RQ_BAD;
    *sp1 = 0;
    char *u = sp1 + 1;
    while (*u == ' ') u++;
    char *sp2 = strchr(u, ' ');
    char *v = NULL;
    if (sp2) { *sp2 = 0; v = sp2 + 1; while (*v == ' ') v++; if (!*v) v = NULL; }
    if (!*line || !*u) return RQ_BAD;
    for (char *p = line; *p; p++) if (!is_token_char((unsigned char)*p)) return RQ_BAD;
    req->method = kf_upper(line);
    req->head = !strcmp(req->method, "HEAD");
    if (v) {
        if (strncmp(v, "HTTP/", 5)) return RQ_BAD;
        if (v[5] != '1' || v[6] != '.' || !isdigit((unsigned char)v[7]) || v[8]) return RQ_VERSION;
        req->http11 = v[7] >= '1';
    }
    req->version = kstrdup(req->http11 ? "HTTP/1.1" : "HTTP/1.0");
    char *abs_host = NULL;
    if (!kf_strnicmp(u, "http://", 7) || !kf_strnicmp(u, "https://", 8)) {    /* absolute form */
        char *h = strstr(u, "//") + 2;
        size_t hl = strcspn(h, "/?");
        abs_host = kstrndup(h, hl);
        u = h[hl] == '/' ? h + hl : kprintf("/%s", h + hl);
    }
    if (u[0] != '/' && strcmp(u, "*")) return RQ_BAD;
    req->uri = kstrdup(u);
    char *q = strchr(req->uri, '?');
    req->path = q ? kstrndup(req->uri, q - req->uri) : kstrdup(req->uri);
    req->query = q ? kstrdup(q + 1) : NULL;

    /* header fields */
    req->headers = struct_new();
    const char *last_key = NULL;
    long long content_length = -1;
    int hosts = 0;
    for (line = strtok_r(NULL, "\n", &save); line; line = strtok_r(NULL, "\n", &save)) {
        ll = strlen(line);
        if (ll && line[ll - 1] == '\r') line[--ll] = 0;
        if (!ll) break;
        if (line[0] == ' ' || line[0] == '\t') {               /* obsolete line folding */
            if (!last_key) return RQ_BAD;
            Val *pv = struct_get(req->headers, last_key);
            struct_set(req->headers, last_key, v_str(kprintf("%s %s", pv ? v_tostr(*pv) : "", kf_trim(line))));
            continue;
        }
        char *colon = strchr(line, ':');
        if (!colon || colon == line) return RQ_BAD;
        *colon = 0;
        for (char *p = line; *p; p++) if (!is_token_char((unsigned char)*p)) return RQ_BAD;   /* no "Name :" */
        char *key = kf_lower(line), *val = kf_trim(colon + 1);
        if (!strcmp(key, "content-length")) {
            if (!*val) return RQ_BAD;
            for (char *p = val; *p; p++) if (!isdigit((unsigned char)*p)) return RQ_BAD;
            long long n = strlen(val) > 15 ? (long long)MAX_BODY + 1 : atoll(val);
            if (content_length >= 0 && n != content_length) return RQ_BAD;
            content_length = n;
        }
        if (!strcmp(key, "host") && hosts++) return RQ_BAD;
        Val *old = struct_get(req->headers, key);
        if (old && strcmp(key, "content-length"))
            val = kprintf("%s%s%s", v_tostr(*old), !strcmp(key, "cookie") ? "; " : ", ", val);
        struct_set(req->headers, key, v_str(val));
        last_key = key;
    }
    if (abs_host) struct_set(req->headers, "host", v_str(abs_host));
    if (req->http11 && !struct_get(req->headers, "host")) return RQ_BAD;

    Val *conn_hdr = struct_get(req->headers, "connection");
    const char *ch = conn_hdr ? v_tostr(*conn_hdr) : "";
    req->keep_alive = req->http11 ? !has_token(ch, "close") : has_token(ch, "keep-alive");

    Val *host = struct_get(req->headers, "host");
    const char *hv = host ? v_tostr(*host) : "";
    if (*hv == '[') req->server_name = kstrndup(hv, strcspn(hv, "]") + 1);
    else req->server_name = *hv ? kstrndup(hv, strcspn(hv, ":")) : kstrdup("localhost");
    Val *ct = struct_get(req->headers, "content-type");
    req->content_type = ct ? (char *)v_tostr(*ct) : NULL;

    /* message body: Transfer-Encoding: chunked wins over Content-Length (and then we close afterwards) */
    Val *te = struct_get(req->headers, "transfer-encoding");
    int chunked = 0;
    if (te) {
        const char *tv = kf_trim(v_tostr(*te));
        if (kf_stricmp(tv, "chunked") && kf_stricmp(tv, "identity")) return RQ_NOT_IMPL;
        chunked = !kf_stricmp(tv, "chunked");
        if (content_length >= 0) req->keep_alive = 0;
        if (!req->http11) req->keep_alive = 0;
    }
    if (!chunked && content_length > MAX_BODY) return RQ_TOO_LARGE;
    int has_body = chunked || content_length > 0;
    Val *expect = struct_get(req->headers, "expect");
    if (expect) {
        if (!has_token(v_tostr(*expect), "100-continue")) return RQ_EXPECT;
        /* tell the client to go ahead, unless it already did */
        if (has_body && req->http11 && !kc_avail(c)) {
            static const char cont[] = "HTTP/1.1 100 Continue\r\n\r\n";
            kc_set_write_budget(c, sizeof cont);
            if (kc_write(c, cont, sizeof cont - 1)) return RQ_CLOSED;
        }
    }
    Buf body; buf_init(&body);
    if (chunked) {
        c->rdeadline = body_deadline(0);
        int rc = read_chunked_body(c, &body);
        if (rc) return rc;
        struct_set(req->headers, "content-length", v_str(kprintf("%zu", body.len)));
    } else if (content_length > 0) {
        c->rdeadline = body_deadline((size_t)content_length);
        if (kc_read_exact(c, (size_t)content_length, &body)) return c->timed_out ? RQ_TIMEOUT : RQ_CLOSED;
    }
    req->body = buf_cstr(&body);
    req->bodylen = body.len;
    return RQ_OK;
}

static void access_log(HttpReq *req) {
    if (!req->resp_status) return;
    time_t t = time(NULL);
    struct tm tm; localtime_r(&t, &tm);
    char ts[64]; strftime(ts, sizeof ts, "%d/%b/%Y:%H:%M:%S %z", &tm);
    char *bytes = req->resp_bytes ? kprintf("%zu", req->resp_bytes) : "-";
    char *line = kprintf("%s - - [%s] \"%s %s %s\" %d %s\n", req->remote_addr ? req->remote_addr : "-", ts,
                         req->method ? req->method : "-", req->uri ? req->uri : "-", req->version ? req->version : "-",
                         req->resp_status, bytes);
    char *p = kf_path_join(kf_log_dir(), "access.log");
    kf_write_file(p, line, strlen(line), 1);
}

typedef struct Conn { int fd; int secure; int port; struct sockaddr_storage addr; } Conn;

/* "yowza.localhost" (or www.yowza.localhost) -> wwwroot/sites/yowza if it exists */
static const char *site_root(const char *host) {
    if (!host) return G.webroot;
    size_t hl = strlen(host);
    if (hl <= 10 || kf_stricmp(host + hl - 10, ".localhost")) return G.webroot;
    const char *end = host + hl - 10, *start = end;
    while (start > host && start[-1] != '.') start--;
    char *name = kf_lower(kstrndup(start, end - start));
    for (char *p = name; *p; p++) if (!isalnum((unsigned char)*p) && *p != '-' && *p != '_') return G.webroot;
    char *dir = kf_path_join(kf_path_join(G.webroot, "sites"), name);
    struct stat st;
    if (stat(dir, &st) == 0 && S_ISDIR(st.st_mode)) return dir;
    return G.webroot;
}

/* the scheme and port a redirect to one of our own hosts must keep */
static char *own_origin(HttpReq *req, const char *host) {
    const char *scheme = req->secure ? "https" : "http";
    int dflt = req->secure ? 443 : 80;
    return req->server_port == dflt ? kprintf("%s://%s", scheme, host) : kprintf("%s://%s:%d", scheme, host, req->server_port);
}

static void handle_request(KfConn *c, HttpReq *req) {
    if (!strcmp(req->uri, "*")) {                               /* OPTIONS * */
        send_response(c, req, 200, NULL, "Allow: GET, HEAD, POST, OPTIONS\r\n", "text/plain", "", 0);
        return;
    }
    /* virtual sites, IIS-style: http://<name>.localhost/ serves wwwroot/sites/<name>/ */
    const char *docroot = site_root(req->server_name);
    /* map URL to file */
    char *upath = kf_urldecode(req->path, strlen(req->path));
    if (strstr(upath, "..") || upath[0] != '/' || strstr(req->path, "%00")) {
        simple_response(c, req, 403, "Forbidden", "Access denied.");
        return;
    }
    char *fpath = kf_path_join(docroot, upath);
    /* every site shares /CFIDE (cfform.js, the Administrator) and the stock /images */
    if (docroot != G.webroot && access(fpath, F_OK) != 0 &&
        (!kf_strnicmp(upath, "/CFIDE/", 7) || !kf_strnicmp(upath, "/images/", 8)))
        fpath = kf_path_join(G.webroot, upath);
    struct stat st;
    /* the static 1999-Web sites link to each other with relative paths ("../orinoco/index.html"), which on a virtual
       host land on /orinoco/...: send those to the other site's host, and anything else only the main site has
       (/web1999/) to the main host - keeping the scheme and port the request came in on */
    if (docroot != G.webroot && stat(fpath, &st) != 0 && !kf_resolve_ci(fpath)) {
        const char *seg = upath + 1, *sl = strchr(seg, '/');
        char *name = kf_lower(sl ? kstrndup(seg, sl - seg) : kstrdup(seg));
        char *other = kf_path_join(kf_path_join(G.webroot, "sites"), name);
        char *main_path = kf_path_join(G.webroot, upath);
        char *loc = NULL;
        if (*name && stat(other, &st) == 0 && S_ISDIR(st.st_mode))
            loc = kprintf("%s/%s", own_origin(req, kprintf("%s.localhost", name)), sl ? sl + 1 : "");
        else if (stat(main_path, &st) == 0 || kf_resolve_ci(main_path))
            loc = kprintf("%s%s", own_origin(req, "localhost"), req->path);
        if (loc) {
            if (req->query) loc = kprintf("%s?%s", loc, req->query);
            redirect_response(c, req, loc);
            return;
        }
    }
    if (stat(fpath, &st) != 0) { char *ci = kf_resolve_ci(fpath); if (ci) fpath = ci; }
    if (stat(fpath, &st) == 0 && S_ISDIR(st.st_mode)) {
        if (upath[strlen(upath) - 1] != '/') {
            redirect_response(c, req, kprintf("%s/%s%s", req->path, req->query ? "?" : "", req->query ? req->query : ""));
            return;
        }
        char *idx = find_index(fpath);
        if (!idx) {
            /* like IIS 4.0 out of the box: browsing is off unless the directory contains .kfbrowse */
            if (access(kf_path_join(fpath, ".kfbrowse"), F_OK) == 0) directory_listing(c, req, upath, fpath);
            else simple_response(c, req, 403, "Directory Listing Denied", "This Virtual Directory does not allow contents to be listed.");
            return;
        }
        upath = kprintf("%s%s", upath, strrchr(idx, '/') + 1);
        fpath = idx;
    }
    if (is_cfml(fpath)) {
        if (access(fpath, R_OK) != 0) {
            char *mth = cfg(REG_SERVER, "MissingTemplateHandler", "");
            if (mth && *mth) {
                Ctx tmp; memset(&tmp, 0, sizeof tmp); tmp.tagdir = G.webroot;
                fpath = (char *)resolve_template_path(&tmp, mth, 0);
            }
        }
        pthread_mutex_lock(&stats_mu); G.queued_requests++; pthread_mutex_unlock(&stats_mu);
        sem_wait(&req_sem);
        pthread_mutex_lock(&stats_mu); G.queued_requests--; G.active_requests++; G.requests_served++; pthread_mutex_unlock(&stats_mu);
        req->docroot = docroot;
        kf_handle_cfml(c, req, upath, fpath);
        pthread_mutex_lock(&stats_mu); G.active_requests--; pthread_mutex_unlock(&stats_mu);
        sem_post(&req_sem);
    } else if (stat(fpath, &st) == 0) {
        if (strcmp(req->method, "GET") && strcmp(req->method, "HEAD") && strcmp(req->method, "POST")) {
            send_response(c, req, 405, NULL, "Allow: GET, HEAD, POST\r\n", "text/plain", "Method Not Allowed\n", 19);
            return;
        }
        serve_static(c, req, fpath);
    } else {
        simple_response(c, req, 404, "Object Not Found",
                        kprintf("The requested URL %s was not found on this server.", kf_html_escape(upath)));
    }
}

/* per-thread engine state must not leak from one request into the next on the same connection */
static void reset_thread_state(void) {
    tags_io_thread_reset();
    tags_form_thread_reset();
    sql_thread_reset();
    parse_thread_reset();
    java_thread_reset();
}

static int conns_busy(void) {
    pthread_mutex_lock(&stats_mu);
    int busy = open_conns * 4 > t_web.max_conns * 3;                  /* over 75% of MaxConnections */
    pthread_mutex_unlock(&stats_mu);
    return busy;
}

static void *conn_thread(void *arg) {
    Conn *cn = arg;
    KfConn *c = kc_new(cn->fd);
    char ip[64] = "127.0.0.1";
    if (cn->addr.ss_family == AF_INET) inet_ntop(AF_INET, &((struct sockaddr_in *)&cn->addr)->sin_addr, ip, sizeof ip);
    else if (cn->addr.ss_family == AF_INET6) inet_ntop(AF_INET6, &((struct sockaddr_in6 *)&cn->addr)->sin6_addr, ip, sizeof ip);
    if (!strncmp(ip, "::ffff:", 7)) memmove(ip, ip + 7, strlen(ip + 7) + 1);
    int secure = cn->secure, port = cn->port;
    free(cn);
    Arena *a = arena_new(); g_arena = a;
    web_cfg(&t_web);
    g_arena = NULL; arena_free(a);
    int lingering = 0;
    if (secure && tls_server_accept(c, kf_time_ms() + t_web.header_timeout * 1000.0)) goto done;
    for (int n = 0;; n++) {
        a = arena_new(); g_arena = a;
        reset_thread_state();
        HttpReq *req = kmalloc(sizeof(HttpReq));
        req->conn = c;
        req->fd = c->fd;
        req->secure = secure;
        req->remote_addr = kstrdup(ip);
        req->server_port = port;
        req->nreq = n + 1;
        double wait = (n == 0 ? t_web.header_timeout : t_web.ka_timeout) * 1000.0;
        int rc = read_request(c, req, kf_time_ms() + wait);
        req->started_ms = kf_time_ms();
        if (rc != RQ_OK) {
            req->keep_alive = 0;
            switch (rc) {
            case RQ_BAD: simple_response(c, req, 400, "Bad Request", "Your browser sent a request that this server could not understand."); break;
            case RQ_TOO_LARGE: simple_response(c, req, 413, "Request Entity Too Large", "The request body is too large."); break;
            case RQ_HDR_TOO_LARGE: simple_response(c, req, 400, "Bad Request", "The request header is too large."); break;
            case RQ_TIMEOUT: simple_response(c, req, 408, "Request Timeout", "The server timed out waiting for the request."); break;
            case RQ_NOT_IMPL: simple_response(c, req, 501, "Not Implemented", "The request uses a transfer coding this server does not understand."); break;
            case RQ_VERSION: simple_response(c, req, 505, "HTTP Version Not Supported", "This server speaks HTTP/1.0 and HTTP/1.1."); break;
            case RQ_EXPECT: simple_response(c, req, 417, "Expectation Failed", "The expectation given in the Expect header cannot be met."); break;
            }
            access_log(req);
            lingering = rc != RQ_CLOSED && !c->closed;
            g_arena = NULL; arena_free(a);
            break;
        }
        if (req->keep_alive && (!t_web.keepalive || req->nreq >= t_web.ka_max || G.restart_requested || conns_busy()))
            req->keep_alive = 0;
        handle_request(c, req);
        access_log(req);
        int keep = req->keep_alive && !c->timed_out && !c->closed;
        g_arena = NULL; arena_free(a);
        if (!keep) { lingering = !c->closed && !c->timed_out; break; }
    }
done:
    if (lingering) kc_close_lingering(c);
    else kc_free(c);
    pthread_mutex_lock(&stats_mu); open_conns--; pthread_mutex_unlock(&stats_mu);
    return NULL;
}

static int open_listener(int port, const char *what) {
    struct addrinfo hints = {0}, *res;
    hints.ai_family = AF_UNSPEC; hints.ai_socktype = SOCK_STREAM; hints.ai_flags = AI_PASSIVE;
    char ps[16]; snprintf(ps, sizeof ps, "%d", port);
    if (getaddrinfo(G.bind, ps, &hints, &res)) { fprintf(stderr, "KoldFusion: cannot resolve %s\n", G.bind); return -1; }
    int fd = socket(res->ai_family, res->ai_socktype | SOCK_CLOEXEC, 0);
    int one = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
    if (fd < 0 || bind(fd, res->ai_addr, res->ai_addrlen) || listen(fd, 128)) {
        fprintf(stderr, "KoldFusion: cannot listen on %s:%d%s: %s\n", G.bind, port, what, strerror(errno));
        kf_log("server.log", "Error", "Cannot listen on %s:%d%s: %s", G.bind, port, what, strerror(errno));
        if (fd >= 0) close(fd);
        freeaddrinfo(res);
        return -1;
    }
    freeaddrinfo(res);
    return fd;
}

int http_serve(void) {
    signal(SIGPIPE, SIG_IGN);
    Arena *a = arena_new(); g_arena = a;
    int limit = cfg_int(REG_SERVER, "LimitSimultaneousRequests", 5);
    WebCfg w; web_cfg(&w);
    g_arena = NULL; arena_free(a);
    if (limit < 1) limit = 1;
    sem_init(&req_sem, 0, (unsigned)limit);

    listen_fd = open_listener(G.port, "");
    if (listen_fd < 0) return 1;
    int sport = tls_server_port();
    if (sport > 0) ssl_listen_fd = open_listener(sport, " (SSL)");   /* not fatal: the plain listener still works */
    pthread_t wd;
    pthread_create(&wd, NULL, watchdog, NULL);
    pthread_detach(wd);
    a = arena_new(); g_arena = a;
    kf_log("server.log", "Information", "KoldFusion Application Server %s started, listening on %s:%d%s (limit %d simultaneous requests).",
           KF_VERSION_STR, G.bind, G.port, ssl_listen_fd >= 0 ? kprintf(" and %d (SSL)", sport) : "", limit);
    g_arena = NULL; arena_free(a);
    for (;;) {
        struct pollfd pf[2] = {{listen_fd, POLLIN, 0}, {ssl_listen_fd, POLLIN, 0}};
        int np = ssl_listen_fd >= 0 ? 2 : 1;
        int pr = poll(pf, np, 1000);
        if (G.restart_requested) break;
        if (pr <= 0) continue;
        for (int i = 0; i < np; i++) {
            if (!(pf[i].revents & (POLLIN | POLLERR | POLLHUP))) continue;
            Conn *cn = calloc(1, sizeof(Conn));
            socklen_t al = sizeof cn->addr;
            int fd = accept4(pf[i].fd, (struct sockaddr *)&cn->addr, &al, SOCK_CLOEXEC);
            if (fd < 0) { free(cn); if (errno != EINTR && errno != EAGAIN) usleep(10000); continue; }
            cn->fd = fd;
            cn->secure = i == 1;
            cn->port = i == 1 ? sport : G.port;
            pthread_mutex_lock(&stats_mu);
            int full = open_conns >= w.max_conns;
            if (!full) open_conns++;
            pthread_mutex_unlock(&stats_mu);
            if (full) {
                /* too many connections: a short 503 on the plain port (one non-blocking try), and close */
                if (!cn->secure) {
                    static const char busy[] = "HTTP/1.0 503 Service Unavailable\r\nContent-Type: text/plain\r\n"
                                               "Content-Length: 25\r\nConnection: close\r\n\r\nServer too busy, sorry.\r\n";
                    if (send(fd, busy, sizeof busy - 1, MSG_NOSIGNAL | MSG_DONTWAIT) < 0) {}
                }
                close(fd); free(cn);
                continue;
            }
            pthread_attr_t at;
            pthread_attr_init(&at);
            pthread_attr_setdetachstate(&at, PTHREAD_CREATE_DETACHED);
            pthread_attr_setstacksize(&at, 16 * 1024 * 1024);
            pthread_t th;
            if (pthread_create(&th, &at, conn_thread, cn)) {
                close(fd); free(cn);
                pthread_mutex_lock(&stats_mu); open_conns--; pthread_mutex_unlock(&stats_mu);
            }
            pthread_attr_destroy(&at);
        }
    }
    close(listen_fd);
    if (ssl_listen_fd >= 0) close(ssl_listen_fd);
    return 0;
}

void http_request_restart(void) {
    G.restart_requested = 1;
    if (listen_fd >= 0) shutdown(listen_fd, SHUT_RDWR);
}

/* command line: kfserver --run /path/to/file.cfm [query-string] */
int kf_run_cli(const char *file, const char *query) {
    Arena *a = arena_new(); g_arena = a;
    web_cfg(&t_web);
    HttpReq *req = kmalloc(sizeof(HttpReq));
    KfConn *out = calloc(1, sizeof(KfConn));
    out->fd = 1;
    out->notsock = 1;
    req->conn = out;
    req->fd = 1;
    req->method = "GET";
    char rp[4096];
    const char *abs = realpath(file, rp) ? rp : file;
    const char *rel = abs;
    if (!strncmp(abs, G.webroot, strlen(G.webroot))) rel = abs + strlen(G.webroot);
    const char *sites = kf_path_join(G.webroot, "sites/");
    if (!strncmp(abs, sites, strlen(sites))) {
        const char *nm = abs + strlen(sites), *sl = strchr(nm, '/');
        if (sl) { req->docroot = kstrndup(abs, sl - abs); rel = sl; req->server_name = kprintf("%.*s.localhost", (int)(sl - nm), nm); }
    }
    req->path = kstrdup(rel);
    req->uri = kstrdup(rel);
    req->query = query ? kstrdup(query) : NULL;
    req->version = "HTTP/1.0";
    req->headers = struct_new();
    req->remote_addr = "127.0.0.1";
    if (!req->server_name) req->server_name = "localhost";
    req->server_port = G.port;
    sem_init(&req_sem, 0, 1);
    kf_handle_cfml(out, req, rel, abs);
    free(out);
    return 0;
}
