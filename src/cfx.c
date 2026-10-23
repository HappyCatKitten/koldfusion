/*
 * cfx.c - loading and calling CFX tags (shared libraries) via kfx.h
 */
#define _GNU_SOURCE
#include "engine.h"
#include "kfx.h"
#include <stdlib.h>
#include <dlfcn.h>
#include <pthread.h>

typedef struct QPriv { Query *q; const char *name; } QPriv;
typedef struct RPriv { Ctx *c; Node *n; Struct *attrs; const char *key; Buf debug; } RPriv;

static Ctx *RC(CFXRequest *r) { return ((RPriv *)r->priv)->c; }

static const char *q_name(CFXQuery *q) { return ((QPriv *)q->priv)->name; }
static int q_rows(CFXQuery *q) { return ((QPriv *)q->priv)->q->nrows; }
static int q_cols(CFXQuery *q) { return ((QPriv *)q->priv)->q->ncols; }
static const char *q_colname(CFXQuery *q, int col) {
    Query *qq = ((QPriv *)q->priv)->q;
    return col >= 1 && col <= qq->ncols ? qq->cols[col - 1] : "";
}
static int q_addrow(CFXQuery *q) { return query_add_row(((QPriv *)q->priv)->q) + 1; }
static void q_set(CFXQuery *q, int row, int col, const char *v) { query_set(((QPriv *)q->priv)->q, col - 1, row - 1, v_strdup(v)); }
static const char *q_get(CFXQuery *q, int row, int col) { return v_tostr(query_get(((QPriv *)q->priv)->q, col - 1, row - 1)); }

static CFXQuery *wrap_query(Query *qq, const char *name) {
    CFXQuery *q = kmalloc(sizeof(CFXQuery));
    QPriv *p = kmalloc(sizeof(QPriv));
    p->q = qq; p->name = name;
    q->priv = p;
    q->GetName = q_name; q->GetRowCount = q_rows; q->GetColumnCount = q_cols; q->GetColumnName = q_colname;
    q->AddRow = q_addrow; q->SetData = q_set; q->GetData = q_get;
    return q;
}

static int r_exists(CFXRequest *r, const char *name) { return struct_get(((RPriv *)r->priv)->attrs, name) != NULL; }
static const char *r_get(CFXRequest *r, const char *name) {
    Val *v = struct_get(((RPriv *)r->priv)->attrs, name);
    return v ? v_tostr(*v) : "";
}
static const char *r_list(CFXRequest *r) {
    Struct *s = ((RPriv *)r->priv)->attrs;
    Buf b; buf_init(&b);
    for (int i = 0; i < s->n; i++) { if (i) buf_putc(&b, ','); buf_puts(&b, kf_upper(s->e[i].key)); }
    return buf_cstr(&b);
}
static CFXQuery *r_query(CFXRequest *r) {
    Val *v = struct_get(((RPriv *)r->priv)->attrs, "query");
    if (!v) return NULL;
    Val qv;
    if (v->t == VT_QUERY) return wrap_query(v->u.q, "query");
    if (!resolve_path(RC(r), v_tostr(*v), &qv) || qv.t != VT_QUERY) return NULL;
    return wrap_query(qv.u.q, v_tostr(*v));
}
static const char *r_setting(CFXRequest *r, const char *name) { return reg_get(((RPriv *)r->priv)->key, name, ""); }
static void r_write(CFXRequest *r, const char *s) { out_puts(RC(r), s); }
static void r_setvar(CFXRequest *r, const char *name, const char *value) { assign_path(RC(r), name, v_strdup(value)); }
static CFXQuery *r_addquery(CFXRequest *r, const char *name, const char *columns) {
    Query *q = query_new(0, NULL);
    Array *a = list_to_array_k(columns, ",");
    for (int i = 0; i < a->n; i++) query_add_column(q, kf_trim(v_tostr(a->v[i])));
    assign_path(RC(r), name, v_query(q));
    return wrap_query(q, kstrdup(name));
}
static int r_debug(CFXRequest *r) { return struct_get(((RPriv *)r->priv)->attrs, "debug") != NULL; }
static void r_wdebug(CFXRequest *r, const char *s) { buf_puts(&((RPriv *)r->priv)->debug, s); }
static void r_throw(CFXRequest *r, const char *err, const char *diag) {
    kf_throw(RC(r), "Application", kprintf("An error occurred while processing %s: %s", kf_upper(((RPriv *)r->priv)->n->tag), err),
             diag ? diag : "");
}

typedef struct Lib { char *path; void *h; struct Lib *next; } Lib;
static Lib *libs;
static pthread_mutex_t mu = PTHREAD_MUTEX_INITIALIZER;

void cfx_call(Ctx *c, Node *n, const char *name) {
    char *uname = kf_upper(name);
    Query *tags = reg_list(cfg_key("CFX"), 1, 0);
    const char *real = NULL;
    for (int r = 0; r < tags->nrows; r++) if (!kf_stricmp(v_tostr(query_get(tags, 0, r)), uname)) real = v_tostr(query_get(tags, 0, r));
    if (!real)
        kf_throw(c, "Application", kprintf("The CFX custom tag \"%s\" was not found in the custom tag database.", uname),
                 "You must add custom tags to the database before using them. If you have added your tag to the database, "
                 "check the spelling of the tag within your template to ensure that it matches the database entry.");
    char *key = cfg_key(kprintf("CFX\\%s", real));
    const char *type = reg_get(key, "Type", "C++");
    if (!kf_stricmp(type, "java")) { java_cfx_call(c, n, uname, key); return; }    /* java_ext.c */
    const char *lib = reg_get(key, "LibraryPath", "");
    const char *proc = reg_get(key, "Procedure", "ProcessTagRequest");
    int keep = atoi(reg_get(key, "KeepLoaded", "1"));
    if (lib[0] != '/') lib = kf_path_join(kf_path_join(G.root, "cfx"), lib);
    pthread_mutex_lock(&mu);
    void *h = NULL;
    for (Lib *l = libs; l; l = l->next) if (!strcmp(l->path, lib)) h = l->h;
    if (!h) {
        h = dlopen(lib, RTLD_NOW | RTLD_LOCAL);
        if (h && keep) { Lib *l = calloc(1, sizeof(Lib)); l->path = strdup(lib); l->h = h; l->next = libs; libs = l; }
    }
    pthread_mutex_unlock(&mu);
    if (!h)
        kf_throw(c, "Application", kprintf("Error loading CFX library %s.", kf_html_escape(lib)), kf_html_escape(dlerror()));
    CFXProcessFn fn = (CFXProcessFn)dlsym(h, proc);
    if (!fn)
        kf_throw(c, "Application", kprintf("The CFX procedure %s was not found in %s.", proc, kf_html_escape(lib)), "");
    CFXRequest *r = kmalloc(sizeof(CFXRequest));
    RPriv *p = kmalloc(sizeof(RPriv));
    p->c = c; p->n = n; p->key = key;
    p->attrs = struct_new();
    for (int i = 0; i < n->nattrs; i++) struct_set(p->attrs, n->attrs[i].name, eval(c, n->attrs[i].val));
    buf_init(&p->debug);
    r->priv = p;
    r->AttributeExists = r_exists; r->GetAttribute = r_get; r->GetAttributeList = r_list; r->GetQuery = r_query;
    r->GetSetting = r_setting; r->Write = r_write; r->SetVariable = r_setvar; r->AddQuery = r_addquery;
    r->Debug = r_debug; r->WriteDebug = r_wdebug; r->ThrowException = r_throw;
    fn(r);
    if (p->debug.len) out_puts(c, kprintf("<PRE><B>Debug output (%s):</B>\n%s</PRE>", uname, kf_html_escape(buf_cstr(&p->debug))));
    if (!keep) dlclose(h);
}
