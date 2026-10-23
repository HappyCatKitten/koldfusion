/*
 * tags_io.c - tags that touch the outside world: CFFILE, CFDIRECTORY,
 * CFREGISTRY, CFHTTP, CFSCHEDULE, CFEXECUTE, CFMAIL, CFPOP, CFFTP and the
 * Windows-only tags that politely fail on a UNIX box.
 */
#define _GNU_SOURCE
#include "engine.h"
#include "netio.h"
#include <stdlib.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <fnmatch.h>
#include <dirent.h>
#include <signal.h>
#include <unistd.h>
#include <time.h>
#include <netdb.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/time.h>

#define TAG(nm) void tag_##nm(Ctx *c, Node *n, int *flow)

/* path-valued attributes accept C:\\ style paths */
static const char *pattr(Ctx *c, Node *n, const char *name, const char *def) {
    const char *v = attr_str(c, n, name, def);
    return v ? kf_native_path(v) : v;
}
static const char *preq(Ctx *c, Node *n, const char *name) { return kf_native_path(require_attr(c, n, name)); }

static void file_err(Ctx *c, const char *detail) {
    kf_throw(c, "Application", "Error processing CFFILE", detail);
}

static double mtime_date(time_t t) {
    struct tm tm; localtime_r(&t, &tm);
    return date_from_parts(tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec);
}

static int copy_file(const char *from, const char *to) {
    size_t len;
    char *d = kf_read_file(from, &len);
    if (!d) return 0;
    int ok = kf_write_file(to, d, len, 0);
    free(d);
    return ok;
}

static void set_mode(Ctx *c, Node *n, const char *path) {
    const char *mode = attr_str(c, n, "mode", NULL);
    if (mode && *mode) chmod(path, (mode_t)strtol(mode, NULL, 8));
}

/* ================================================================ CFFILE */
static void set_file_result(Ctx *c, Struct *r) {
    struct_set(c->variables, "CFFILE", v_struct(r));
    struct_set(c->variables, "File", v_struct(r));
}

static const char *ext_of(const char *f) { const char *d = strrchr(f, '.'); return d ? d + 1 : ""; }
static const char *base_of(const char *f) { const char *d = strrchr(f, '.'); return d ? kstrndup(f, d - f) : f; }

static void file_upload(Ctx *c, Node *n) {
    RState *rs = c->rs;
    const char *field = require_attr(c, n, "filefield");
    const char *dest = preq(c, n, "destination");
    const char *conflict = attr_str(c, n, "nameconflict", "error");
    const char *accept = attr_str(c, n, "accept", NULL);
    Val *info = rs->formfiles ? struct_get(rs->formfiles, field) : NULL;
    if (!info)
        file_err(c, kprintf("The form field %s did not contain a file.", kf_upper(field)));
    Struct *fi = info->u.st;
    const char *tmp = v_tostr(*struct_get(fi, "tmpfile"));
    const char *client = v_tostr(*struct_get(fi, "clientfile"));
    const char *ctype = v_tostr(*struct_get(fi, "contenttype"));
    double size = 0; v_tonum(*struct_get(fi, "size"), &size);
    const char *cf = strrchr(client, '\\'); if (!cf) cf = strrchr(client, '/');
    const char *clientfile = cf ? cf + 1 : client;
    if (accept && *accept) {
        int ok = 0;
        Array *a = list_to_array_k(accept, ",");
        for (int i = 0; i < a->n; i++) {
            const char *t = kf_trim(v_tostr(a->v[i]));
            if (!kf_stricmp(t, ctype)) ok = 1;
            size_t tl = strlen(t);
            if (tl > 2 && !strcmp(t + tl - 2, "/*") && !kf_strnicmp(t, ctype, tl - 1)) ok = 1;
        }
        if (!ok) file_err(c, kprintf("The MIME type of the uploaded file \"%s\" was not accepted by the server. "
                                     "Only files of type \"%s\" can be uploaded.", kf_html_escape(ctype), kf_html_escape(accept)));
    }
    struct stat st;
    char *dir, *fname;
    if (stat(dest, &st) == 0 && S_ISDIR(st.st_mode)) { dir = kstrdup(dest); fname = kstrdup(clientfile); }
    else { dir = (char *)kf_template_dir(dest); const char *s = strrchr(dest, '/'); fname = kstrdup(s ? s + 1 : dest); }
    char *target = kf_path_join(dir, fname);
    int existed = access(target, F_OK) == 0, overwritten = 0, renamed = 0, saved = 1;
    double oldsize = 0;
    if (existed) {
        stat(target, &st); oldsize = (double)st.st_size;
        if (!kf_stricmp(conflict, "error"))
            file_err(c, kprintf("File overwrite attempted. The file \"%s\" already exists on the server. Use NAMECONFLICT to "
                                "specify a different behavior.", kf_html_escape(target)));
        else if (!kf_stricmp(conflict, "skip")) saved = 0;
        else if (!kf_stricmp(conflict, "overwrite")) overwritten = 1;
        else if (!kf_stricmp(conflict, "makeunique")) {
            for (int i = 1; access(target, F_OK) == 0; i++) {
                fname = kprintf("%s%d.%s", base_of(clientfile), i, ext_of(clientfile));
                target = kf_path_join(dir, fname);
            }
            renamed = 1;
        }
    }
    if (saved && !copy_file(tmp, target)) file_err(c, kprintf("Unable to write the file \"%s\": %s", kf_html_escape(target), strerror(errno)));
    if (saved) set_mode(c, n, target);
    Struct *r = struct_new();
    const char *slash = strchr(ctype, '/');
    struct_set(r, "AttemptedServerFile", v_strdup(clientfile));
    struct_set(r, "ClientDirectory", v_str(cf ? kstrndup(client, cf - client) : ""));
    struct_set(r, "ClientFile", v_strdup(clientfile));
    struct_set(r, "ClientFileExt", v_strdup(ext_of(clientfile)));
    struct_set(r, "ClientFileName", v_strdup(base_of(clientfile)));
    struct_set(r, "ContentType", v_str(slash ? kstrndup(ctype, slash - ctype) : ctype));
    struct_set(r, "ContentSubType", v_str(slash ? kstrdup(slash + 1) : ""));
    struct_set(r, "FileExisted", v_bool(existed));
    struct_set(r, "FileSize", v_num(size));
    struct_set(r, "FileWasAppended", v_bool(0));
    struct_set(r, "FileWasOverwritten", v_bool(overwritten));
    struct_set(r, "FileWasRenamed", v_bool(renamed));
    struct_set(r, "FileWasSaved", v_bool(saved));
    struct_set(r, "OldFileSize", v_num(oldsize));
    struct_set(r, "ServerDirectory", v_strdup(dir));
    struct_set(r, "ServerFile", v_strdup(fname));
    struct_set(r, "ServerFileExt", v_strdup(ext_of(fname)));
    struct_set(r, "ServerFileName", v_strdup(base_of(fname)));
    struct_set(r, "TimeCreated", v_date(date_now()));
    struct_set(r, "TimeLastModified", v_date(date_now()));
    struct_set(r, "DateLastAccessed", v_date(date_now()));
    set_file_result(c, r);
}

TAG(file) {
    (void)flow;
    tag_security_check(c, "cffile");
    const char *action = require_attr(c, n, "action");
    if (!kf_stricmp(action, "upload")) { file_upload(c, n); return; }
    if (!kf_stricmp(action, "read") || !kf_stricmp(action, "readbinary")) {
        const char *f = preq(c, n, "file");
        const char *var = require_attr(c, n, "variable");
        size_t len;
        char *d = kf_read_file(f, &len);
        if (!d) file_err(c, kprintf("Error attempting to read '%s'. %s", kf_html_escape(f), strerror(errno)));
        char *copy = kstrndup(d, len);
        free(d);
        assign_path(c, var, !kf_stricmp(action, "read") ? v_strn(copy, len) : v_binary(copy, len));
        return;
    }
    if (!kf_stricmp(action, "write") || !kf_stricmp(action, "append")) {
        const char *f = preq(c, n, "file");
        int present;
        Val out = attr_val(c, n, "output", &present);
        if (!present) kf_throw(c, "Application", "Attribute validation error for tag CFFILE.", "The tag requires the attribute(s): OUTPUT.");
        int nl = attr_bool(c, n, "addnewline", 1);
        const char *s; size_t len;
        if (out.t == VT_BINARY) { s = out.u.str.s; len = out.u.str.len; nl = 0; }
        else { s = val_simple_str(c, out, NULL); len = strlen(s); }
        int app = !kf_stricmp(action, "append");
        if (!kf_write_file(f, s, len, app)) file_err(c, kprintf("Error attempting to write '%s'. %s", kf_html_escape(f), strerror(errno)));
        if (nl) kf_write_file(f, "\n", 1, 1);
        set_mode(c, n, f);
        return;
    }
    if (!kf_stricmp(action, "copy") || !kf_stricmp(action, "move") || !kf_stricmp(action, "rename")) {
        const char *src = preq(c, n, "source");
        const char *dst = preq(c, n, "destination");
        struct stat st;
        if (stat(src, &st)) file_err(c, kprintf("The value of the attribute SOURCE, which is currently \"%s\", is invalid. "
                                               "The file does not exist.", kf_html_escape(src)));
        char *target = (char *)dst;
        if (stat(dst, &st) == 0 && S_ISDIR(st.st_mode)) {
            const char *b = strrchr(src, '/');
            target = kf_path_join(dst, b ? b + 1 : src);
        }
        if (!kf_stricmp(action, "copy")) {
            if (!copy_file(src, target)) file_err(c, kprintf("Unable to copy \"%s\" to \"%s\": %s", src, target, strerror(errno)));
        } else if (rename(src, target)) {
            if (errno == EXDEV && copy_file(src, target)) unlink(src);
            else file_err(c, kprintf("Unable to %s \"%s\" to \"%s\": %s", kf_lower(action), src, target, strerror(errno)));
        }
        return;
    }
    if (!kf_stricmp(action, "delete")) {
        const char *f = preq(c, n, "file");
        if (unlink(f)) file_err(c, kprintf("Error attempting to delete '%s'. %s", kf_html_escape(f), strerror(errno)));
        return;
    }
    kf_throw(c, "Application", "Attribute validation error for tag CFFILE.",
             kprintf("The value of the attribute ACTION, which is currently \"%s\", is invalid. Valid values are "
                     "UPLOAD, MOVE, RENAME, COPY, DELETE, READ, READBINARY, WRITE and APPEND.", kf_html_escape(action)));
}

/* ================================================================ CFDIRECTORY */
static const char *g_sortspec;
static Query *g_sortq;
static int cmp_rows(const void *a, const void *b) {
    int ra = *(const int *)a, rb = *(const int *)b;
    Array *specs = list_to_array_k(g_sortspec, ",");
    for (int i = 0; i < specs->n; i++) {
        char *spec = kf_trim(v_tostr(specs->v[i]));
        char *sp = strchr(spec, ' ');
        int desc = 0;
        if (sp) { *sp = 0; desc = kf_stristr(sp + 1, "desc") != NULL; }
        int ci = query_col_index(g_sortq, spec);
        if (ci < 0) continue;
        int r = v_compare(query_get(g_sortq, ci, ra), query_get(g_sortq, ci, rb));
        if (r) return desc ? -r : r;
    }
    return ra - rb;
}

TAG(directory) {
    (void)flow;
    tag_security_check(c, "cfdirectory");
    const char *action = attr_str(c, n, "action", "list");
    const char *dir = preq(c, n, "directory");
    if (!kf_stricmp(action, "list")) {
        const char *name = require_attr(c, n, "name");
        const char *filter = attr_str(c, n, "filter", "");
        const char *sort = attr_str(c, n, "sort", NULL);
        const char *cols[] = {"Name", "Size", "Type", "DateLastModified", "Attributes", "Mode"};
        Query *q = query_new(6, cols);
        DIR *d = opendir(dir);
        if (!d) kf_throw(c, "Application", "Error processing CFDIRECTORY",
                         kprintf("The directory \"%s\" could not be read: %s", kf_html_escape(dir), strerror(errno)));
        struct dirent *de;
        while ((de = readdir(d))) {
            if (*filter && fnmatch(filter, de->d_name, FNM_CASEFOLD) && strcmp(de->d_name, ".") && strcmp(de->d_name, "..")) continue;
            if (*filter && (!strcmp(de->d_name, ".") || !strcmp(de->d_name, ".."))) continue;
            char *p = kf_path_join(dir, de->d_name);
            struct stat st;
            if (stat(p, &st)) continue;
            int r = query_add_row(q);
            query_set(q, 0, r, v_strdup(de->d_name));
            query_set(q, 1, r, v_num(S_ISDIR(st.st_mode) ? 0 : (double)st.st_size));
            query_set(q, 2, r, v_str(S_ISDIR(st.st_mode) ? "Dir" : "File"));
            query_set(q, 3, r, v_str(kf_dateformat(mtime_date(st.st_mtime), "mm/dd/yyyy") ?
                                     kprintf("%s %s", kf_dateformat(mtime_date(st.st_mtime), "mm/dd/yyyy"),
                                             kf_timeformat(mtime_date(st.st_mtime), "hh:mm tt")) : ""));
            query_set(q, 4, r, v_str(st.st_mode & S_IWUSR ? (de->d_name[0] == '.' && strlen(de->d_name) > 2 ? "H" : "") : "R"));
            query_set(q, 5, r, v_str(kprintf("%o", st.st_mode & 0777)));
        }
        closedir(d);
        /* sort: default by name like NT did */
        int *idx = kmalloc(sizeof(int) * (q->nrows ? q->nrows : 1));
        for (int i = 0; i < q->nrows; i++) idx[i] = i;
        g_sortspec = sort ? sort : "Name ASC"; g_sortq = q;
        qsort(idx, q->nrows, sizeof(int), cmp_rows);
        Query *sorted = query_new(6, cols);
        for (int i = 0; i < q->nrows; i++) {
            int r = query_add_row(sorted);
            for (int col = 0; col < 6; col++) query_set(sorted, col, r, query_get(q, col, idx[i]));
        }
        assign_path(c, name, v_query(sorted));
        return;
    }
    if (!kf_stricmp(action, "create")) {
        if (mkdir(dir, 0755)) kf_throw(c, "Application", "Error processing CFDIRECTORY",
                                       kprintf("Unable to create directory \"%s\": %s", kf_html_escape(dir), strerror(errno)));
        return;
    }
    if (!kf_stricmp(action, "delete")) {
        if (rmdir(dir)) kf_throw(c, "Application", "Error processing CFDIRECTORY",
                                 kprintf("Unable to delete directory \"%s\": %s", kf_html_escape(dir), strerror(errno)));
        return;
    }
    if (!kf_stricmp(action, "rename")) {
        const char *nd = preq(c, n, "newdirectory");
        char *target = nd[0] == '/' ? (char *)nd : kf_path_join(kf_template_dir(kf_path_join(dir, "..")), nd);
        if (strchr(nd, '/') == NULL) { char *parent = kstrdup(dir); size_t l = strlen(parent); while (l > 1 && parent[l - 1] == '/') parent[--l] = 0;
            char *s = strrchr(parent, '/'); if (s) s[1] = 0; target = kf_path_join(parent, nd); }
        if (rename(dir, target)) kf_throw(c, "Application", "Error processing CFDIRECTORY",
                                          kprintf("Unable to rename \"%s\": %s", kf_html_escape(dir), strerror(errno)));
        return;
    }
    kf_throw(c, "Application", "Attribute validation error for tag CFDIRECTORY.",
             "The value of the attribute ACTION must be one of LIST, CREATE, DELETE, RENAME.");
}

/* ================================================================ CFREGISTRY */
static char *map_branch(const char *b) {
    /* scripts written for ColdFusion poke at Allaire\ColdFusion; send them to our keys */
    char *r = kstrdup(b);
    for (char *p = r; *p; p++) if (*p == '/') *p = '\\';
    const char *pat = "SOFTWARE\\Allaire\\ColdFusion";
    const char *m = kf_stristr(r, pat);
    if (m) r = kprintf("%.*sSOFTWARE\\Gibson\\KoldFusion%s", (int)(m - r), r, m + strlen(pat));
    if (!kf_strnicmp(r, "HKLM\\", 5)) r = kprintf("HKEY_LOCAL_MACHINE\\%s", r + 5);
    return r;
}

TAG(registry) {
    (void)flow;
    tag_security_check(c, "cfregistry");
    const char *action = require_attr(c, n, "action");
    char *branch = map_branch(require_attr(c, n, "branch"));
    if (!kf_stricmp(action, "getall")) {
        const char *name = require_attr(c, n, "name");
        const char *type = attr_str(c, n, "type", "string");
        int any = !kf_stricmp(type, "any");
        Query *q = reg_list(branch, any || !kf_stricmp(type, "key"), any || !kf_stricmp(type, "string") || !kf_stricmp(type, "dword"));
        if (!any && kf_stricmp(type, "key")) {
            /* filter by value type */
            const char *cols[] = {"Entry", "Type", "Value"};
            Query *f = query_new(3, cols);
            for (int r = 0; r < q->nrows; r++) {
                if (kf_stricmp(v_tostr(query_get(q, 1, r)), type)) continue;
                int nr = query_add_row(f);
                for (int col = 0; col < 3; col++) query_set(f, col, nr, query_get(q, col, r));
            }
            q = f;
        }
        const char *sort = attr_str(c, n, "sort", NULL);
        if (sort) {
            int *idx = kmalloc(sizeof(int) * (q->nrows ? q->nrows : 1));
            for (int i = 0; i < q->nrows; i++) idx[i] = i;
            g_sortspec = sort; g_sortq = q;
            qsort(idx, q->nrows, sizeof(int), cmp_rows);
            const char *cols[] = {"Entry", "Type", "Value"};
            Query *s = query_new(3, cols);
            for (int i = 0; i < q->nrows; i++) {
                int nr = query_add_row(s);
                for (int col = 0; col < 3; col++) query_set(s, col, nr, query_get(q, col, idx[i]));
            }
            q = s;
        }
        assign_path(c, name, v_query(q));
        return;
    }
    if (!kf_stricmp(action, "get")) {
        const char *entry = require_attr(c, n, "entry");
        const char *var = require_attr(c, n, "variable");
        char *v = reg_get(branch, entry, NULL);
        assign_path(c, var, v_str(v ? v : ""));
        return;
    }
    if (!kf_stricmp(action, "set")) {
        const char *entry = require_attr(c, n, "entry");
        const char *type = attr_str(c, n, "type", "string");
        const char *value = attr_str(c, n, "value", "");
        if (!kf_stricmp(type, "key")) reg_set(kprintf("%s\\%s", branch, entry), NULL, NULL, 0);
        else reg_set(branch, entry, value, !kf_stricmp(type, "dword"));
        return;
    }
    if (!kf_stricmp(action, "delete")) {
        const char *entry = attr_str(c, n, "entry", NULL);
        if (entry) reg_delete_entry(branch, entry); else reg_delete_key(branch);
        return;
    }
    kf_throw(c, "Application", "Attribute validation error for tag CFREGISTRY.",
             "The value of the attribute ACTION must be one of GETALL, GET, SET, DELETE.");
}

/* ================================================================ CFHTTP */
static __thread Array *t_httpparams;
static __thread Struct *t_mailparams;
/* a CFHTTP/CFMAIL body that threw leaves these set: clear them before the thread serves another request */
void tags_io_thread_reset(void) { t_httpparams = NULL; t_mailparams = NULL; }

TAG(httpparam) {
    (void)flow;
    if (!t_httpparams) kf_throw(c, "Template", "Context validation error for tag CFHTTPPARAM.", "The tag must be nested inside a CFHTTP tag.");
    Struct *p = struct_new();
    struct_set(p, "type", v_strdup(require_attr(c, n, "type")));
    struct_set(p, "name", v_strdup(require_attr(c, n, "name")));
    struct_set(p, "value", v_strdup(attr_str(c, n, "value", "")));
    struct_set(p, "file", v_strdup(attr_str(c, n, "file", "")));
    array_push(t_httpparams, v_struct(p));
}

static Query *csv_to_query(const char *text, const char *columns, char delim, char qual, int first_is_header) {
    Array *rows = array_new();
    const char *p = text;
    while (*p) {
        Array *fields = array_new();
        Buf f; buf_init(&f);
        int inq = 0;
        for (;;) {
            char ch = *p;
            if (!ch) { array_push(fields, v_str(buf_cstr(&f))); break; }
            if (inq) {
                if (ch == qual) { if (p[1] == qual) { buf_putc(&f, qual); p += 2; continue; } inq = 0; p++; continue; }
                buf_putc(&f, ch); p++; continue;
            }
            if (ch == qual && f.len == 0) { inq = 1; p++; continue; }
            if (ch == delim) { array_push(fields, v_str(buf_cstr(&f))); buf_init(&f); p++; continue; }
            if (ch == '\r') { p++; continue; }
            if (ch == '\n') { array_push(fields, v_str(buf_cstr(&f))); p++; break; }
            buf_putc(&f, ch); p++;
        }
        if (fields->n == 1 && !*v_tostr(fields->v[0])) continue;
        array_push(rows, v_arr(fields));
    }
    Query *q = query_new(0, NULL);
    int start = 0;
    if (columns && *columns) {
        Array *cn = list_to_array_k(columns, ",");
        for (int i = 0; i < cn->n; i++) query_add_column(q, kf_trim(v_tostr(cn->v[i])));
        if (first_is_header) start = 1;
    } else if (rows->n) {
        Array *h = rows->v[0].u.a;
        for (int i = 0; i < h->n; i++) {
            char *nm = kf_trim(v_tostr(h->v[i]));
            if (!*nm) nm = kprintf("COLUMN_%d", i + 1);
            query_add_column(q, nm);
        }
        start = 1;
    }
    for (int r = start; r < rows->n; r++) {
        Array *f = rows->v[r].u.a;
        int row = query_add_row(q);
        for (int col = 0; col < q->ncols && col < f->n; col++) query_set(q, col, row, f->v[col]);
    }
    return q;
}

static char *resolve_urls(const char *html, const char *base) {
    /* make relative HREF/SRC/ACTION attributes absolute */
    size_t skip = !kf_strnicmp(base, "https://", 8) ? 8 : 7;
    char *host = kstrdup(base);
    char *slash = strchr(host + skip, '/');
    char *dir = kstrndup(base, strcspn(base, "?#"));
    if (slash) *slash = 0;
    char *ld = strrchr(dir + skip, '/'); if (ld) ld[1] = 0; else dir = kprintf("%s/", dir);
    Buf b; buf_init(&b);
    for (const char *p = html; *p; ) {
        const char *attrs[] = {"href=\"", "src=\"", "action=\"", "background=\"", NULL};
        int matched = 0;
        for (int i = 0; attrs[i]; i++) {
            size_t al = strlen(attrs[i]);
            if (!kf_strnicmp(p, attrs[i], al)) {
                buf_put(&b, p, al);
                p += al;
                if (kf_strnicmp(p, "http:", 5) && kf_strnicmp(p, "https:", 6) && kf_strnicmp(p, "mailto:", 7) && kf_strnicmp(p, "javascript:", 11) &&
                    kf_strnicmp(p, "ftp:", 4) && *p != '#') {
                    buf_puts(&b, *p == '/' ? host : dir);
                    if (*p == '/') {}
                }
                matched = 1;
                break;
            }
        }
        if (!matched) buf_putc(&b, *p++);
    }
    return buf_cstr(&b);
}

TAG(http) {
    const char *url = require_attr(c, n, "url");
    const char *method = attr_str(c, n, "method", "get");
    const char *user = attr_str(c, n, "username", NULL), *pass = attr_str(c, n, "password", NULL);
    const char *proxy = attr_str(c, n, "proxyserver", NULL);
    int proxyport = (int)attr_num(c, n, "proxyport", 80);
    int timeout = (int)attr_num(c, n, "timeout", 60);
    int port = (int)attr_num(c, n, "port", 0);
    int resolve = attr_bool(c, n, "resolveurl", 0);
    int throwerr = attr_bool(c, n, "throwonerror", 0);
    int redirect = attr_bool(c, n, "redirect", 1);
    /* KoldFusion extra: CHECKCERTIFICATE="No" skips verifying an https:// server's certificate */
    int verify = attr_str(c, n, "checkcertificate", NULL) ? attr_bool(c, n, "checkcertificate", 1) : -1;
    const char *useragent = attr_str(c, n, "useragent", NULL);
    Array *saved = t_httpparams;
    t_httpparams = array_new();
    exec_nodes(c, n->kids, n->nkids, flow);
    Array *params = t_httpparams;
    t_httpparams = saved;

    Struct *hdrs = struct_new();
    Buf body; buf_init(&body);
    Buf qs; buf_init(&qs);
    Buf cookies; buf_init(&cookies);
    int multipart = 0;
    for (int i = 0; i < params->n; i++) {
        Struct *p = params->v[i].u.st;
        if (!kf_stricmp(v_tostr(*struct_get(p, "type")), "file")) multipart = 1;
    }
    const char *boundary = "----------KoldFusionBoundary1999";
    for (int i = 0; i < params->n; i++) {
        Struct *p = params->v[i].u.st;
        const char *type = v_tostr(*struct_get(p, "type")), *name = v_tostr(*struct_get(p, "name"));
        const char *value = v_tostr(*struct_get(p, "value"));
        if (!kf_stricmp(type, "url")) { if (qs.len) buf_putc(&qs, '&'); buf_printf(&qs, "%s=%s", kf_urlencode(name), kf_urlencode(value)); }
        else if (!kf_stricmp(type, "cookie")) { if (cookies.len) buf_puts(&cookies, "; "); buf_printf(&cookies, "%s=%s", name, kf_urlencode(value)); }
        else if (!kf_stricmp(type, "cgi")) struct_set(hdrs, name, v_strdup(value));
        else if (!kf_stricmp(type, "formfield") || !kf_stricmp(type, "file")) {
            if (multipart) {
                buf_printf(&body, "--%s\r\n", boundary);
                if (!kf_stricmp(type, "file")) {
                    const char *fp = v_tostr(*struct_get(p, "file"));
                    size_t len; char *data = kf_read_file(fp, &len);
                    const char *bn = strrchr(fp, '/');
                    buf_printf(&body, "Content-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\nContent-Type: %s\r\n\r\n",
                               name, bn ? bn + 1 : fp, mime_type_for(fp));
                    if (data) { buf_put(&body, data, len); free(data); }
                    buf_puts(&body, "\r\n");
                } else buf_printf(&body, "Content-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n", name, value);
            } else {
                if (body.len) buf_putc(&body, '&');
                buf_printf(&body, "%s=%s", kf_urlencode(name), kf_urlencode(value));
            }
        }
    }
    if (multipart) buf_printf(&body, "--%s--\r\n", boundary);
    if (qs.len) url = kprintf("%s%c%s", url, strchr(url, '?') ? '&' : '?', buf_cstr(&qs));
    if (cookies.len) struct_set(hdrs, "Cookie", v_str(buf_cstr(&cookies)));
    int post = !kf_stricmp(method, "post");
    if (post) struct_set(hdrs, "Content-Type", v_str(multipart ? kprintf("multipart/form-data; boundary=%s", boundary)
                                                                : "application/x-www-form-urlencoded"));
    HttpClientOpts ho = {0};
    ho.method = post ? "POST" : "GET"; ho.url = url; ho.headers = hdrs;
    ho.body = post ? (body.s ? body.s : "") : NULL; ho.bodylen = post ? body.len : 0;
    ho.timeout_s = timeout; ho.port = port; ho.proxy = proxy; ho.proxyport = proxyport; ho.user = user; ho.pass = pass;
    ho.useragent = useragent; ho.follow_redirects = redirect; ho.verify = verify;
    HttpClientResult hr;
    char err[1024] = "";
    int ok = http_client_ex(&ho, &hr, err, sizeof err);
    Buf resp = hr.body;
    int status = hr.status; char *status_line = hr.status_line ? hr.status_line : ""; Struct *rh = hr.headers;
    if (ok && hr.final_url) url = hr.final_url;
    Struct *r = struct_new();
    if (!ok) {
        if (throwerr) kf_throw(c, "Application", "Error processing CFHTTP", err);
        struct_set(r, "FileContent", v_str("Connection Failure"));
        struct_set(r, "MimeType", v_str("Unable to determine MIME type of file."));
        struct_set(r, "Header", v_str(""));
        struct_set(r, "ResponseHeader", v_struct(struct_new()));
        struct_set(r, "StatusCode", v_str("Connection Failure. Status code unavailable."));
        struct_set(c->variables, "CFHTTP", v_struct(r));
        return;
    }
    if (throwerr && status >= 400) kf_throw(c, "Application", "Error processing CFHTTP", kprintf("The server returned %s.", status_line));
    if (throwerr && !redirect && status >= 300 && status < 400)
        kf_throw(c, "Application", "Error processing CFHTTP", kprintf("The server returned %s and REDIRECT is No.", status_line));
    char *content = kstrndup(resp.s ? resp.s : "", resp.len);
    Val *ct = struct_get(rh, "Content-Type");
    const char *mime = ct ? v_tostr(*ct) : "text/html";
    if (resolve && kf_stristr(mime, "text/html")) content = resolve_urls(content, url);
    struct_set(r, "FileContent", kf_stristr(mime, "text") || kf_stristr(mime, "xml") || !ct ? v_strn(content, resp.len) : v_binary(content, resp.len));
    if (kf_stristr(mime, "text") || !ct) struct_set(r, "FileContent", v_str(content));
    struct_set(r, "MimeType", v_str(kstrndup(mime, strcspn(mime, ";"))));
    Buf hb; buf_init(&hb);
    buf_printf(&hb, "%s ", status_line);
    for (int i = 0; i < rh->n; i++) {
        Val hv = rh->e[i].v;                /* a header sent more than once (Set-Cookie) is an array */
        if (hv.t == VT_ARRAY) { for (int k = 0; k < hv.u.a->n; k++) buf_printf(&hb, "%s: %s ", rh->e[i].key, v_tostr(hv.u.a->v[k])); }
        else buf_printf(&hb, "%s: %s ", rh->e[i].key, v_tostr(hv));
    }
    struct_set(r, "Header", v_str(buf_cstr(&hb)));
    struct_set(rh, "Explanation", v_strdup(strlen(status_line) > 13 ? status_line + 13 : ""));
    struct_set(rh, "Status_Code", v_num(status));
    struct_set(rh, "HTTP_Version", v_strdup(kstrndup(status_line, strcspn(status_line, " "))));
    struct_set(r, "ResponseHeader", v_struct(rh));
    struct_set(r, "StatusCode", v_strdup(strlen(status_line) > 9 ? status_line + 9 : status_line));
    struct_set(c->variables, "CFHTTP", v_struct(r));
    const char *path = pattr(c, n, "path", NULL);
    if (path) {
        const char *file = pattr(c, n, "file", NULL);
        if (!file) { const char *s = strrchr(url, '/'); file = s && s[1] ? s + 1 : "index.html"; }
        kf_write_file(kf_path_join(path, file), resp.s ? resp.s : "", resp.len, 0);
    }
    const char *qname = attr_str(c, n, "name", NULL);
    if (qname) {
        const char *delim = attr_str(c, n, "delimiter", ",");
        const char *tq = attr_str(c, n, "textqualifier", "\"");
        Query *q = csv_to_query(content, attr_str(c, n, "columns", NULL), *delim ? *delim : ',', *tq ? *tq : 0,
                                attr_bool(c, n, "firstrowasheaders", 1));
        assign_path(c, qname, v_query(q));
    }
}

/* ================================================================ CFSCHEDULE */
TAG(schedule) {
    (void)flow;
    const char *action = require_attr(c, n, "action");
    const char *task = require_attr(c, n, "task");
    char *key = cfg_key(kprintf("Schedule\\%s", task));
    if (!kf_stricmp(action, "delete")) {
        if (!reg_exists(key, NULL)) kf_throw(c, "Application", "Error processing CFSCHEDULE", kprintf("The task %s does not exist.", kf_html_escape(task)));
        reg_delete_key(key);
        kf_log("schedule.log", "Information", "Task %s deleted.", task);
        return;
    }
    if (!kf_stricmp(action, "run")) {
        char msg[512];
        if (!sched_run_task(task, msg, sizeof msg)) kf_throw(c, "Application", "Error processing CFSCHEDULE", msg);
        return;
    }
    if (kf_stricmp(action, "update"))
        kf_throw(c, "Application", "Attribute validation error for tag CFSCHEDULE.", "ACTION must be one of UPDATE, DELETE, RUN.");
    const char *fields[] = {"operation", "url", "startdate", "starttime", "enddate", "endtime", "interval", "requesttimeout",
                            "username", "password", "proxyserver", "publish", "path", "file", "resolveurl", NULL};
    const char *op = attr_str(c, n, "operation", "HTTPRequest");
    if (kf_stricmp(op, "httprequest"))
        kf_throw(c, "Application", "Attribute validation error for tag CFSCHEDULE.", "The only supported OPERATION is HTTPRequest.");
    require_attr(c, n, "url"); require_attr(c, n, "startdate"); require_attr(c, n, "starttime"); require_attr(c, n, "interval");
    reg_set(key, NULL, NULL, 0);
    for (int i = 0; fields[i]; i++) {
        const char *v = attr_str(c, n, fields[i], NULL);
        if (!v) { if (!reg_exists(key, fields[i])) reg_set(key, fields[i], "", 0); continue; }
        if (!strcmp(fields[i], "password")) v = kf_scramble(v);
        if (!strcmp(fields[i], "startdate") || !strcmp(fields[i], "enddate")) {
            double d;
            if (*v && date_parse(v, &d)) v = kf_dateformat(d, "mm/dd/yyyy");
        }
        if (!strcmp(fields[i], "starttime") || !strcmp(fields[i], "endtime")) {
            double d;
            if (*v && date_parse(kprintf("1/1/2000 %s", v), &d)) v = kf_timeformat(d, "HH:mm:ss");
        }
        reg_set(key, fields[i], v, 0);
    }
    reg_set(key, "LastRun", reg_get(key, "LastRun", ""), 0);
    kf_log("schedule.log", "Information", "Task %s updated.", task);
}

/* ================================================================ CFEXECUTE */
TAG(execute) {
    (void)flow;
    tag_security_check(c, "cfexecute");
    const char *name = require_attr(c, n, "name");
    const char *args = attr_str(c, n, "arguments", "");
    const char *outfile = pattr(c, n, "outputfile", NULL);
    double timeout = attr_num(c, n, "timeout", 0);
    Array *av = list_to_array_k(args, " ");
    char **argv = kmalloc(sizeof(char *) * (av->n + 2));
    argv[0] = (char *)name;
    for (int i = 0; i < av->n; i++) argv[i + 1] = (char *)v_tostr(av->v[i]);
    argv[av->n + 1] = NULL;
    int pfd[2];
    if (pipe(pfd)) kf_throw(c, "Application", "Error processing CFEXECUTE", strerror(errno));
    pid_t pid = fork();
    if (pid == 0) {
        dup2(pfd[1], 1); dup2(pfd[1], 2);
        close(pfd[0]); close(pfd[1]);
        execvp(name, argv);
        _exit(127);
    }
    close(pfd[1]);
    if (pid < 0) { close(pfd[0]); kf_throw(c, "Application", "Error processing CFEXECUTE", strerror(errno)); }
    if (timeout <= 0) {
        /* fire and forget: ColdFusion did not wait when TIMEOUT was 0 */
        close(pfd[0]);
        if (fork() == 0) { waitpid(pid, NULL, 0); _exit(0); }
        return;
    }
    Buf out; buf_init(&out);
    double deadline = kf_time_ms() + timeout * 1000;
    fcntl(pfd[0], F_SETFL, O_NONBLOCK);
    int status = 0, done = 0;
    char buf[4096];
    while (!done) {
        ssize_t r = read(pfd[0], buf, sizeof buf);
        if (r > 0) { buf_put(&out, buf, (size_t)r); continue; }
        if (r == 0) break;
        if (waitpid(pid, &status, WNOHANG) == pid) { done = 1; while ((r = read(pfd[0], buf, sizeof buf)) > 0) buf_put(&out, buf, (size_t)r); break; }
        if (kf_time_ms() > deadline) {
            kill(pid, SIGKILL); waitpid(pid, NULL, 0); close(pfd[0]);
            kf_throw(c, "Application", "Timeout period expired for CFEXECUTE.",
                     kprintf("The process %s did not finish within %s seconds.", kf_html_escape(name), fmt_number(timeout)));
        }
        usleep(10000);
    }
    close(pfd[0]);
    if (!done) waitpid(pid, &status, 0);
    if (outfile) kf_write_file(outfile, out.s ? out.s : "", out.len, 0);
    else out_put(c, out.s ? out.s : "", out.len);
}

/* ================================================================ CFMAIL */

TAG(mailparam) {
    (void)flow;
    if (!t_mailparams) kf_throw(c, "Template", "Context validation error for tag CFMAILPARAM.", "The tag must be nested inside a CFMAIL tag.");
    const char *file = pattr(c, n, "file", NULL);
    if (file) {
        Val *a = struct_get(t_mailparams, "attachments");
        array_push(a->u.a, v_strdup(file));
        return;
    }
    Val *h = struct_get(t_mailparams, "headers");
    struct_set(h->u.st, require_attr(c, n, "name"), v_strdup(attr_str(c, n, "value", "")));
}

static void send_one(Ctx *c, Node *n, int *flow) {
    RState *rs = c->rs;
    Struct *saved = t_mailparams;
    t_mailparams = struct_new();
    struct_set(t_mailparams, "headers", v_struct(struct_new()));
    struct_set(t_mailparams, "attachments", v_arr(array_new()));
    const char *mime = attr_str(c, n, "mimeattach", NULL);
    if (mime) array_push(struct_get(t_mailparams, "attachments")->u.a, v_strdup(mime));
    Buf body; buf_init(&body);
    Buf *sout = rs->out;
    int sio = c->in_output;
    rs->out = &body;
    c->in_output = 1;
    exec_nodes(c, n->kids, n->nkids, flow);
    rs->out = sout;
    c->in_output = sio;
    Struct *m = struct_new();
    struct_set(m, "to", v_strdup(require_attr(c, n, "to")));
    struct_set(m, "from", v_strdup(require_attr(c, n, "from")));
    struct_set(m, "subject", v_strdup(require_attr(c, n, "subject")));
    struct_set(m, "cc", v_strdup(attr_str(c, n, "cc", "")));
    struct_set(m, "bcc", v_strdup(attr_str(c, n, "bcc", "")));
    struct_set(m, "type", v_strdup(attr_str(c, n, "type", "text")));
    struct_set(m, "server", v_strdup(attr_str(c, n, "server", "")));
    struct_set(m, "port", v_strdup(attr_str(c, n, "port", "")));
    struct_set(m, "timeout", v_strdup(attr_str(c, n, "timeout", "")));
    struct_set(m, "mailerid", v_strdup(attr_str(c, n, "mailerid", "KoldFusion Application Server")));
    struct_set(m, "body", v_str(buf_cstr(&body)));
    struct_set(m, "headers", *struct_get(t_mailparams, "headers"));
    struct_set(m, "attachments", *struct_get(t_mailparams, "attachments"));
    t_mailparams = saved;
    char err[512];
    if (!mail_spool(m, err, sizeof err)) kf_throw(c, "Application", "Error processing CFMAIL", err);
}

TAG(mail) {
    Query *q = NULL;
    int present;
    Val qv = attr_val(c, n, "query", &present);
    if (present) {
        if (qv.t == VT_QUERY) q = qv.u.q;
        else { Val t; if (!resolve_path(c, v_tostr(qv), &t) || t.t != VT_QUERY)
                   kf_throw(c, "Application", "Attribute validation error for tag CFMAIL.", "QUERY must name a query.");
               q = t.u.q; }
    }
    if (!q) { send_one(c, n, flow); return; }
    int start = (int)attr_num(c, n, "startrow", 1) - 1, maxrows = (int)attr_num(c, n, "maxrows", -1);
    const char *group = attr_str(c, n, "group", NULL);
    int end = q->nrows;
    if (maxrows >= 0 && start + maxrows < end) end = start + maxrows;
    QLoop ql = { q, c->qloop };
    c->qloop = &ql;
    int saved_row = q->currentrow;
    for (int r = start < 0 ? 0 : start; r < end; ) {
        int gend = r + 1;
        if (group) {
            int ci = query_col_index(q, group);
            while (gend < end && ci >= 0 && !kf_stricmp(v_tostr(query_get(q, ci, r)), v_tostr(query_get(q, ci, gend)))) gend++;
        }
        q->currentrow = r + 1;
        Query *sg = c->grp_q; int ss = c->grp_start, se = c->grp_end, sa = c->grp_active;
        c->grp_q = q; c->grp_start = r; c->grp_end = gend; c->grp_active = group != NULL;
        send_one(c, n, flow);
        c->grp_q = sg; c->grp_start = ss; c->grp_end = se; c->grp_active = sa;
        r = gend;
    }
    q->currentrow = saved_row;
    c->qloop = ql.prev;
}

/* ================================================================ CFPOP */
static int pop_line(int fd, Buf *b) {
    char ch;
    buf_init(b);
    for (;;) {
        ssize_t r = recv(fd, &ch, 1, 0);
        if (r <= 0) return -1;
        if (ch == '\n') break;
        if (ch != '\r') buf_putc(b, ch);
    }
    buf_cstr(b);
    return 0;
}
static int pop_cmd(int fd, const char *cmd, Buf *resp) {
    if (cmd) { send(fd, cmd, strlen(cmd), MSG_NOSIGNAL); send(fd, "\r\n", 2, MSG_NOSIGNAL); }
    if (pop_line(fd, resp)) return 0;
    return !strncmp(resp->s, "+OK", 3);
}
static char *pop_multiline(int fd) {
    Buf all; buf_init(&all);
    Buf l;
    while (!pop_line(fd, &l)) {
        if (!strcmp(l.s, ".")) break;
        buf_puts(&all, l.s[0] == '.' ? l.s + 1 : l.s);
        buf_puts(&all, "\n");
    }
    return buf_cstr(&all);
}
static const char *hdr_field(const char *msg, const char *name) {
    size_t nl = strlen(name);
    const char *p = msg;
    while (*p && *p != '\n') {
        if (!kf_strnicmp(p, name, nl) && p[nl] == ':') {
            const char *v = p + nl + 1;
            while (*v == ' ') v++;
            return kstrndup(v, strcspn(v, "\n"));
        }
        p = strchr(p, '\n');
        if (!p) break;
        p++;
    }
    return "";
}

void mime_extract(const char *msg, const char *attach_dir, int unique, char **body, char **names, char **files);
TAG(pop) {
    (void)flow;
    const char *server = require_attr(c, n, "server");
    int port = (int)attr_num(c, n, "port", 110);
    const char *user = attr_str(c, n, "username", ""), *pass = attr_str(c, n, "password", "");
    const char *action = attr_str(c, n, "action", "getheaderonly");
    const char *name = attr_str(c, n, "name", NULL);
    int timeout = (int)attr_num(c, n, "timeout", 60);
    struct addrinfo hints = {0}, *res;
    hints.ai_socktype = SOCK_STREAM;
    char ps[16]; snprintf(ps, sizeof ps, "%d", port);
    if (getaddrinfo(server, ps, &hints, &res))
        kf_throw(c, "Application", "Error processing CFPOP", kprintf("Unknown host %s.", kf_html_escape(server)));
    int fd = socket(res->ai_family, SOCK_STREAM, 0);
    struct timeval tv = {timeout, 0};
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv);
    if (connect(fd, res->ai_addr, res->ai_addrlen)) {
        freeaddrinfo(res); close(fd);
        kf_throw(c, "Application", "Error processing CFPOP",
                 kprintf("Connection Failure: unable to connect to the POP3 server %s on port %d.", kf_html_escape(server), port));
    }
    freeaddrinfo(res);
    Buf r;
    if (!pop_cmd(fd, NULL, &r) || !pop_cmd(fd, kprintf("USER %s", user), &r) || !pop_cmd(fd, kprintf("PASS %s", pass), &r)) {
        close(fd);
        kf_throw(c, "Application", "Error processing CFPOP", kprintf("The POP3 server rejected the login: %s", kf_html_escape(r.s ? r.s : "")));
    }
    pop_cmd(fd, "STAT", &r);
    int count = atoi(r.s + 4);
    const char *msgnums = attr_str(c, n, "messagenumber", NULL);
    if (!kf_stricmp(action, "delete")) {
        Array *a = list_to_array_k(msgnums ? msgnums : "", ",");
        for (int i = 0; i < a->n; i++) pop_cmd(fd, kprintf("DELE %s", v_tostr(a->v[i])), &r);
        pop_cmd(fd, "QUIT", &r);
        close(fd);
        return;
    }
    int full = !kf_stricmp(action, "getall");
    const char *attach_dir = attr_str(c, n, "attachmentpath", NULL);
    struct stat ast;
    if (attach_dir && (stat((attach_dir = kf_native_path(attach_dir)), &ast) != 0 || !S_ISDIR(ast.st_mode))) {
        pop_cmd(fd, "QUIT", &r);
        close(fd);
        kf_throw(c, "Application", "Error processing CFPOP",
                 kprintf("The ATTACHMENTPATH directory %s does not exist.", kf_html_escape(attr_str(c, n, "attachmentpath", ""))));
    }
    const char *cols[] = {"Date", "From", "MessageNumber", "ReplyTo", "Subject", "CC", "To", "Body", "Header", "Attachments", "AttachmentFiles"};
    Query *q = query_new(full ? 11 : 9, cols);
    int start = (int)attr_num(c, n, "startrow", 1), maxrows = (int)attr_num(c, n, "maxrows", count);
    Array *which = msgnums ? list_to_array_k(msgnums, ",") : NULL;
    for (int i = start; i <= count && (which || i < start + maxrows); i++) {
        if (which) {
            int want = 0;
            for (int j = 0; j < which->n; j++) if (atoi(v_tostr(which->v[j])) == i) want = 1;
            if (!want) continue;
        }
        if (!pop_cmd(fd, full ? kprintf("RETR %d", i) : kprintf("TOP %d 0", i), &r)) continue;
        char *msg = pop_multiline(fd);
        char *sep = strstr(msg, "\n\n");
        char *hdrs = sep ? kstrndup(msg, sep - msg + 1) : msg;
        int row = query_add_row(q);
        query_set(q, 0, row, v_str(hdr_field(hdrs, "Date")));
        query_set(q, 1, row, v_str(hdr_field(hdrs, "From")));
        query_set(q, 2, row, v_num(i));
        query_set(q, 3, row, v_str(hdr_field(hdrs, "Reply-To")));
        query_set(q, 4, row, v_str(hdr_field(hdrs, "Subject")));
        query_set(q, 5, row, v_str(hdr_field(hdrs, "Cc")));
        query_set(q, 6, row, v_str(hdr_field(hdrs, "To")));
        if (full) {
            char *mbody, *anames, *afiles;          /* mime.c: text body + attachments saved to ATTACHMENTPATH */
            mime_extract(msg, attach_dir, attr_bool(c, n, "generateuniquefilenames", 0), &mbody, &anames, &afiles);
            query_set(q, 7, row, v_str(mbody));
            query_set(q, 8, row, v_str(hdrs));
            query_set(q, 9, row, v_str(anames));
            query_set(q, 10, row, v_str(afiles));
        } else query_set(q, 8, row, v_str(hdrs));
    }
    pop_cmd(fd, "QUIT", &r);
    close(fd);
    if (name) assign_path(c, name, v_query(q));
}

/* ================================================================ unsupported on UNIX */
/* CFLDAP lives in ldap.c */
/* CFOBJECT, CFSERVLET and CFSERVLETPARAM live in java.c / java_ext.c */
TAG(report) {
    (void)flow;
    kf_throw(c, "Application", "Error processing CFREPORT",
             kprintf("Crystal Reports are only supported on Windows NT. Unable to run %s.", kf_html_escape(attr_str(c, n, "report", ""))));
}
