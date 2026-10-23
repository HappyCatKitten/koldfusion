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
    FN(kfusion_dbprocs,1,1),
    {NULL, NULL, 0, 0}
};
