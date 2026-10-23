/*
 * dsn.c - data sources. Every data source, whatever "driver" the
 * Administrator shows (Access, SQL Server, Oracle80, SQLOLEDB...), is served
 * by the built-in KoldFusion Flat-File Driver from <root>/db/<database>/.
 */
#define _GNU_SOURCE
#include "engine.h"
#include "sql.h"
#include <stdlib.h>
#include <sys/stat.h>

static const char *rget(const char *k, const char *e, const char *def) { return reg_get(k, e, def); }

int dsn_lookup(const char *name, Dsn *d) {
    memset(d, 0, sizeof *d);
    Query *q = reg_list(cfg_key("DataSources"), 1, 0);
    const char *real = NULL;
    for (int r = 0; r < q->nrows; r++) if (!kf_stricmp(v_tostr(query_get(q, 0, r)), name)) real = v_tostr(query_get(q, 0, r));
    if (!real) return 0;
    char *k = cfg_key(kprintf("DataSources\\%s", real));
    d->name = real;
    d->driver = rget(k, "Driver", "Microsoft Access Driver (*.mdb)");
    d->kind = rget(k, "Kind", "ODBC");
    d->description = rget(k, "Description", "");
    d->username = rget(k, "Username", "");
    d->password = kf_unscramble(rget(k, "Password", ""));
    d->login_timeout = atoi(rget(k, "LoginTimeout", "30"));
    d->maintain = atoi(rget(k, "MaintainConnections", "1"));
    d->disabled = atoi(rget(k, "Disabled", "0"));
    const char *restrict_ = rget(k, "Restrict", "");
    d->restrict_select = kf_stristr(restrict_, "SELECT") != NULL;
    d->restrict_insert = kf_stristr(restrict_, "INSERT") != NULL;
    d->restrict_update = kf_stristr(restrict_, "UPDATE") != NULL;
    d->restrict_delete = kf_stristr(restrict_, "DELETE") != NULL;
    d->restrict_sp = kf_stristr(restrict_, "SP") != NULL;
    const char *db = rget(k, "Database", real);
    if (db[0] == '/') d->path = db;
    else d->path = kf_path_join(kf_path_join(G.root, "db"), db);
    return 1;
}

Query *dsn_list(void) {
    const char *cols[] = {"Name", "Driver", "Kind", "Description", "Database"};
    Query *res = query_new(5, cols);
    Query *q = reg_list(cfg_key("DataSources"), 1, 0);
    for (int r = 0; r < q->nrows; r++) {
        const char *name = v_tostr(query_get(q, 0, r));
        char *k = cfg_key(kprintf("DataSources\\%s", name));
        int row = query_add_row(res);
        query_set(res, 0, row, v_strdup(name));
        query_set(res, 1, row, v_strdup(rget(k, "Driver", "")));
        query_set(res, 2, row, v_strdup(rget(k, "Kind", "ODBC")));
        query_set(res, 3, row, v_strdup(rget(k, "Description", "")));
        query_set(res, 4, row, v_strdup(rget(k, "Database", name)));
    }
    return res;
}

int dsn_verify(const char *name, char *msg, size_t msglen) {
    Dsn d;
    if (!dsn_lookup(name, &d)) { snprintf(msg, msglen, "Data source %s not found.", name); return 0; }
    if (d.disabled) { snprintf(msg, msglen, "Connections to data source %s have been disabled by the administrator.", name); return 0; }
    struct stat st;
    if (stat(d.path, &st) || !S_ISDIR(st.st_mode)) {
        snprintf(msg, msglen, "[Gibson][KoldFusion Flat-File Driver] Could not find database directory '%s'.", d.path);
        return 0;
    }
    Query *q;
    char err[512];
    if (!sql_list_tables(d.path, &q, err, sizeof err)) { snprintf(msg, msglen, "%s", err); return 0; }
    snprintf(msg, msglen, "The connection to the data source was verified successfully.");
    return 1;
}
