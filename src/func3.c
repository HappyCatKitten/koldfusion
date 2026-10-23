/*
 * func3.c - GetHttpRequestData(), the Verity K2 Server functions and the
 * Administrator's KFUSION_DBPROCS(). Kept in their own table (searched by
 * func_lookup() in func2.c after the main one).
 */
#define _GNU_SOURCE
#include "engine.h"
#include "func.h"
#include "sql.h"
#include <ctype.h>
#include <stdlib.h>

/* ================================================================ GetHttpRequestData */
/* "user-agent" -> "User-Agent" (the request parser keeps names lower-cased) */
static char *header_case(const char *s) {
    char *r = kstrdup(s);
    int up = 1;
    for (char *p = r; *p; p++) {
        *p = (char)(up ? toupper((unsigned char)*p) : tolower((unsigned char)*p));
        up = *p == '-';
    }
    return r;
}

F(gethttprequestdata) {
    (void)argc; (void)argv; (void)call;
    HttpReq *req = c->rs->http;
    Struct *r = struct_new(), *h = struct_new();
    if (req && req->headers)
        for (int i = 0; i < req->headers->n; i++)
            struct_set(h, header_case(req->headers->e[i].key), req->headers->e[i].v);
    struct_set(r, "Headers", v_struct(h));
    const char *ct = req && req->content_type ? req->content_type : "";
    if (!req || !req->body || !req->bodylen) struct_set(r, "Content", v_str(""));
    else if (!kf_strnicmp(ct, "text/", 5) || !kf_strnicmp(ct, "application/x-www-form-urlencoded", 33) || !*ct)
        struct_set(r, "Content", v_strn(req->body, req->bodylen));
    else struct_set(r, "Content", v_binary(req->body, req->bodylen));   /* uploads etc.: binary object */
    struct_set(r, "Method", v_str(req && req->method ? req->method : "GET"));
    struct_set(r, "Protocol", v_str(req && req->version ? req->version : "HTTP/1.0"));
    return v_struct(r);
}

/* ================================================================ Verity K2 Server
 * KoldFusion's own Verity engine answers as the "K2 Server": every registered
 * collection is served, nothing is brokered, and the document limit is the one
 * set on the Administrator's Verity page (registry Verity\K2Server). */
#define K2KEY "Verity\\K2Server"

static double k2_doc_count(void) {
    Query *q = verity_list();
    double n = 0;
    for (int r = 0; r < q->nrows; r++) { double d; if (v_tonum(query_get(q, 3, r), &d)) n += d; }
    return n;
}
static double k2_limit(void) { return cfg_int(K2KEY, "DocCountLimit", 250000); }
static int k2_online(void) { return cfg_int(K2KEY, "Online", 1) != 0; }

F(getk2servercollections) {
    (void)argc; (void)argv; (void)call; (void)c;
    if (!k2_online()) return v_str("");
    Query *q = verity_list();
    Buf b; buf_init(&b);
    for (int r = 0; r < q->nrows; r++) { if (r) buf_putc(&b, ','); buf_puts(&b, v_tostr(query_get(q, 0, r))); }
    return v_str(buf_cstr(&b));
}
F(getk2serverdoccount) { (void)argc; (void)argv; (void)call; (void)c; return v_num(k2_online() ? k2_doc_count() : 0); }
F(getk2serverdoccountlimit) { (void)argc; (void)argv; (void)call; (void)c; return v_num(k2_limit()); }
F(isk2serverabroker) { (void)argc; (void)argv; (void)call; (void)c; return v_bool(0); }
F(isk2serverdoccountexceeded) { (void)argc; (void)argv; (void)call; (void)c; return v_bool(k2_online() && k2_doc_count() > k2_limit()); }
F(isk2serveronline) { (void)argc; (void)argv; (void)call; (void)c; return v_bool(k2_online()); }

/* ================================================================ structures (4.5.1 SP2)
 * StructFindKey / StructFindValue search nested structures and arrays depth
 * first; paths look like ".EMPLOYEES[2].NAME". StructSort returns the
 * top-level keys ordered by their values (or a sub-element of them). */
static int find_scope_all(Ctx *c, Expr *call, int argc, Val *argv) {
    if (argc < 3) return 0;
    const char *sc = fa_str(c, call, argv, 2);
    if (!kf_stricmp(sc, "all")) return 1;
    if (!kf_stricmp(sc, "one")) return 0;
    fn_param_error(c, call, 2, argv[2], "must be either \"one\" or \"all\"");
}

static int find_walk(Val node, const char *path, const char *want, int bykey, int all, Array *out, int depth) {
    if (depth > 64) return 0;
    if (node.t == VT_STRUCT) {
        Struct *st = node.u.st;
        for (int i = 0; i < st->n; i++) {
            const char *k = st->e[i].key;
            Val v = st->e[i].v;
            char *p = kprintf("%s.%s", path, kf_upper(k));
            int hit = bykey ? !kf_stricmp(k, want)
                            : (v_is_simple(v) && v.t != VT_NULL && !kf_stricmp(v_tostr(v), want));
            if (hit) {
                Struct *r = struct_new();
                if (bykey) struct_set(r, "Value", v);
                else struct_set(r, "Key", v_str(kf_upper(k)));
                struct_set(r, "Owner", node);
                struct_set(r, "Path", v_str(p));
                array_push(out, v_struct(r));
                if (!all) return 1;
            }
            if ((v.t == VT_STRUCT || v.t == VT_ARRAY) && find_walk(v, p, want, bykey, all, out, depth + 1) && !all) return 1;
        }
    } else if (node.t == VT_ARRAY) {
        Array *a = node.u.a;
        for (int i = 0; i < a->n; i++) {
            Val v = a->v[i];
            if ((v.t == VT_STRUCT || v.t == VT_ARRAY) &&
                find_walk(v, kprintf("%s[%d]", path, i + 1), want, bykey, all, out, depth + 1) && !all) return 1;
        }
    }
    return 0;
}

F(structfindkey) {
    Struct *st = fa_struct(c, call, argv, 0);
    const char *want = fa_str(c, call, argv, 1);
    Array *out = array_new();
    find_walk(v_struct(st), "", want, 1, find_scope_all(c, call, argc, argv), out, 0);
    return v_arr(out);
}
F(structfindvalue) {
    Struct *st = fa_struct(c, call, argv, 0);
    const char *want = fa_str(c, call, argv, 1);
    Array *out = array_new();
    find_walk(v_struct(st), "", want, 0, find_scope_all(c, call, argc, argv), out, 0);
    return v_arr(out);
}

typedef struct SortEnt { const char *key; Val v; double n; } SortEnt;
F(structsort) {
    Struct *st = fa_struct(c, call, argv, 0);
    const char *type = argc > 1 ? fa_str(c, call, argv, 1) : "text";
    const char *order = argc > 2 ? fa_str(c, call, argv, 2) : "asc";
    const char *sub = argc > 3 ? fa_str(c, call, argv, 3) : "";
    int numeric = !kf_stricmp(type, "numeric"), nocase = !kf_stricmp(type, "textnocase");
    if (!numeric && !nocase && kf_stricmp(type, "text"))
        fn_param_error(c, call, 1, argv[1], "must be one of \"numeric\", \"text\" or \"textnocase\"");
    int desc = !kf_stricmp(order, "desc");
    if (!desc && kf_stricmp(order, "asc")) fn_param_error(c, call, 2, argv[2], "must be either \"asc\" or \"desc\"");
    SortEnt *e = kmalloc(sizeof(SortEnt) * (st->n + 1));
    for (int i = 0; i < st->n; i++) {
        Val v = st->e[i].v;
        /* pathToSubElement: "price" or "info.price" below each top-level value */
        if (*sub) {
            Array *parts = list_to_array_k(sub, ".");
            for (int k = 0; k < parts->n; k++) {
                Val *nv = v.t == VT_STRUCT ? struct_get(v.u.st, v_tostr(parts->v[k])) : NULL;
                if (!nv) kf_throw_at(c, call, "Expression", "Error in StructSort.",
                                     kprintf("The element %s of key %s does not exist or is not a structure.", kf_upper(sub), kf_upper(st->e[i].key)));
                v = *nv;
            }
        }
        if (!v_is_simple(v))
            kf_throw_at(c, call, "Expression", "Error in StructSort.",
                        kprintf("The value of key %s is not a simple value and cannot be sorted.", kf_upper(st->e[i].key)));
        e[i].key = st->e[i].key; e[i].v = v;
        if (numeric && !v_tonum(v, &e[i].n))
            kf_throw_at(c, call, "Expression", "Error in StructSort.",
                        kprintf("The value of key %s, \"%s\", is not numeric.", kf_upper(st->e[i].key), v_tostr(v)));
    }
    for (int i = 1; i < st->n; i++) {                /* stable insertion sort */
        SortEnt x = e[i];
        int j = i - 1;
        for (; j >= 0; j--) {
            int cmp = numeric ? (e[j].n > x.n) - (e[j].n < x.n)
                    : nocase ? kf_stricmp(v_tostr(e[j].v), v_tostr(x.v)) : strcmp(v_tostr(e[j].v), v_tostr(x.v));
            if (desc ? cmp >= 0 : cmp <= 0) break;
            e[j + 1] = e[j];
        }
        e[j + 1] = x;
    }
    Array *out = array_new();
    for (int i = 0; i < st->n; i++) array_push(out, v_str(kf_upper(e[i].key)));
    return v_arr(out);
}

/* ================================================================ Administrator */
F(kfusion_dbprocs) {
    (void)argc;
    const char *p = c->rs->cur_tpl ? c->rs->cur_tpl->path : "";
    char *dir = kf_path_join(G.webroot, "CFIDE/administrator");
    if (strncmp(p, dir, strlen(dir)))
        kf_throw_at(c, call, "Security", "The function KFUSION_DBPROCS is reserved for the KoldFusion Administrator.",
                    "Undocumented KFUSION_ functions may only be called by templates in /CFIDE/administrator.");
    Dsn d; char err[1024]; Query *q;
    if (!dsn_lookup(fa_str(c, call, argv, 0), &d)) kf_throw_at(c, call, "Database", "Data source not found.", "");
    if (!sql_list_procedures(d.path, &q, err, sizeof err)) kf_throw_at(c, call, "Database", err, "");
    return v_query(q);
}

#define FN(name, mn, mx) {#name, fn_##name, mn, mx}
const FuncDef FUNCS3[] = {
    FN(gethttprequestdata,0,0),
    FN(getk2servercollections,0,0), FN(getk2serverdoccount,0,0), FN(getk2serverdoccountlimit,0,0),
    FN(isk2serverabroker,0,0), FN(isk2serverdoccountexceeded,0,0), FN(isk2serveronline,0,0),
    FN(structfindkey,2,3), FN(structfindvalue,2,3), FN(structsort,1,4),
    FN(kfusion_dbprocs,1,1),
    {NULL, NULL, 0, 0}
};
