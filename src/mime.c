/*
 * mime.c - just enough MIME for CFPOP ACTION="GetAll": find the readable
 * body of a (possibly multipart) message and save its attachments into
 * ATTACHMENTPATH, the way ColdFusion 4.5 filled the Body, Attachments and
 * AttachmentFiles columns.
 */
#define _GNU_SOURCE
#include "engine.h"
#include <ctype.h>
#include <sys/stat.h>

/* unfolded value of header `name` in a header block ("" if absent) */
static char *mh_get(const char *hdrs, const char *name) {
    size_t nl = strlen(name);
    const char *p = hdrs;
    while (p && *p) {
        if (!kf_strnicmp(p, name, nl) && p[nl] == ':') {
            Buf b; buf_init(&b);
            const char *v = p + nl + 1;
            for (;;) {
                const char *e = strchr(v, '\n');
                size_t l = e ? (size_t)(e - v) : strlen(v);
                buf_put(&b, v, l);
                if (!e || (e[1] != ' ' && e[1] != '\t')) break;
                buf_putc(&b, ' ');
                v = e + 1;
            }
            return kf_trim(buf_cstr(&b));
        }
        p = strchr(p, '\n');
        if (p) p++;
    }
    return "";
}

/* parameter of a header value: boundary="xyz"; filename=a.txt */
static char *mh_param(const char *val, const char *param) {
    size_t pl = strlen(param);
    for (const char *p = val; (p = kf_stristr(p, param)); p += pl) {
        if (p > val && p[-1] != ';' && p[-1] != ' ' && p[-1] != '\t') continue;
        const char *q = p + pl;
        while (*q == ' ') q++;
        if (*q != '=') continue;
        q++;
        while (*q == ' ') q++;
        if (*q == '"') { const char *e = strchr(q + 1, '"'); return kstrndup(q + 1, e ? (size_t)(e - q - 1) : strlen(q + 1)); }
        return kf_trim(kstrndup(q, strcspn(q, ";")));
    }
    return "";
}

static int hexv(int c) { return isdigit(c) ? c - '0' : isxdigit(c) ? (tolower(c) - 'a' + 10) : -1; }

static char *qp_decode(const char *s, size_t *outlen) {
    Buf b; buf_init(&b);
    for (const char *p = s; *p; p++) {
        if (*p == '=' && p[1] == '\n') { p++; continue; }               /* soft line break */
        if (*p == '=' && hexv((unsigned char)p[1]) >= 0 && hexv((unsigned char)p[2]) >= 0) {
            buf_putc(&b, (char)(hexv((unsigned char)p[1]) * 16 + hexv((unsigned char)p[2])));
            p += 2;
            continue;
        }
        buf_putc(&b, *p);
    }
    *outlen = b.len;
    return buf_cstr(&b);
}

static char *decode_part(const char *hdrs, const char *body, size_t *len) {
    const char *enc = mh_get(hdrs, "Content-Transfer-Encoding");
    if (!kf_stricmp(enc, "base64")) return (char *)base64_decode(body, len);
    if (!kf_stricmp(enc, "quoted-printable")) return qp_decode(body, len);
    *len = strlen(body);
    return (char *)body;
}

typedef struct MimeOut {
    const char *dir; int unique;
    char *text, *html;
    Buf names, files;
} MimeOut;

static char *safe_name(const char *fn) {
    const char *b = fn;
    for (const char *p = fn; *p; p++) if (*p == '/' || *p == '\\' || *p == ':') b = p + 1;
    char *r = kstrdup(*b && strcmp(b, ".") && strcmp(b, "..") ? b : "attachment");
    for (char *p = r; *p; p++) if ((unsigned char)*p < 32 || *p == '\t') *p = '_';
    return r;
}

static void save_attachment(MimeOut *mo, const char *fname, const char *data, size_t len) {
    if (mo->names.len) buf_putc(&mo->names, '\t');
    buf_puts(&mo->names, fname);
    if (!mo->dir || !*mo->dir) return;
    char *path = kf_path_join(mo->dir, fname);
    struct stat st;
    if (mo->unique) {
        const char *dot = strrchr(fname, '.');
        size_t stem = dot && dot != fname ? (size_t)(dot - fname) : strlen(fname);
        for (int i = 1; stat(path, &st) == 0 && i < 10000; i++)
            path = kf_path_join(mo->dir, kprintf("%.*s%d%s", (int)stem, fname, i, fname + stem));
    }
    if (!kf_write_file(path, data, len, 0)) return;
    if (mo->files.len) buf_putc(&mo->files, '\t');
    buf_puts(&mo->files, path);
}

static void walk_part(MimeOut *mo, const char *hdrs, const char *body, int depth) {
    const char *ctype = mh_get(hdrs, "Content-Type");
    if (depth < 8 && !kf_strnicmp(ctype, "multipart/", 10)) {
        char *bnd = mh_param(ctype, "boundary");
        if (!*bnd) { if (!mo->text) mo->text = (char *)body; return; }
        char *delim = kprintf("--%s", bnd);
        size_t dl = strlen(delim);
        const char *p = body;
        /* skip the preamble up to the first delimiter line */
        for (;;) {
            if (!strncmp(p, delim, dl)) break;
            p = strchr(p, '\n');
            if (!p) return;
            p++;
        }
        while (p && !strncmp(p, delim, dl) && strncmp(p + dl, "--", 2)) {
            const char *start = strchr(p, '\n');
            if (!start) break;
            start++;
            const char *q = start, *end = NULL;
            while (q && *q) {
                if (!strncmp(q, delim, dl)) { end = q; break; }
                q = strchr(q, '\n');
                if (q) q++;
            }
            size_t plen = end ? (size_t)(end - start) : strlen(start);
            char *part = kstrndup(start, plen);
            if (plen && part[plen - 1] == '\n') part[plen - 1] = 0;     /* the newline belongs to the delimiter */
            char *sep = strstr(part, "\n\n");
            char *ph = sep ? kstrndup(part, sep - part + 1) : (part[0] == '\n' ? "" : part);
            char *pb = sep ? sep + 2 : (part[0] == '\n' ? part + 1 : "");
            walk_part(mo, ph, pb, depth + 1);
            p = end;
        }
        return;
    }
    const char *disp = mh_get(hdrs, "Content-Disposition");
    char *fname = mh_param(disp, "filename");
    if (!*fname) fname = mh_param(ctype, "name");
    size_t len;
    char *data = decode_part(hdrs, body, &len);
    if (*fname || !kf_strnicmp(disp, "attachment", 10) ||
        (*ctype && kf_strnicmp(ctype, "text/", 5) && kf_strnicmp(ctype, "message/", 8))) {
        save_attachment(mo, safe_name(*fname ? fname : "attachment"), data, len);
        return;
    }
    if (!kf_strnicmp(ctype, "text/html", 9)) { if (!mo->html) mo->html = data; return; }
    if (!mo->text) mo->text = data;
}

/* msg: headers + "\n\n" + body with \n line ends */
void mime_extract(const char *msg, const char *attach_dir, int unique, char **body, char **names, char **files) {
    MimeOut mo; memset(&mo, 0, sizeof mo);
    mo.dir = attach_dir; mo.unique = unique;
    buf_init(&mo.names); buf_init(&mo.files);
    const char *sep = strstr(msg, "\n\n");
    char *hdrs = sep ? kstrndup(msg, sep - msg + 1) : (char *)msg;
    walk_part(&mo, hdrs, sep ? sep + 2 : "", 0);
    *body = mo.text ? mo.text : mo.html ? mo.html : "";
    *names = buf_cstr(&mo.names);
    *files = buf_cstr(&mo.files);
}
