/*
 * http.c - the built-in web server and the HTTP client used by CFHTTP.
 *
 * ColdFusion 4.5 sat behind IIS/Netscape/Apache via a connector stub. We
 * fold the web server in: static files are served directly, .cfm/.cfml/.dbm
 * go to the engine. HTTP/1.0, one request per connection, like it's 1999.
 */
#define _GNU_SOURCE
#include "engine.h"
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

#define SERVER_SOFTWARE "KoldFusion/4.5.1 (Unix)"
#define MAX_BODY (64 * 1024 * 1024)

static sem_t req_sem;
static pthread_mutex_t stats_mu = PTHREAD_MUTEX_INITIALIZER;
static int listen_fd = -1;
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

static int write_all(int fd, const char *p, size_t n) {
    while (n) {
        ssize_t w = write(fd, p, n);
        if (w < 0) { if (errno == EINTR) continue; return -1; }
        p += w; n -= (size_t)w;
    }
    return 0;
}

static const char *status_text(int code) {
    switch (code) {
    case 200: return "OK"; case 201: return "Created"; case 204: return "No Content";
    case 301: return "Moved Permanently"; case 302: return "Object Moved"; case 304: return "Not Modified";
    case 400: return "Bad Request"; case 401: return "Unauthorized"; case 403: return "Forbidden";
    case 404: return "Object Not Found"; case 405: return "Method Not Allowed"; case 500: return "Internal Server Error";
    case 503: return "Service Unavailable";
    }
    return "Unknown";
}

static void simple_response(int fd, int code, const char *title, const char *body) {
    char *html = kprintf("<HTML><HEAD><TITLE>%s</TITLE></HEAD>\n<BODY BGCOLOR=\"#FFFFFF\">\n<H2>HTTP %d - %s</H2>\n"
                         "<FONT FACE=\"Arial, Helvetica\" SIZE=\"2\">%s</FONT>\n<HR NOSHADE SIZE=1>\n"
                         "<FONT FACE=\"Arial, Helvetica\" SIZE=\"1\"><I>%s</I></FONT>\n</BODY></HTML>\n",
                         title, code, title, body, SERVER_SOFTWARE);
    char *hdr = kprintf("HTTP/1.0 %d %s\r\nServer: %s\r\nDate: %s\r\nContent-Type: text/html\r\nContent-Length: %zu\r\n"
                        "Connection: close\r\n\r\n", code, status_text(code), SERVER_SOFTWARE, http_date(time(NULL)), strlen(html));
    write_all(fd, hdr, strlen(hdr));
    write_all(fd, html, strlen(html));
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
static const char *apply_zoom(const char *body, size_t len, size_t *outlen) {
    *outlen = len;
    int zoom = cfg_int(REG_SERVER, "DisplayZoom", 175);
    if (zoom <= 0 || zoom == 100) return body;
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
        "return o.call(window,u,n,f)};if(r)window.resizeTo=function(w,h){return r.call(window,Math.round(w*z),Math.round(h*z))}})(%g);</script>",
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

static void send_engine_response(int fd, RState *rs) {
    Buf h; buf_init(&h);
    int status = rs->status ? rs->status : 200;
    const char *st = rs->status_text && *rs->status_text ? rs->status_text : status_text(status);
    buf_printf(&h, "HTTP/1.0 %d %s\r\nServer: %s\r\nDate: %s\r\n", status, st, SERVER_SOFTWARE, http_date(time(NULL)));
    if (rs->location) buf_printf(&h, "Location: %s\r\n", rs->location);
    if (rs->setcookies)
        for (int i = 0; i < rs->setcookies->n; i++) buf_printf(&h, "Set-Cookie: %s\r\n", v_tostr(rs->setcookies->v[i]));
    if (rs->headers)
        for (int i = 0; i < rs->headers->n; i++)
            buf_printf(&h, "%s: %s\r\n", rs->headers->e[i].key, v_tostr(rs->headers->e[i].v));

    if (rs->content_file) {
        size_t len;
        char *data = kf_read_file(rs->content_file, &len);
        if (!data) { data = strdup(""); len = 0; }
        buf_printf(&h, "Content-Type: %s\r\nContent-Length: %zu\r\nConnection: close\r\n\r\n",
                   rs->content_type ? rs->content_type : mime_type_for(rs->content_file), len);
        write_all(fd, h.s, h.len);
        write_all(fd, data, len);
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
    buf_printf(&h, "Content-Type: %s\r\nContent-Length: %zu\r\nConnection: close\r\n\r\n", ctype, blen);
    write_all(fd, h.s, h.len);
    write_all(fd, body, blen);
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

static void directory_listing(int fd, const char *urlpath, const char *dir) {
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
    char *hdr = kprintf("HTTP/1.0 200 OK\r\nServer: %s\r\nContent-Type: text/html\r\nContent-Length: %zu\r\nConnection: close\r\n\r\n",
                        SERVER_SOFTWARE, b.len);
    write_all(fd, hdr, strlen(hdr));
    write_all(fd, b.s, b.len);
}

static void serve_static(int fd, HttpReq *req, const char *path) {
    struct stat st;
    stat(path, &st);
    Val *ims = struct_get(req->headers, "if-modified-since");
    char *lm = http_date(st.st_mtime);
    if (ims && !strcmp(v_tostr(*ims), lm)) {
        char *hdr = kprintf("HTTP/1.0 304 Not Modified\r\nServer: %s\r\nDate: %s\r\nConnection: close\r\n\r\n",
                            SERVER_SOFTWARE, http_date(time(NULL)));
        write_all(fd, hdr, strlen(hdr));
        return;
    }
    size_t len;
    char *raw = kf_read_file(path, &len);
    if (!raw) { simple_response(fd, 403, "Forbidden", "You do not have permission to read this file."); return; }
    const char *data = raw;
    if (!strcmp(mime_type_for(path), "text/html")) data = apply_zoom(raw, len, &len);
    char *hdr = kprintf("HTTP/1.0 200 OK\r\nServer: %s\r\nDate: %s\r\nLast-Modified: %s\r\nContent-Type: %s\r\n"
                        "Content-Length: %zu\r\nConnection: close\r\n\r\n",
                        SERVER_SOFTWARE, http_date(time(NULL)), lm, mime_type_for(path), len);
    write_all(fd, hdr, strlen(hdr));
    if (strcmp(req->method, "HEAD")) write_all(fd, data, len);
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
    struct_set(c, "HTTPS", v_str("off"));
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

void kf_handle_cfml(int fd, HttpReq *req, const char *script_name, const char *filepath) {
    RState *rs = kmalloc(sizeof(RState));
    rs->http = req;
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
    send_engine_response(fd, rs);
    double ms = kf_time_ms() - rs->start_ms;
    if (cfg_int("Logging", "LogSlowPages", 0) && ms > cfg_int("Logging", "SlowPageSeconds", 30) * 1000.0)
        kf_log("server.log", "Warning", "%s took %.0f seconds to process.", filepath, ms / 1000);
    if (rs->formfiles)
        for (int i = 0; i < rs->formfiles->n; i++) {
            Val *t = struct_get(rs->formfiles->e[i].v.u.st, "tmpfile");
            if (t) unlink(v_tostr(*t));
        }
}

static int read_request(int fd, HttpReq *req) {
    Buf b; buf_init(&b);
    char tmp[8192];
    size_t hdr_end = 0;
    for (;;) {
        ssize_t r = recv(fd, tmp, sizeof tmp, 0);
        if (r <= 0) return -1;
        buf_put(&b, tmp, (size_t)r);
        char *e = memmem(b.s, b.len, "\r\n\r\n", 4);
        if (e) { hdr_end = (size_t)(e - b.s) + 4; break; }
        if (b.len > 64 * 1024) return -2;
    }
    char *hdrs = kstrndup(b.s, hdr_end);
    char *line_end = strstr(hdrs, "\r\n");
    *line_end = 0;
    char *m = strtok(hdrs, " "), *u = strtok(NULL, " "), *v = strtok(NULL, " ");
    if (!m || !u) return -2;
    req->method = kf_upper(m);
    req->uri = kstrdup(u);
    req->version = kstrdup(v ? v : "HTTP/1.0");
    char *q = strchr(req->uri, '?');
    req->path = q ? kstrndup(req->uri, q - req->uri) : kstrdup(req->uri);
    req->query = q ? kstrdup(q + 1) : NULL;
    req->headers = struct_new();
    for (char *line = strtok(line_end + 2, "\r\n"); line; line = strtok(NULL, "\r\n")) {
        char *colon = strchr(line, ':');
        if (!colon) continue;
        *colon = 0;
        struct_set(req->headers, kf_lower(kf_trim(line)), v_str(kf_trim(colon + 1)));
    }
    Val *cl = struct_get(req->headers, "content-length");
    size_t want = cl ? (size_t)atol(v_tostr(*cl)) : 0;
    if (want > MAX_BODY) return -3;
    Val *ct = struct_get(req->headers, "content-type");
    req->content_type = ct ? (char *)v_tostr(*ct) : NULL;
    size_t have = b.len - hdr_end;
    Buf body; buf_init(&body);
    buf_put(&body, b.s + hdr_end, have);
    while (body.len < want) {
        ssize_t r = recv(fd, tmp, sizeof tmp, 0);
        if (r <= 0) break;
        buf_put(&body, tmp, (size_t)r);
    }
    req->body = buf_cstr(&body);
    req->bodylen = body.len < want ? body.len : want;
    Val *host = struct_get(req->headers, "host");
    req->server_name = host ? kstrndup(v_tostr(*host), strcspn(v_tostr(*host), ":")) : kstrdup("localhost");
    return 0;
}

static void access_log(HttpReq *req, int status) {
    time_t t = time(NULL);
    struct tm tm; localtime_r(&t, &tm);
    char ts[64]; strftime(ts, sizeof ts, "%d/%b/%Y:%H:%M:%S %z", &tm);
    char *line = kprintf("%s - - [%s] \"%s %s %s\" %d -\n", req->remote_addr, ts, req->method, req->uri, req->version, status);
    char *p = kf_path_join(kf_log_dir(), "access.log");
    kf_write_file(p, line, strlen(line), 1);
}

typedef struct Conn { int fd; struct sockaddr_storage addr; } Conn;

static void *conn_thread(void *arg) {
    Conn *cn = arg;
    int fd = cn->fd;
    Arena *a = arena_new();
    g_arena = a;
    HttpReq *req = kmalloc(sizeof(HttpReq));
    req->fd = fd;
    char ip[64] = "127.0.0.1";
    if (cn->addr.ss_family == AF_INET) inet_ntop(AF_INET, &((struct sockaddr_in *)&cn->addr)->sin_addr, ip, sizeof ip);
    else if (cn->addr.ss_family == AF_INET6) inet_ntop(AF_INET6, &((struct sockaddr_in6 *)&cn->addr)->sin6_addr, ip, sizeof ip);
    if (!strncmp(ip, "::ffff:", 7)) memmove(ip, ip + 7, strlen(ip + 7) + 1);
    req->remote_addr = kstrdup(ip);
    req->server_port = G.port;
    req->started_ms = kf_time_ms();
    free(cn);
    struct timeval tv = {30, 0};
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv);

    int rc = read_request(fd, req);
    if (rc == -2) simple_response(fd, 400, "Bad Request", "Your browser sent a request that this server could not understand.");
    else if (rc == -3) simple_response(fd, 413, "Request Entity Too Large", "The request body is too large.");
    if (rc) goto out;

    /* map URL to file */
    char *upath = kf_urldecode(req->path, strlen(req->path));
    if (strstr(upath, "..") || upath[0] != '/') { simple_response(fd, 403, "Forbidden", "Access denied."); goto out; }
    char *fpath = kf_path_join(G.webroot, upath);
    struct stat st;
    int status = 200;
    if (stat(fpath, &st) != 0) { char *ci = kf_resolve_ci(fpath); if (ci) fpath = ci; }
    if (stat(fpath, &st) == 0 && S_ISDIR(st.st_mode)) {
        if (upath[strlen(upath) - 1] != '/') {
            char *loc = kprintf("%s/%s%s", req->path, req->query ? "?" : "", req->query ? req->query : "");
            char *hdr = kprintf("HTTP/1.0 302 Object Moved\r\nServer: %s\r\nLocation: %s\r\nContent-Length: 0\r\nConnection: close\r\n\r\n",
                                SERVER_SOFTWARE, loc);
            write_all(fd, hdr, strlen(hdr));
            access_log(req, 302);
            goto out;
        }
        char *idx = find_index(fpath);
        if (!idx) {
            /* like IIS 4.0 out of the box: browsing is off unless the directory contains .kfbrowse */
            if (access(kf_path_join(fpath, ".kfbrowse"), F_OK) == 0) { directory_listing(fd, upath, fpath); access_log(req, 200); }
            else { simple_response(fd, 403, "Directory Listing Denied", "This Virtual Directory does not allow contents to be listed."); access_log(req, 403); }
            goto out;
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
        G.queued_requests++;
        sem_wait(&req_sem);
        G.queued_requests--;
        pthread_mutex_lock(&stats_mu); G.active_requests++; G.requests_served++; pthread_mutex_unlock(&stats_mu);
        kf_handle_cfml(fd, req, upath, fpath);
        pthread_mutex_lock(&stats_mu); G.active_requests--; pthread_mutex_unlock(&stats_mu);
        sem_post(&req_sem);
    } else if (stat(fpath, &st) == 0) {
        serve_static(fd, req, fpath);
    } else {
        status = 404;
        simple_response(fd, 404, "Object Not Found",
                        kprintf("The requested URL %s was not found on this server.", kf_html_escape(upath)));
    }
    access_log(req, status);
out:
    close(fd);
    g_arena = NULL;
    arena_free(a);
    return NULL;
}

int http_serve(void) {
    signal(SIGPIPE, SIG_IGN);
    Arena *a = arena_new(); g_arena = a;
    int limit = cfg_int(REG_SERVER, "LimitSimultaneousRequests", 5);
    g_arena = NULL; arena_free(a);
    if (limit < 1) limit = 1;
    sem_init(&req_sem, 0, (unsigned)limit);

    struct addrinfo hints = {0}, *res;
    hints.ai_family = AF_UNSPEC; hints.ai_socktype = SOCK_STREAM; hints.ai_flags = AI_PASSIVE;
    char port[16]; snprintf(port, sizeof port, "%d", G.port);
    if (getaddrinfo(G.bind, port, &hints, &res)) { fprintf(stderr, "KoldFusion: cannot resolve %s\n", G.bind); return 1; }
    listen_fd = socket(res->ai_family, res->ai_socktype | SOCK_CLOEXEC, 0);
    int one = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
    if (bind(listen_fd, res->ai_addr, res->ai_addrlen) || listen(listen_fd, 128)) {
        fprintf(stderr, "KoldFusion: cannot listen on %s:%d: %s\n", G.bind, G.port, strerror(errno));
        return 1;
    }
    freeaddrinfo(res);
    pthread_t wd;
    pthread_create(&wd, NULL, watchdog, NULL);
    pthread_detach(wd);
    kf_log("server.log", "Information", "KoldFusion Application Server %s started, listening on %s:%d (limit %d simultaneous requests).",
           KF_VERSION_STR, G.bind, G.port, limit);
    for (;;) {
        Conn *cn = calloc(1, sizeof(Conn));
        socklen_t al = sizeof cn->addr;
        int fd = accept4(listen_fd, (struct sockaddr *)&cn->addr, &al, SOCK_CLOEXEC);
        if (fd < 0) {
            free(cn);
            if (G.restart_requested) break;
            if (errno == EINTR) continue;
            usleep(10000);
            continue;
        }
        cn->fd = fd;
        pthread_attr_t at;
        pthread_attr_init(&at);
        pthread_attr_setdetachstate(&at, PTHREAD_CREATE_DETACHED);
        pthread_attr_setstacksize(&at, 16 * 1024 * 1024);
        pthread_t th;
        if (pthread_create(&th, &at, conn_thread, cn)) { close(fd); free(cn); }
        pthread_attr_destroy(&at);
    }
    close(listen_fd);
    return 0;
}

void http_request_restart(void) {
    G.restart_requested = 1;
    if (listen_fd >= 0) shutdown(listen_fd, SHUT_RDWR);
}

/* ================================================================ client */
static int parse_url(const char *url, char **host, int *port, char **path) {
    if (kf_strnicmp(url, "http://", 7)) return 0;
    const char *h = url + 7;
    const char *slash = strchr(h, '/');
    char *hp = slash ? kstrndup(h, slash - h) : kstrdup(h);
    char *at = strrchr(hp, '@');
    if (at) hp = at + 1;
    char *colon = strchr(hp, ':');
    *port = 80;
    if (colon) { *colon = 0; *port = atoi(colon + 1); }
    *host = hp;
    *path = kstrdup(slash ? slash : "/");
    return 1;
}

int http_client(const char *method, const char *url, Struct *hdrs, const char *body, size_t bodylen,
                int timeout_s, const char *proxy, int proxyport, const char *user, const char *pass,
                Buf *resp_body, int *status, char **status_line, Struct **resp_headers, char *err, size_t errlen) {
    char *host, *path; int port;
    if (!parse_url(url, &host, &port, &path)) {
        snprintf(err, errlen, "Only http:// URLs are supported (this is 1999: SSL requires the Netscape Enterprise Server).");
        return 0;
    }
    const char *chost = proxy && *proxy ? proxy : host;
    int cport = proxy && *proxy ? (proxyport ? proxyport : 80) : port;
    struct addrinfo hints = {0}, *res;
    hints.ai_socktype = SOCK_STREAM;
    char ps[16]; snprintf(ps, sizeof ps, "%d", cport);
    if (getaddrinfo(chost, ps, &hints, &res)) { snprintf(err, errlen, "Unknown host %s.", chost); return 0; }
    int fd = socket(res->ai_family, SOCK_STREAM | SOCK_CLOEXEC, 0);
    struct timeval tv = {timeout_s > 0 ? timeout_s : 60, 0};
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv);
    setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof tv);
    if (connect(fd, res->ai_addr, res->ai_addrlen)) {
        snprintf(err, errlen, "Connection Failure: unable to connect to %s:%d (%s).", chost, cport, strerror(errno));
        freeaddrinfo(res); close(fd); return 0;
    }
    freeaddrinfo(res);
    Buf rq; buf_init(&rq);
    buf_printf(&rq, "%s %s HTTP/1.0\r\nHost: %s\r\nUser-Agent: KoldFusion\r\nConnection: close\r\n",
               method, proxy && *proxy ? url : path, host);
    if (user && *user) {
        char *cred = kprintf("%s:%s", user, pass ? pass : "");
        buf_printf(&rq, "Authorization: Basic %s\r\n", base64_encode((unsigned char *)cred, strlen(cred)));
    }
    if (hdrs) for (int i = 0; i < hdrs->n; i++) buf_printf(&rq, "%s: %s\r\n", hdrs->e[i].key, v_tostr(hdrs->e[i].v));
    if (body) buf_printf(&rq, "Content-Length: %zu\r\n", bodylen);
    buf_puts(&rq, "\r\n");
    if (body) buf_put(&rq, body, bodylen);
    if (write_all(fd, rq.s, rq.len)) { snprintf(err, errlen, "Connection Failure: write error."); close(fd); return 0; }
    Buf r; buf_init(&r);
    char tmp[8192];
    ssize_t n;
    while ((n = recv(fd, tmp, sizeof tmp, 0)) > 0) buf_put(&r, tmp, (size_t)n);
    close(fd);
    if (n < 0 && !r.len) { snprintf(err, errlen, "Connection Timeout: no response from %s within %d seconds.", chost, timeout_s); return 0; }
    char *s = buf_cstr(&r);
    char *he = memmem(s, r.len, "\r\n\r\n", 4);
    size_t hl = he ? (size_t)(he - s) : r.len;
    char *hdrtext = kstrndup(s, hl);
    char *first = strtok(hdrtext, "\r\n");
    *status_line = kstrdup(first ? first : "");
    *status = first && strlen(first) > 9 ? atoi(first + 9) : 0;
    Struct *rh = struct_new();
    for (char *line = strtok(NULL, "\r\n"); line; line = strtok(NULL, "\r\n")) {
        char *colon = strchr(line, ':');
        if (!colon) continue;
        *colon = 0;
        struct_set(rh, kf_trim(line), v_str(kf_trim(colon + 1)));
    }
    *resp_headers = rh;
    const char *bstart = he ? he + 4 : s + r.len;
    size_t blen = r.len - (size_t)(bstart - s);
    Val *te = struct_get(rh, "Transfer-Encoding");
    if (te && kf_stristr(v_tostr(*te), "chunked")) {
        const char *p = bstart, *end = bstart + blen;
        while (p < end) {
            long cl = strtol(p, NULL, 16);
            const char *nl = memmem(p, end - p, "\r\n", 2);
            if (!nl || cl <= 0) break;
            p = nl + 2;
            if (p + cl > end) cl = end - p;
            buf_put(resp_body, p, (size_t)cl);
            p += cl + 2;
        }
    } else buf_put(resp_body, bstart, blen);
    return 1;
}

/* command line: kfserver --run /path/to/file.cfm [query-string] */
int kf_run_cli(const char *file, const char *query) {
    Arena *a = arena_new(); g_arena = a;
    HttpReq *req = kmalloc(sizeof(HttpReq));
    req->fd = 1;
    req->method = "GET";
    char rp[4096];
    const char *abs = realpath(file, rp) ? rp : file;
    const char *rel = abs;
    if (!strncmp(abs, G.webroot, strlen(G.webroot))) rel = abs + strlen(G.webroot);
    req->path = kstrdup(rel);
    req->uri = kstrdup(rel);
    req->query = query ? kstrdup(query) : NULL;
    req->version = "HTTP/1.0";
    req->headers = struct_new();
    req->remote_addr = "127.0.0.1";
    req->server_name = "localhost";
    req->server_port = G.port;
    sem_init(&req_sem, 0, 1);
    kf_handle_cfml(1, req, rel, abs);
    return 0;
}
