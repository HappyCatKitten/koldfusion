/*
 * func_admin.c - undocumented KFUSION_* functions used by the Administrator
 * (ColdFusion 4.5's Administrator did the same with CFUSION_* functions).
 * They only work in templates under /CFIDE/administrator.
 */
#define _GNU_SOURCE
#include "engine.h"
#include "func.h"
#include "sql.h"
#include <stdlib.h>
#include <dirent.h>
#include <math.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/stat.h>

Query *template_cache_list(void);
void template_cache_flush(void);
int qcache_count(void);
void qcache_flush(void);
Query *active_requests(void);
void http_request_restart(void);
Query *tag_list_all(void);
void mail_spool_run_once(void);

static void admin_only(Ctx *c, Expr *call) {
    const char *p = c->rs->cur_tpl ? c->rs->cur_tpl->path : "";
    char *dir = kf_path_join(G.webroot, "CFIDE/administrator");
    if (strncmp(p, dir, strlen(dir)))
        kf_throw_at(c, call, "Security", kprintf("The function %s is reserved for the KoldFusion Administrator.", fn_name(call)),
                    "Undocumented KFUSION_ functions may only be called by templates in /CFIDE/administrator.");
}
#define ADMIN admin_only(c, call)

static Val result(int ok, const char *msg) {
    Struct *s = struct_new();
    struct_set(s, "OK", v_bool(ok));
    struct_set(s, "Message", v_strdup(msg));
    return v_struct(s);
}

F(kfusion_encrypt) { (void)argc; ADMIN; return v_str(kf_scramble(fa_str(c, call, argv, 0))); }
F(kfusion_decrypt) { (void)argc; ADMIN; return v_str(kf_unscramble(fa_str(c, call, argv, 0))); }
F(kfusion_checkpassword) {
    (void)argc; ADMIN;
    const char *which = argc > 1 ? fa_str(c, call, argv, 1) : "Admin";
    char *stored = cfg(REG_SERVER, kprintf("%sPassword", which), "");
    return v_bool(!strcmp(kf_unscramble(stored), fa_str(c, call, argv, 0)));
}
F(kfusion_setpassword) {
    (void)argc; ADMIN;
    cfg_set(REG_SERVER, kprintf("%sPassword", fa_str(c, call, argv, 0)), kf_scramble(fa_str(c, call, argv, 1)));
    return v_bool(1);
}
F(kfusion_verifydsn) {
    (void)argc; ADMIN;
    char msg[1024];
    int ok = dsn_verify(fa_str(c, call, argv, 0), msg, sizeof msg);
    return result(ok, msg);
}
F(kfusion_verifymail) {
    (void)argc; ADMIN;
    char msg[1024];
    int ok = smtp_verify(fa_str(c, call, argv, 0), fa_int(c, call, argv, 1), fa_int(c, call, argv, 2), msg, sizeof msg);
    return result(ok, msg);
}
F(kfusion_dsnlist) { (void)argc; (void)argv; ADMIN; return v_query(dsn_list()); }
F(kfusion_dbtables) {
    (void)argc; ADMIN;
    Dsn d; char err[1024]; Query *q;
    if (!dsn_lookup(fa_str(c, call, argv, 0), &d)) kf_throw_at(c, call, "Database", "Data source not found.", "");
    if (!sql_list_tables(d.path, &q, err, sizeof err)) kf_throw_at(c, call, "Database", err, "");
    return v_query(q);
}
F(kfusion_dbdescribe) {
    (void)argc; ADMIN;
    Dsn d; char err[1024]; Query *q;
    if (!dsn_lookup(fa_str(c, call, argv, 0), &d)) kf_throw_at(c, call, "Database", "Data source not found.", "");
    if (!sql_describe(d.path, fa_str(c, call, argv, 1), &q, err, sizeof err)) kf_throw_at(c, call, "Database", err, "");
    return v_query(q);
}
F(kfusion_dbcreate) {
    /* make sure a data source's database directory exists */
    (void)argc; ADMIN;
    Dsn d;
    if (!dsn_lookup(fa_str(c, call, argv, 0), &d)) return v_bool(0);
    return v_bool(kf_mkdirs(d.path));
}
F(kfusion_serverinfo) {
    (void)argc; (void)argv; ADMIN;
    Struct *s = struct_new();
    double up = (kf_time_ms() - G.started_ms) / 1000;
    struct_set(s, "UptimeSeconds", v_num(floor(up)));
    struct_set(s, "Uptime", v_str(kprintf("%d days, %d hours, %d minutes", (int)(up / 86400), (int)(up / 3600) % 24, (int)(up / 60) % 60)));
    struct_set(s, "StartedAt", v_date(G.started_at));
    struct_set(s, "Requests", v_num((double)G.requests_served));
    struct_set(s, "Active", v_num(G.active_requests));
    struct_set(s, "Queued", v_num(G.queued_requests));
    struct_set(s, "TimedOut", v_num(G.unresponsive));
    struct_set(s, "CachedQueries", v_num(qcache_count()));
    Query *tc = template_cache_list();
    double bytes = 0;
    for (int r = 0; r < tc->nrows; r++) { double d; v_tonum(query_get(tc, 1, r), &d); bytes += d; }
    struct_set(s, "CachedTemplates", v_num(tc->nrows));
    struct_set(s, "CachedTemplateBytes", v_num(bytes));
    struct_set(s, "Root", v_strdup(G.root));
    struct_set(s, "WebRoot", v_strdup(G.webroot));
    struct_set(s, "Port", v_num(G.port));
    struct_set(s, "Bind", v_strdup(G.bind));
    struct_set(s, "PID", v_num(getpid()));
    struct_set(s, "Executable", v_strdup(G.exe_path));
    return v_struct(s);
}
F(kfusion_activerequests) { (void)argc; (void)argv; ADMIN; return v_query(active_requests()); }
F(kfusion_sessions) { (void)argc; (void)argv; ADMIN; return v_query(session_stats()); }
F(kfusion_templatecache) { (void)argc; (void)argv; ADMIN; return v_query(template_cache_list()); }
F(kfusion_flushcache) {
    ADMIN;
    const char *what = argc ? fa_str(c, call, argv, 0) : "all";
    if (!kf_stricmp(what, "template") || !kf_stricmp(what, "all")) template_cache_flush();
    if (!kf_stricmp(what, "query") || !kf_stricmp(what, "all")) qcache_flush();
    if (!kf_stricmp(what, "sql") || !kf_stricmp(what, "all")) sql_cache_flush();
    return v_bool(1);
}
static void *delayed_restart(void *p) { (void)p; sleep(1); http_request_restart(); return NULL; }
F(kfusion_restart) {
    (void)argc; (void)argv; ADMIN;
    kf_log("server.log", "Information", "Restart requested from the KoldFusion Administrator.");
    pthread_t t;
    pthread_create(&t, NULL, delayed_restart, NULL);
    pthread_detach(t);
    return v_bool(1);
}
F(kfusion_taglist) { (void)argc; (void)argv; ADMIN; return v_query(tag_list_all()); }
F(kfusion_functionlist) { (void)argc; (void)argv; ADMIN; return v_query(func_list_all()); }
F(kfusion_veritylist) { (void)argc; (void)argv; ADMIN; return v_query(verity_list()); }
F(kfusion_verity) {
    ADMIN;
    const char *action = fa_str(c, call, argv, 0), *name = argc > 1 ? fa_str(c, call, argv, 1) : "";
    char err[1024] = "";
    int ok = 0;
    if (!kf_stricmp(action, "create")) ok = verity_create(name, argc > 2 ? fa_str(c, call, argv, 2) : "", argc > 3 ? fa_str(c, call, argv, 3) : "English", err, sizeof err);
    else if (!kf_stricmp(action, "delete")) ok = verity_delete(name, err, sizeof err);
    else if (!kf_stricmp(action, "purge")) ok = verity_purge(name, err, sizeof err);
    else if (!kf_stricmp(action, "optimize") || !kf_stricmp(action, "repair")) ok = verity_optimize(name, err, sizeof err);
    else if (!kf_stricmp(action, "index")) {
        long cnt = 0;
        ok = verity_index_path(name, argc > 2 ? fa_str(c, call, argv, 2) : "", argc > 3 ? fa_str(c, call, argv, 3) : "",
                               argc > 4 ? fa_bool(c, call, argv, 4) : 0, argc > 5 ? fa_str(c, call, argv, 5) : "", &cnt, err, sizeof err);
        if (ok) snprintf(err, sizeof err, "%ld documents were indexed in collection %s.", cnt, name);
    }
    if (ok && !*err) snprintf(err, sizeof err, "The %s operation on collection %s completed successfully.", kf_lower(action), name);
    return result(ok, err);
}
F(kfusion_runtask) {
    (void)argc; ADMIN;
    char msg[512];
    int ok = sched_run_task(fa_str(c, call, argv, 0), msg, sizeof msg);
    return result(ok, msg);
}
F(kfusion_spoollist) {
    (void)argc; ADMIN;
    const char *which = fa_str(c, call, argv, 0);
    char *dir = kprintf("%s/mail/%s", G.root, !kf_stricmp(which, "undelivr") ? "undelivr" : "spool");
    const char *cols[] = {"Name", "Size", "DateLastModified", "Path"};
    Query *q = query_new(4, cols);
    DIR *d = opendir(dir);
    struct dirent *de;
    while (d && (de = readdir(d))) {
        if (de->d_name[0] == '.') continue;
        char *p = kf_path_join(dir, de->d_name);
        struct stat st;
        if (stat(p, &st)) continue;
        struct tm tm; localtime_r(&st.st_mtime, &tm);
        int r = query_add_row(q);
        query_set(q, 0, r, v_strdup(de->d_name));
        query_set(q, 1, r, v_num((double)st.st_size));
        query_set(q, 2, r, v_date(date_from_parts(tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec)));
        query_set(q, 3, r, v_str(p));
    }
    if (d) closedir(d);
    return v_query(q);
}
F(kfusion_respool) {
    (void)argc; (void)argv; ADMIN;
    char *from = kprintf("%s/mail/undelivr", G.root), *to = kprintf("%s/mail/spool", G.root);
    DIR *d = opendir(from);
    struct dirent *de;
    int n = 0;
    while (d && (de = readdir(d))) {
        if (de->d_name[0] == '.') continue;
        if (!rename(kf_path_join(from, de->d_name), kf_path_join(to, de->d_name))) n++;
    }
    if (d) closedir(d);
    return v_num(n);
}
F(kfusion_spoolnow) { (void)argc; (void)argv; ADMIN; mail_spool_run_once(); return v_bool(1); }

/* KFUSION_CHECKSYNTAX(cfml [, name]) - used by /CFDOCS/cfmlsyntaxcheck; available everywhere */
F(kfusion_checksyntax) {
    const char *src = fa_str(c, call, argv, 0);
    const char *name = argc > 1 ? fa_str(c, call, argv, 1) : "(pasted code)";
    Arena *a = arena_new();
    char *copy = malloc(strlen(src) + 1);
    strcpy(copy, src);
    KfError *err = NULL;
    Template *t = template_parse(name, copy, strlen(copy), a, &err);
    Struct *r = struct_new();
    if (t) {
        struct_set(r, "OK", v_bool(1));
        struct_set(r, "Message", v_str("No syntax errors were found."));
        struct_set(r, "Line", v_num(0));
        struct_set(r, "Column", v_num(0));
    } else {
        struct_set(r, "OK", v_bool(0));
        struct_set(r, "Message", v_strdup(err ? err->message : "Unknown error"));
        struct_set(r, "Detail", v_strdup(err ? err->detail : ""));
        struct_set(r, "Line", v_num(err ? err->line : 0));
        struct_set(r, "Column", v_num(err ? err->col : 0));
    }
    if (!struct_get(r, "Detail")) struct_set(r, "Detail", v_str(""));
    free(copy);
    arena_free(a);
    return v_struct(r);
}

#define FN(name, mn, mx) {#name, fn_##name, mn, mx}
const FuncDef ADMIN_FUNCS[] = {
    FN(kfusion_encrypt,1,1), FN(kfusion_decrypt,1,1), FN(kfusion_checkpassword,1,2), FN(kfusion_setpassword,2,2),
    FN(kfusion_verifydsn,1,1), FN(kfusion_verifymail,3,3), FN(kfusion_dsnlist,0,0), FN(kfusion_dbtables,1,1),
    FN(kfusion_dbdescribe,2,2), FN(kfusion_dbcreate,1,1), FN(kfusion_serverinfo,0,0), FN(kfusion_activerequests,0,0),
    FN(kfusion_sessions,0,0), FN(kfusion_templatecache,0,0), FN(kfusion_flushcache,0,1), FN(kfusion_restart,0,0),
    FN(kfusion_taglist,0,0), FN(kfusion_functionlist,0,0), FN(kfusion_veritylist,0,0), FN(kfusion_verity,2,6),
    FN(kfusion_runtask,1,1), FN(kfusion_spoollist,1,1), FN(kfusion_respool,0,0), FN(kfusion_spoolnow,0,0), FN(kfusion_checksyntax,1,2),
    {NULL, NULL, 0, 0}
};
