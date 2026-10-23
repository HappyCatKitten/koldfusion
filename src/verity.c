/*
 * verity.c - a pocket-sized stand-in for the Verity SEARCH'97 engine that
 * ColdFusion 4.5 bundled: collections, CFCOLLECTION, CFINDEX, CFSEARCH.
 *
 * A collection is a directory holding one documents file. Searches scan the
 * collection, score by term frequency, and support the Verity "simple"
 * syntax: words (AND), commas (OR), "quoted phrases", NOT, and * ? wildcards.
 */
#define _GNU_SOURCE
#include "engine.h"
#include <stdlib.h>
#include <ctype.h>
#include <dirent.h>
#include <fnmatch.h>
#include <math.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/stat.h>

#define TAG(nm) void tag_##nm(Ctx *c, Node *n, int *flow)

static pthread_mutex_t vmu = PTHREAD_MUTEX_INITIALIZER;

typedef struct Doc { char *key, *title, *url, *c1, *c2, *body; } Doc;
typedef struct Coll { Doc *d; int n, cap; } Coll;

static char *coll_dir(const char *name) {
    char *path = cfg(kprintf("Verity\\Collections\\%s", name), "Path", NULL);
    if (!path) return NULL;
    return kf_path_join(path, name);
}

static void esc(Buf *b, const char *s) {
    for (; s && *s; s++) {
        if (*s == '\t') buf_puts(b, "\\t");
        else if (*s == '\n') buf_puts(b, "\\n");
        else if (*s == '\r') continue;
        else if (*s == '\\') buf_puts(b, "\\\\");
        else buf_putc(b, *s);
    }
}
static char *unesc(const char *s, size_t n) {
    Buf b; buf_init(&b);
    for (size_t i = 0; i < n; i++) {
        if (s[i] == '\\' && i + 1 < n) {
            char d = s[++i];
            buf_putc(&b, d == 't' ? '\t' : d == 'n' ? '\n' : d);
        } else buf_putc(&b, s[i]);
    }
    return buf_cstr(&b);
}

static void coll_add(Coll *cl, Doc d) {
    for (int i = 0; i < cl->n; i++) if (!strcmp(cl->d[i].key, d.key)) { cl->d[i] = d; return; }
    if (cl->n == cl->cap) {
        int nc = cl->cap ? cl->cap * 2 : 64;
        Doc *nd = kmalloc(sizeof(Doc) * nc);
        if (cl->n) memcpy(nd, cl->d, sizeof(Doc) * cl->n);
        cl->d = nd; cl->cap = nc;
    }
    cl->d[cl->n++] = d;
}

static int coll_load(const char *name, Coll *cl, char *err, size_t el) {
    memset(cl, 0, sizeof *cl);
    char *dir = coll_dir(name);
    if (!dir) { snprintf(err, el, "The collection %s does not exist. Use the KoldFusion Administrator to create it.", name); return 0; }
    size_t len;
    char *data = kf_read_file(kf_path_join(dir, "docs.kfv"), &len);
    if (!data) return 1;
    char *p = data;
    while (*p) {
        char *e = strchr(p, '\n');
        size_t ll = e ? (size_t)(e - p) : strlen(p);
        const char *f[6]; size_t fl[6]; int nf = 0;
        const char *s = p;
        for (size_t i = 0; i <= ll && nf < 6; i++) {
            if (i == ll || p[i] == '\t') { f[nf] = s; fl[nf] = (size_t)(p + i - s); nf++; s = p + i + 1; }
        }
        if (nf == 6) {
            Doc d = { unesc(f[0], fl[0]), unesc(f[1], fl[1]), unesc(f[2], fl[2]), unesc(f[3], fl[3]), unesc(f[4], fl[4]), unesc(f[5], fl[5]) };
            coll_add(cl, d);
        }
        if (!e) break;
        p = e + 1;
    }
    free(data);
    return 1;
}

static int coll_save(const char *name, Coll *cl) {
    char *dir = coll_dir(name);
    kf_mkdirs(dir);
    Buf b; buf_init(&b);
    for (int i = 0; i < cl->n; i++) {
        Doc *d = &cl->d[i];
        if (!d->key) continue;
        esc(&b, d->key); buf_putc(&b, '\t'); esc(&b, d->title); buf_putc(&b, '\t'); esc(&b, d->url); buf_putc(&b, '\t');
        esc(&b, d->c1); buf_putc(&b, '\t'); esc(&b, d->c2); buf_putc(&b, '\t'); esc(&b, d->body); buf_putc(&b, '\n');
    }
    char *tmp = kf_path_join(dir, "docs.kfv.tmp");
    if (!kf_write_file(tmp, b.s ? b.s : "", b.len, 0)) return 0;
    return rename(tmp, kf_path_join(dir, "docs.kfv")) == 0;
}

/* ---------------------------------------------------------------- admin ops */
int verity_create(const char *name, const char *path, const char *lang, char *err, size_t el) {
    if (!*name) { snprintf(err, el, "A collection name is required."); return 0; }
    for (const char *p = name; *p; p++) if (!isalnum((unsigned char)*p) && *p != '_' && *p != '-') {
        snprintf(err, el, "Collection names may contain only letters, digits, underscores and hyphens."); return 0; }
    if (cfg(kprintf("Verity\\Collections\\%s", name), "Path", NULL)) { snprintf(err, el, "The collection %s already exists.", name); return 0; }
    if (!path || !*path) path = kf_path_join(G.root, "verity/collections");
    if (!kf_mkdirs(kf_path_join(path, name))) { snprintf(err, el, "Unable to create the collection directory in %s.", path); return 0; }
    char *k = cfg_key(kprintf("Verity\\Collections\\%s", name));
    reg_set(k, "Path", path, 0);
    reg_set(k, "Language", lang && *lang ? lang : "English", 0);
    reg_set(k, "Created", date_odbc(date_now()), 0);
    kf_write_file(kf_path_join(kf_path_join(path, name), "docs.kfv"), "", 0, 0);
    return 1;
}

int verity_delete(const char *name, char *err, size_t el) {
    char *dir = coll_dir(name);
    if (!dir) { snprintf(err, el, "The collection %s does not exist.", name); return 0; }
    unlink(kf_path_join(dir, "docs.kfv"));
    rmdir(dir);
    reg_delete_key(cfg_key(kprintf("Verity\\Collections\\%s", name)));
    return 1;
}

int verity_purge(const char *name, char *err, size_t el) {
    char *dir = coll_dir(name);
    if (!dir) { snprintf(err, el, "The collection %s does not exist.", name); return 0; }
    pthread_mutex_lock(&vmu);
    kf_write_file(kf_path_join(dir, "docs.kfv"), "", 0, 0);
    pthread_mutex_unlock(&vmu);
    return 1;
}

int verity_optimize(const char *name, char *err, size_t el) {
    Coll cl;
    pthread_mutex_lock(&vmu);
    int ok = coll_load(name, &cl, err, el) && coll_save(name, &cl);
    pthread_mutex_unlock(&vmu);
    return ok;
}

Query *verity_list(void) {
    const char *cols[] = {"Name", "Path", "Language", "Documents", "Size", "Created"};
    Query *q = query_new(6, cols);
    Query *k = reg_list(cfg_key("Verity\\Collections"), 1, 0);
    for (int r = 0; r < k->nrows; r++) {
        const char *name = v_tostr(query_get(k, 0, r));
        char *ck = cfg_key(kprintf("Verity\\Collections\\%s", name));
        int row = query_add_row(q);
        query_set(q, 0, row, v_strdup(name));
        query_set(q, 1, row, v_strdup(reg_get(ck, "Path", "")));
        query_set(q, 2, row, v_strdup(reg_get(ck, "Language", "English")));
        Coll cl; char err[256];
        coll_load(name, &cl, err, sizeof err);
        query_set(q, 3, row, v_num(cl.n));
        struct stat st;
        query_set(q, 4, row, v_num(stat(kf_path_join(coll_dir(name), "docs.kfv"), &st) == 0 ? (double)st.st_size : 0));
        query_set(q, 5, row, v_strdup(reg_get(ck, "Created", "")));
    }
    return q;
}

/* ---------------------------------------------------------------- indexing */
static char *strip_html(const char *s, char **title) {
    Buf b; buf_init(&b);
    *title = NULL;
    const char *t = kf_stristr(s, "<title>");
    if (t) { t += 7; const char *e = kf_stristr(t, "</title>"); if (e) *title = kf_trim(kstrndup(t, e - t)); }
    int intag = 0, inscript = 0;
    for (const char *p = s; *p; p++) {
        if (*p == '<') {
            if (!kf_strnicmp(p, "<script", 7) || !kf_strnicmp(p, "<style", 6)) inscript = 1;
            if (!kf_strnicmp(p, "</script", 8) || !kf_strnicmp(p, "</style", 7)) inscript = 0;
            intag = 1; continue;
        }
        if (*p == '>' && intag) { intag = 0; buf_putc(&b, ' '); continue; }
        if (intag || inscript) continue;
        if (*p == '&') {
            if (!strncmp(p, "&nbsp;", 6)) { buf_putc(&b, ' '); p += 5; continue; }
            if (!strncmp(p, "&amp;", 5)) { buf_putc(&b, '&'); p += 4; continue; }
            if (!strncmp(p, "&lt;", 4)) { buf_putc(&b, '<'); p += 3; continue; }
            if (!strncmp(p, "&gt;", 4)) { buf_putc(&b, '>'); p += 3; continue; }
        }
        buf_putc(&b, isspace((unsigned char)*p) ? ' ' : *p);
    }
    /* collapse spaces */
    char *r = buf_cstr(&b), *o = r;
    int sp = 0;
    for (char *p = r; *p; p++) {
        if (*p == ' ') { if (!sp && o != r) *o++ = ' '; sp = 1; }
        else { *o++ = *p; sp = 0; }
    }
    *o = 0;
    return r;
}

static Doc file_doc(const char *path, const char *urlpath, const char *dirbase) {
    size_t len;
    char *data = kf_read_file(path, &len);
    Doc d = {0};
    d.key = kstrdup(path);
    char *title = NULL;
    d.body = data ? strip_html(kstrndup(data, len), &title) : kstrdup("");
    if (data) free(data);
    const char *bn = strrchr(path, '/');
    d.title = title && *title ? title : kstrdup(bn ? bn + 1 : path);
    const char *rel = dirbase && !strncmp(path, dirbase, strlen(dirbase)) ? path + strlen(dirbase) : (bn ? bn + 1 : path);
    while (*rel == '/') rel++;
    d.url = urlpath && *urlpath ? kf_path_join(urlpath, rel) : kstrdup("");
    d.c1 = kstrdup(""); d.c2 = kstrdup("");
    return d;
}

static int ext_match(const char *name, const char *exts) {
    Array *a = list_to_array_k(exts && *exts ? exts : ".htm,.html,.cfm,.cfml,.txt", ", ");
    const char *dot = strrchr(name, '.');
    for (int i = 0; i < a->n; i++) {
        const char *e = v_tostr(a->v[i]);
        if (!strcmp(e, "*.") && !dot) return 1;
        if (*e == '*') e++;
        if (dot && !kf_stricmp(dot, e)) return 1;
    }
    return 0;
}

static void walk(Coll *cl, const char *dir, const char *base, const char *exts, int recurse, const char *urlpath, long *count) {
    DIR *d = opendir(dir);
    if (!d) return;
    struct dirent *de;
    while ((de = readdir(d))) {
        if (de->d_name[0] == '.') continue;
        char *p = kf_path_join(dir, de->d_name);
        struct stat st;
        if (stat(p, &st)) continue;
        if (S_ISDIR(st.st_mode)) { if (recurse) walk(cl, p, base, exts, recurse, urlpath, count); continue; }
        if (!ext_match(de->d_name, exts)) continue;
        coll_add(cl, file_doc(p, urlpath, base));
        (*count)++;
    }
    closedir(d);
}

int verity_index_path(const char *collection, const char *dir, const char *exts, int recurse,
                      const char *urlpath, long *count, char *err, size_t el) {
    Coll cl;
    pthread_mutex_lock(&vmu);
    if (!coll_load(collection, &cl, err, el)) { pthread_mutex_unlock(&vmu); return 0; }
    *count = 0;
    walk(&cl, dir, dir, exts, recurse, urlpath, count);
    int ok = coll_save(collection, &cl);
    pthread_mutex_unlock(&vmu);
    if (!ok) snprintf(err, el, "Unable to write the collection %s.", collection);
    return ok;
}

int verity_update(const char *collection, const char *key, const char *title, const char *body,
                  const char *url, const char *custom1, const char *custom2, char *err, size_t el) {
    Coll cl;
    pthread_mutex_lock(&vmu);
    if (!coll_load(collection, &cl, err, el)) { pthread_mutex_unlock(&vmu); return 0; }
    Doc d = { kstrdup(key), kstrdup(title ? title : key), kstrdup(url ? url : ""), kstrdup(custom1 ? custom1 : ""),
              kstrdup(custom2 ? custom2 : ""), kstrdup(body ? body : "") };
    coll_add(&cl, d);
    int ok = coll_save(collection, &cl);
    pthread_mutex_unlock(&vmu);
    return ok;
}

int verity_remove(const char *collection, const char *key, char *err, size_t el) {
    Coll cl;
    pthread_mutex_lock(&vmu);
    if (!coll_load(collection, &cl, err, el)) { pthread_mutex_unlock(&vmu); return 0; }
    for (int i = 0; i < cl.n; i++) if (!strcmp(cl.d[i].key, key)) cl.d[i].key = NULL;
    int ok = coll_save(collection, &cl);
    pthread_mutex_unlock(&vmu);
    return ok;
}

/* ---------------------------------------------------------------- searching */
typedef struct Term { char *text; int phrase, neg, or_group; } Term;

static int parse_criteria(const char *crit, Term *terms, int max) {
    int n = 0, group = 0, neg = 0;
    const char *p = crit;
    while (*p && n < max) {
        while (isspace((unsigned char)*p)) p++;
        if (!*p) break;
        if (*p == ',') { group++; p++; continue; }
        if (*p == '"') {
            const char *e = strchr(p + 1, '"');
            size_t l = e ? (size_t)(e - p - 1) : strlen(p + 1);
            terms[n++] = (Term){ kf_lower(kstrndup(p + 1, l)), 1, neg, group };
            neg = 0;
            p += l + (e ? 2 : 1);
            continue;
        }
        const char *s = p;
        while (*p && !isspace((unsigned char)*p) && *p != ',' && *p != '"') p++;
        char *w = kstrndup(s, p - s);
        if (!kf_stricmp(w, "and")) continue;
        if (!kf_stricmp(w, "or")) { group++; continue; }
        if (!kf_stricmp(w, "not")) { neg = 1; continue; }
        /* explicit-syntax operators like <WORD> are ignored */
        if (*w == '<') continue;
        terms[n++] = (Term){ kf_lower(w), 0, neg, group };
        neg = 0;
    }
    return n;
}

static int count_hits(const char *hay, const char *term, int phrase) {
    int hits = 0;
    if (!phrase && (strchr(term, '*') || strchr(term, '?'))) {
        const char *p = hay;
        while (*p) {
            while (*p && !isalnum((unsigned char)*p)) p++;
            const char *s = p;
            while (*p && (isalnum((unsigned char)*p) || *p == '\'')) p++;
            if (p > s && !fnmatch(term, kstrndup(s, p - s), FNM_CASEFOLD)) hits++;
        }
        return hits;
    }
    size_t tl = strlen(term);
    for (const char *p = hay; (p = kf_stristr(p, term)); p += tl) {
        int startok = p == hay || !isalnum((unsigned char)p[-1]);
        int endok = !isalnum((unsigned char)p[tl]) || (!phrase && p[tl] == 's');   /* poor man's stemming */
        if (startok && endok) hits++;
    }
    return hits;
}

Query *verity_search(const char *collections, const char *criteria, int maxrows, int startrow, char *err, size_t el) {
    const char *cols[] = {"Key", "Title", "Score", "URL", "Custom1", "Custom2", "Summary", "RecordsSearched"};
    Query *q = query_new(8, cols);
    Term terms[64];
    int nt = parse_criteria(criteria ? criteria : "", terms, 64);
    Array *names = list_to_array_k(collections, ",");
    typedef struct Hit { Doc *d; double score; } Hit;
    Hit *hits = NULL; int nh = 0, ch = 0, searched = 0;
    for (int ci = 0; ci < names->n; ci++) {
        Coll cl;
        if (!coll_load(kf_trim(v_tostr(names->v[ci])), &cl, err, el)) return NULL;
        for (int i = 0; i < cl.n; i++) {
            Doc *d = &cl.d[i];
            searched++;
            double score = 0;
            int ok = nt > 0;
            /* groups are OR'ed; terms inside a group are AND'ed */
            int maxg = 0;
            for (int t = 0; t < nt; t++) if (terms[t].or_group > maxg) maxg = terms[t].or_group;
            int any_group = 0;
            for (int g = 0; g <= maxg; g++) {
                int gok = 1, gterms = 0; double gscore = 0;
                for (int t = 0; t < nt; t++) {
                    if (terms[t].or_group != g) continue;
                    gterms++;
                    int h = count_hits(d->body, terms[t].text, terms[t].phrase) + 3 * count_hits(d->title, terms[t].text, terms[t].phrase);
                    if (terms[t].neg) { if (h) gok = 0; }
                    else if (!h) gok = 0;
                    else gscore += h;
                }
                if (gterms && gok) { any_group = 1; score += gscore; }
            }
            ok = ok && any_group;
            if (!ok) continue;
            if (nh == ch) { ch = ch ? ch * 2 : 32; Hit *nhs = kmalloc(sizeof(Hit) * ch); if (nh) memcpy(nhs, hits, sizeof(Hit) * nh); hits = nhs; }
            double words = 1 + strlen(d->body) / 6.0;
            hits[nh].d = d; hits[nh].score = score / sqrt(words);
            nh++;
        }
    }
    /* sort by score */
    for (int i = 1; i < nh; i++) { Hit h = hits[i]; int j = i - 1; while (j >= 0 && hits[j].score < h.score) { hits[j + 1] = hits[j]; j--; } hits[j + 1] = h; }
    double top = nh ? hits[0].score : 1;
    if (startrow < 1) startrow = 1;
    for (int i = startrow - 1; i < nh && (maxrows < 0 || q->nrows < maxrows); i++) {
        Doc *d = hits[i].d;
        int r = query_add_row(q);
        query_set(q, 0, r, v_str(d->key));
        query_set(q, 1, r, v_str(d->title));
        query_set(q, 2, r, v_str(kprintf("%.4f", top > 0 ? hits[i].score / top * 0.98 : 0)));
        query_set(q, 3, r, v_str(d->url));
        query_set(q, 4, r, v_str(d->c1));
        query_set(q, 5, r, v_str(d->c2));
        size_t sl = strlen(d->body);
        query_set(q, 6, r, v_str(kstrndup(d->body, sl > 250 ? 250 : sl)));
        query_set(q, 7, r, v_num(searched));
    }
    return q;
}

/* ---------------------------------------------------------------- tags */
TAG(collection) {
    (void)flow;
    const char *action = require_attr(c, n, "action");
    const char *coll = require_attr(c, n, "collection");
    char err[512] = "";
    int ok = 1;
    if (!kf_stricmp(action, "create")) ok = verity_create(coll, attr_str(c, n, "path", NULL), attr_str(c, n, "language", "English"), err, sizeof err);
    else if (!kf_stricmp(action, "delete")) ok = verity_delete(coll, err, sizeof err);
    else if (!kf_stricmp(action, "optimize") || !kf_stricmp(action, "repair")) ok = verity_optimize(coll, err, sizeof err);
    else if (!kf_stricmp(action, "map")) {
        const char *path = require_attr(c, n, "path");
        char *k = cfg_key(kprintf("Verity\\Collections\\%s", coll));
        reg_set(k, "Path", path, 0);
        reg_set(k, "Language", attr_str(c, n, "language", "English"), 0);
        reg_set(k, "Created", date_odbc(date_now()), 0);
    } else kf_throw(c, "Application", "Attribute validation error for tag CFCOLLECTION.",
                    "ACTION must be one of CREATE, REPAIR, DELETE, OPTIMIZE, MAP.");
    if (!ok) kf_throw(c, "Application", "Error processing CFCOLLECTION", err);
}

TAG(index) {
    (void)flow;
    const char *coll = require_attr(c, n, "collection");
    const char *action = require_attr(c, n, "action");
    const char *type = attr_str(c, n, "type", "custom");
    char err[512] = "";
    int ok = 1;
    if (!kf_stricmp(action, "purge")) ok = verity_purge(coll, err, sizeof err);
    else if (!kf_stricmp(action, "optimize")) ok = verity_optimize(coll, err, sizeof err);
    else if (!kf_stricmp(action, "update") || !kf_stricmp(action, "refresh") || !kf_stricmp(action, "delete")) {
        if (!kf_stricmp(action, "refresh")) ok = verity_purge(coll, err, sizeof err);
        int del = !kf_stricmp(action, "delete");
        const char *key = attr_str(c, n, "key", NULL);
        Query *q = NULL;
        int present;
        Val qv = attr_val(c, n, "query", &present);
        if (present) {
            if (qv.t == VT_QUERY) q = qv.u.q;
            else { Val t; if (resolve_path(c, v_tostr(qv), &t) && t.t == VT_QUERY) q = t.u.q; }
            if (!q) kf_throw(c, "Application", "Attribute validation error for tag CFINDEX.", "QUERY must name a query.");
        }
        if (!kf_stricmp(type, "path") && del) {
            if (!key) kf_throw(c, "Application", "Attribute validation error for tag CFINDEX.", "KEY must be the directory to remove.");
            Coll cl;
            pthread_mutex_lock(&vmu);
            ok = coll_load(coll, &cl, err, sizeof err);
            size_t kl = strlen(key);
            if (ok) {
                for (int i = 0; i < cl.n; i++) if (cl.d[i].key && !strncmp(cl.d[i].key, key, kl)) cl.d[i].key = NULL;
                ok = coll_save(coll, &cl);
            }
            pthread_mutex_unlock(&vmu);
        } else if (!kf_stricmp(type, "path")) {
            long cnt = 0;
            if (!key) key = attr_str(c, n, "directory", NULL);
            if (!key) kf_throw(c, "Application", "Attribute validation error for tag CFINDEX.", "KEY must be the directory to index.");
            ok = ok && verity_index_path(coll, key, attr_str(c, n, "extensions", NULL), attr_bool(c, n, "recurse", 0),
                                         attr_str(c, n, "urlpath", ""), &cnt, err, sizeof err);
        } else if (!kf_stricmp(type, "file")) {
            if (!key) kf_throw(c, "Application", "Attribute validation error for tag CFINDEX.", "KEY must be the file to index.");
            if (del) ok = verity_remove(coll, key, err, sizeof err);
            else {
                Doc d = file_doc(key, attr_str(c, n, "urlpath", ""), NULL);
                ok = verity_update(coll, d.key, d.title, d.body, d.url, "", "", err, sizeof err);
            }
        } else if (q) {
            const char *title = attr_str(c, n, "title", NULL);
            Array *bodycols = list_to_array_k(attr_str(c, n, "body", ""), ",");
            const char *c1 = attr_str(c, n, "custom1", NULL), *c2 = attr_str(c, n, "custom2", NULL);
            for (int r = 0; r < q->nrows && ok; r++) {
#define COL(nm) (nm && query_col_index(q, nm) >= 0 ? v_tostr(query_get(q, query_col_index(q, nm), r)) : (nm ? nm : ""))
                const char *k = COL(key);
                if (del) { ok = verity_remove(coll, k, err, sizeof err); continue; }
                Buf b; buf_init(&b);
                for (int i = 0; i < bodycols->n; i++) { const char *bc = kf_trim(v_tostr(bodycols->v[i])); buf_puts(&b, COL(bc)); buf_putc(&b, ' '); }
                ok = verity_update(coll, k, title ? COL(title) : k, buf_cstr(&b), attr_str(c, n, "urlpath", ""),
                                   c1 ? COL(c1) : "", c2 ? COL(c2) : "", err, sizeof err);
#undef COL
            }
        } else {
            if (!key) kf_throw(c, "Application", "Attribute validation error for tag CFINDEX.", "KEY is required.");
            if (del) ok = verity_remove(coll, key, err, sizeof err);
            else ok = verity_update(coll, key, attr_str(c, n, "title", key), attr_str(c, n, "body", ""), attr_str(c, n, "urlpath", ""),
                                    attr_str(c, n, "custom1", ""), attr_str(c, n, "custom2", ""), err, sizeof err);
        }
    } else kf_throw(c, "Application", "Attribute validation error for tag CFINDEX.",
                    "ACTION must be one of UPDATE, DELETE, PURGE, REFRESH, OPTIMIZE.");
    if (!ok) kf_throw(c, "Application", "Error processing CFINDEX", err);
}

TAG(search) {
    (void)flow;
    const char *name = require_attr(c, n, "name");
    const char *coll = require_attr(c, n, "collection");
    const char *crit = attr_str(c, n, "criteria", "");
    char err[512] = "";
    Query *q = verity_search(coll, crit, (int)attr_num(c, n, "maxrows", -1), (int)attr_num(c, n, "startrow", 1), err, sizeof err);
    if (!q) kf_throw(c, "Application", "Error processing CFSEARCH", err);
    assign_path(c, name, v_query(q));
}
