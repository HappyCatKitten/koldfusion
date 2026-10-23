/*
 * tags_db.c - CFQUERY, CFQUERYPARAM, CFTRANSACTION, CFINSERT, CFUPDATE,
 * CFSTOREDPROC and the server-wide query cache.
 */
#define _GNU_SOURCE
#include "engine.h"
#include "sql.h"
#include <stdlib.h>
#include <ctype.h>
#include <math.h>
#include <pthread.h>
#include <errno.h>
#include <time.h>
#include <dirent.h>
#include <unistd.h>
#include <sys/stat.h>

#define TAG(nm) void tag_##nm(Ctx *c, Node *n, int *flow)

/* ================================================================ query cache */
typedef struct QCache {
    char *key;           /* dsn \x01 name \x01 sql */
    Arena *arena;
    Query *q;
    double created;      /* date_now() */
    struct QCache *next;
} QCache;
static QCache *qcache;
static int qcache_n;
static pthread_mutex_t qc_mu = PTHREAD_MUTEX_INITIALIZER;

static Query *qcache_get(const char *key, double max_age_days, double after) {
    Query *r = NULL;
    double now = date_now();
    pthread_mutex_lock(&qc_mu);
    for (QCache *e = qcache; e; e = e->next) {
        if (strcmp(e->key, key)) continue;
        if ((max_age_days > 0 && e->created + max_age_days >= now) || (after > 0 && e->created >= after)) r = query_copy(e->q);
        break;
    }
    pthread_mutex_unlock(&qc_mu);
    return r;
}

static void qcache_put(const char *key, Query *q) {
    int max = cfg_int(REG_SERVER, "MaxCachedQueries", 100);
    pthread_mutex_lock(&qc_mu);
    QCache **pp = &qcache;
    while (*pp) {
        if (!strcmp((*pp)->key, key)) { QCache *d = *pp; *pp = d->next; arena_free(d->arena); free(d->key); free(d); qcache_n--; break; }
        pp = &(*pp)->next;
    }
    QCache *e = calloc(1, sizeof(QCache));
    e->key = strdup(key);
    e->arena = arena_new();
    Arena *saved = g_arena; g_arena = e->arena;
    e->q = query_copy(q);
    g_arena = saved;
    e->created = date_now();
    e->next = qcache; qcache = e; qcache_n++;
    /* drop the oldest beyond the limit */
    while (qcache_n > max && qcache) {
        QCache **old = &qcache;
        while ((*old)->next) old = &(*old)->next;
        QCache *d = *old; *old = NULL;
        arena_free(d->arena); free(d->key); free(d); qcache_n--;
    }
    pthread_mutex_unlock(&qc_mu);
}

int qcache_count(void) { return qcache_n; }
void qcache_flush(void) {
    pthread_mutex_lock(&qc_mu);
    while (qcache) { QCache *d = qcache; qcache = d->next; arena_free(d->arena); free(d->key); free(d); }
    qcache_n = 0;
    pthread_mutex_unlock(&qc_mu);
}

/* ================================================================ errors */
static const char *sqlstate_for(const char *msg) {
    if (kf_stristr(msg, "not found") && kf_stristr(msg, "table")) return "S0002 (Base table not found)";
    if (kf_stristr(msg, "column") && (kf_stristr(msg, "not found") || kf_stristr(msg, "unknown"))) return "S0022 (Column not found)";
    if (kf_stristr(msg, "syntax")) return "37000 (Syntax error or access violation)";
    if (kf_stristr(msg, "already exists") || kf_stristr(msg, "already an object")) return "S0001 (Base table already exists)";
    if (kf_stristr(msg, "Wrong number of parameters") || kf_stristr(msg, "expects parameter") ||
        kf_stristr(msg, "too many arguments")) return "07001 (Wrong number of parameters)";
    if (kf_stristr(msg, "Could not find stored procedure") || kf_stristr(msg, "Must declare the variable"))
        return "37000 (Syntax error or access violation)";
    if (kf_stristr(msg, "type") || kf_stristr(msg, "mismatch")) return "22005 (Error in assignment)";
    return "S1000 (General error)";
}

static void throw_db(Ctx *c, const char *msg, const char *sql, const char *dsn) {
    KfError *e = kf_error_new("Database", msg, "");
    e->sqlstate = kstrdup(sqlstate_for(msg));
    e->nativecode = "0";
    e->sql = sql ? kstrdup(sql) : NULL;
    e->datasource = dsn ? kstrdup(dsn) : NULL;
    kf_throw_err(c->rs, e);
}

static int statement_kind(const char *sql) {
    while (isspace((unsigned char)*sql) || *sql == '(') sql++;
    if (!kf_strnicmp(sql, "select", 6)) return 1;
    if (!kf_strnicmp(sql, "insert", 6)) return 2;
    if (!kf_strnicmp(sql, "update", 6)) return 3;
    if (!kf_strnicmp(sql, "delete", 6)) return 4;
    if (!kf_strnicmp(sql, "exec", 4) || !kf_strnicmp(sql, "call", 4) || !kf_strnicmp(sql, "{call", 5)) return 5;
    return 0;
}

/* ---------------------------------------------------------------- transactions
 * The flat-file driver has no log, so CFTRANSACTION snapshots each data source's
 * tables the first time it is touched inside the transaction and restores them
 * on rollback. */
static int copy_tables(const char *from, const char *to, int clear_dest) {
    kf_mkdirs(to);
    if (clear_dest) {
        DIR *d = opendir(to);
        struct dirent *de;
        while (d && (de = readdir(d))) {
            size_t l = strlen(de->d_name);
            if (l > 4 && !strcmp(de->d_name + l - 4, ".tbl")) unlink(kf_path_join(to, de->d_name));
        }
        if (d) closedir(d);
    }
    DIR *d = opendir(from);
    if (!d) return 0;
    struct dirent *de;
    while ((de = readdir(d))) {
        size_t l = strlen(de->d_name);
        if (l <= 4 || strcmp(de->d_name + l - 4, ".tbl")) continue;
        size_t len;
        char *data = kf_read_file(kf_path_join(from, de->d_name), &len);
        if (data) { kf_write_file(kf_path_join(to, de->d_name), data, len, 0); free(data); }
    }
    closedir(d);
    return 1;
}

/* Like Access's file locking, one transaction at a time may hold a data source: a second page that wants to change it
 * waits (up to 10 seconds) for the first to commit or roll back. Without this, two rollbacks could each restore the
 * other's half-written snapshot. */
static pthread_mutex_t txn_mu = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t txn_cv = PTHREAD_COND_INITIALIZER;
#define TXN_MAX_HELD 64
static struct { char *dir; const RState *owner; } txn_held[TXN_MAX_HELD];

static int txn_acquire(const RState *rs, const char *dbdir) {
    struct timespec until;
    clock_gettime(CLOCK_REALTIME, &until);
    until.tv_sec += 10;
    pthread_mutex_lock(&txn_mu);
    for (;;) {
        int busy = 0, freeslot = -1;
        for (int i = 0; i < TXN_MAX_HELD; i++) {
            if (!txn_held[i].dir) { if (freeslot < 0) freeslot = i; continue; }
            if (!strcmp(txn_held[i].dir, dbdir) && txn_held[i].owner != rs) busy = 1;
        }
        if (!busy && freeslot >= 0) {
            txn_held[freeslot].dir = strdup(dbdir);
            txn_held[freeslot].owner = rs;
            pthread_mutex_unlock(&txn_mu);
            return 1;
        }
        if (pthread_cond_timedwait(&txn_cv, &txn_mu, &until) == ETIMEDOUT) {
            pthread_mutex_unlock(&txn_mu);
            return 0;
        }
    }
}

static void txn_release(const RState *rs, const char *dbdir) {
    pthread_mutex_lock(&txn_mu);
    for (int i = 0; i < TXN_MAX_HELD; i++)
        if (txn_held[i].dir && txn_held[i].owner == rs && !strcmp(txn_held[i].dir, dbdir)) {
            free(txn_held[i].dir);
            txn_held[i].dir = NULL;
            txn_held[i].owner = NULL;
        }
    pthread_cond_broadcast(&txn_cv);
    pthread_mutex_unlock(&txn_mu);
}

static void txn_touch(Ctx *c, const char *dbdir, const char *sql, const char *dsn) {
    RState *rs = c->rs;
    if (!rs->in_txn) return;
    if (!rs->txn) rs->txn = struct_new();
    if (struct_get(rs->txn, dbdir)) return;
    if (!txn_acquire(rs, dbdir))
        throw_db(c, "[Gibson][KoldFusion Flat-File Driver] Could not lock the data source; it is in use by another "
                    "user's transaction.", sql, dsn);
    static long seq;
    char *snap = kprintf("%s/temp/txn_%d_%ld", G.root, (int)getpid(), __sync_add_and_fetch(&seq, 1));
    sql_lock();
    copy_tables(dbdir, snap, 1);
    sql_unlock();
    struct_set(rs->txn, dbdir, v_strdup(snap));
}

static void txn_end(RState *rs, int rollback) {
    if (!rs->txn) return;
    for (int i = 0; i < rs->txn->n; i++) {
        const char *db = rs->txn->e[i].key, *snap = v_tostr(rs->txn->e[i].v);
        sql_lock();
        if (rollback) copy_tables(snap, db, 1);
        sql_unlock();
        copy_tables("/nonexistent", snap, 1);   /* clear the snapshot */
        rmdir(snap);
        if (rollback) sql_cache_flush();
        txn_release(rs, db);
    }
    struct_clear(rs->txn);
}

static Query *run_sql(Ctx *c, const char *dsn_name, const char *sql, const char *qname, long *affected) {
    Dsn d;
    if (!dsn_lookup(dsn_name, &d))
        throw_db(c, kprintf("Data source %s could not be found.", kf_upper(dsn_name)), sql, dsn_name);
    if (d.disabled)
        throw_db(c, kprintf("Connections to the data source %s have been disabled by the KoldFusion Administrator.", d.name), sql, d.name);
    int k = statement_kind(sql);
    if ((k == 1 && d.restrict_select) || (k == 2 && d.restrict_insert) || (k == 3 && d.restrict_update) ||
        (k == 4 && d.restrict_delete) || (k == 5 && d.restrict_sp))
        throw_db(c, kprintf("The SQL operation is restricted for data source %s.", d.name),
                 sql, d.name);
    char err[2048];
    Query *q = NULL;
    *affected = 0;
    if (k != 1) txn_touch(c, d.path, sql, d.name);
    double t0 = kf_time_ms();
    if (!sql_exec(d.path, sql, &q, affected, err, sizeof err)) throw_db(c, err, sql, d.name);
    double ms = kf_time_ms() - t0;
    if (q) {
        q->name = qname ? kstrdup(qname) : NULL;
        q->sql = kstrdup(sql);
        q->datasource = d.name;
        q->exectime_ms = ms;
    }
    RState *rs = c->rs;
    if (rs->show_query_info) {
        DebugQuery *dq = kmalloc(sizeof(DebugQuery));
        dq->name = qname; dq->datasource = d.name; dq->sql = kstrdup(sql); dq->ms = ms;
        dq->records = q ? q->nrows : 0;
        dq->template = rs->cur_tpl ? rs->cur_tpl->path : "";
        dq->next = rs->dq; rs->dq = dq;
    }
    return q;
}

/* ================================================================ CFQUERY */
TAG(query) {
    RState *rs = c->rs;
    const char *name = attr_str(c, n, "name", NULL);
    const char *dsn = attr_str(c, n, "datasource", NULL);
    const char *dbtype = attr_str(c, n, "dbtype", "odbc");
    if (!kf_stricmp(dbtype, "query"))
        kf_throw(c, "Application", "Attribute validation error for tag CFQUERY.",
                 "DBTYPE=\"query\" (query of queries) is not supported. It was introduced in ColdFusion 5.0; this is 4.5.");
    if (!dsn) {
        Val *def = struct_get(c->variables, "__kf_default_dsn");
        if (!def) kf_throw(c, "Application", "Attribute validation error for tag CFQUERY.",
                           "The tag requires the attribute(s): DATASOURCE.");
        dsn = v_tostr(*def);
    }
    int maxrows = (int)attr_num(c, n, "maxrows", -1);
    int present;
    Val cw = attr_val(c, n, "cachedwithin", &present);
    double cachedwithin = 0, cachedafter = 0;
    if (present) v_tonum(cw, &cachedwithin);
    Val ca = attr_val(c, n, "cachedafter", &present);
    if (present) v_todate(ca, &cachedafter);

    /* build the SQL text */
    Buf sqlbuf; buf_init(&sqlbuf);
    Buf *saved = rs->out;
    int saved_sql = c->sql_mode, saved_out = c->in_output;
    rs->out = &sqlbuf;
    c->sql_mode = 1;
    c->in_output = 1;
    exec_nodes(c, n->kids, n->nkids, flow);
    c->sql_mode = saved_sql;
    c->in_output = saved_out;
    rs->out = saved;
    char *sql = kf_trim(buf_cstr(&sqlbuf));

    Query *q = NULL;
    long affected = 0;
    char *key = NULL;
    if (cachedwithin > 0 || cachedafter > 0) {
        key = kprintf("%s\x01%s\x01%s", kf_upper(dsn), name ? kf_upper(name) : "", sql);
        q = qcache_get(key, cachedwithin, cachedafter);
        if (q) q->cached = 1;
    }
    if (!q) {
        q = run_sql(c, dsn, sql, name, &affected);
        if (q && key) qcache_put(key, q);
    } else if (rs->show_query_info) {
        DebugQuery *dq = kmalloc(sizeof(DebugQuery));
        dq->name = name; dq->datasource = dsn; dq->sql = kprintf("%s (cached)", sql); dq->ms = 0; dq->records = q->nrows;
        dq->next = rs->dq; rs->dq = dq;
    }
    if (q && maxrows >= 0 && q->nrows > maxrows) q->nrows = maxrows;
    Struct *cfq = struct_new();
    struct_set(cfq, "ExecutionTime", v_num(q ? floor(q->exectime_ms) : 0));
    struct_set(c->variables, "CFQUERY", v_struct(cfq));
    if (name && q) {
        q->currentrow = 0;
        assign_path(c, name, v_query(q));
    }
    *flow = FL_OK;
}

static const char *sqltype_class(const char *t) {
    /* 'n' numeric, 'd' date, 's' string, 'b' bit */
    if (!t) return "s";
    if (kf_stristr(t, "INTEGER") || kf_stristr(t, "INT") || kf_stristr(t, "NUMERIC") || kf_stristr(t, "DECIMAL") ||
        kf_stristr(t, "FLOAT") || kf_stristr(t, "DOUBLE") || kf_stristr(t, "REAL") || kf_stristr(t, "MONEY")) return "n";
    if (kf_stristr(t, "BIT")) return "b";
    if (kf_stristr(t, "DATE") || kf_stristr(t, "TIME")) return "d";
    return "s";
}

static void emit_param_value(Ctx *c, Buf *b, const char *val, const char *cls, const char *type, int maxlen, int scale) {
    if (*cls == 'n') {
        double d;
        if (!v_isnumeric_str(val, &d))
            kf_throw(c, "Database", kprintf("Invalid data '%s' for CFSQLTYPE '%s'.", kf_html_escape(val), kf_upper(type)), "");
        if (kf_stristr(type, "INT") && d != floor(d))
            kf_throw(c, "Database", kprintf("Invalid data '%s' for CFSQLTYPE '%s'.", kf_html_escape(val), kf_upper(type)), "");
        if (scale >= 0 && (kf_stristr(type, "NUMERIC") || kf_stristr(type, "DECIMAL"))) {   /* SCALE: decimal places */
            double p = pow(10, scale);
            d = (d < 0 ? -1 : 1) * floor(fabs(d) * p + 0.5) / p;
        }
        buf_puts(b, fmt_number(d));
        return;
    }
    if (*cls == 'b') {
        int bv;
        if (!v_tobool(v_str(val), &bv))
            kf_throw(c, "Database", kprintf("Invalid data '%s' for CFSQLTYPE '%s'.", kf_html_escape(val), kf_upper(type)), "");
        buf_puts(b, bv ? "1" : "0");
        return;
    }
    if (*cls == 'd') {
        double d;
        if (!date_parse(val, &d))
            kf_throw(c, "Database", kprintf("Invalid data '%s' for CFSQLTYPE '%s'.", kf_html_escape(val), kf_upper(type)), "");
        int y, mo, dd, h, mi, s;
        date_to_parts(d, &y, &mo, &dd, &h, &mi, &s);
        if (kf_stristr(type, "TIMESTAMP")) buf_printf(b, "{ts '%04d-%02d-%02d %02d:%02d:%02d'}", y, mo, dd, h, mi, s);
        else if (kf_stristr(type, "TIME") && !kf_stristr(type, "DATE")) buf_printf(b, "{t '%02d:%02d:%02d'}", h, mi, s);
        else buf_printf(b, "{d '%04d-%02d-%02d'}", y, mo, dd);
        return;
    }
    if (maxlen > 0 && (int)strlen(val) > maxlen)
        kf_throw(c, "Database", kprintf("Invalid data '%s' value exceeds MAXLENGTH setting '%d'.", kf_html_escape(val), maxlen), "");
    buf_putc(b, '\'');
    for (const char *p = val; *p; p++) { if (*p == '\'') buf_putc(b, '\''); buf_putc(b, *p); }
    buf_putc(b, '\'');
}

TAG(queryparam) {
    (void)flow;
    if (!c->sql_mode)
        kf_throw(c, "Template", "Context validation error for tag CFQUERYPARAM.", "The tag must be nested inside a CFQUERY tag.");
    Val v = attr_val(c, n, "value", NULL);
    const char *type = attr_str(c, n, "cfsqltype", "CF_SQL_CHAR");
    int maxlen = (int)attr_num(c, n, "maxlength", 0);
    int scale = (int)attr_num(c, n, "scale", -1);
    int isnull = attr_bool(c, n, "null", 0);
    int list = attr_bool(c, n, "list", 0);
    const char *sep = attr_str(c, n, "separator", ",");
    const char *cls = sqltype_class(type);
    Buf b; buf_init(&b);
    if (isnull) buf_puts(&b, "NULL");
    else if (list) {
        Array *a = list_to_array_k(val_simple_str(c, v, NULL), sep);
        for (int i = 0; i < a->n; i++) {
            if (i) buf_putc(&b, ',');
            emit_param_value(c, &b, v_tostr(a->v[i]), cls, type, maxlen, scale);
        }
    } else emit_param_value(c, &b, val_simple_str(c, v, NULL), cls, type, maxlen, scale);
    buf_put(c->rs->out, b.s ? b.s : "", b.len);
}

TAG(transaction) {
    RState *rs = c->rs;
    const char *action = attr_str(c, n, "action", "begin");
    const char *iso = attr_str(c, n, "isolation", NULL);      /* the flat-file driver is always SERIALIZABLE */
    if (iso && kf_stricmp(iso, "read_uncommitted") && kf_stricmp(iso, "read_committed") &&
        kf_stricmp(iso, "repeatable_read") && kf_stricmp(iso, "serializable") && kf_stricmp(iso, "versioning"))
        kf_throw(c, "Application", "Attribute validation error for tag CFTRANSACTION.",
                 kprintf("The value of the attribute ISOLATION, which is currently \"%s\", must be one of the values: "
                         "READ_UNCOMMITTED, READ_COMMITTED, REPEATABLE_READ, SERIALIZABLE.", kf_html_escape(iso)));
    if (kf_stricmp(action, "begin") && kf_stricmp(action, "commit") && kf_stricmp(action, "rollback"))
        kf_throw(c, "Application", "Attribute validation error for tag CFTRANSACTION.",
                 kprintf("The value of the attribute ACTION, which is currently \"%s\", must be one of the values: BEGIN, COMMIT, ROLLBACK.",
                         kf_html_escape(action)));
    if (!kf_stricmp(action, "commit") || !kf_stricmp(action, "rollback")) {
        if (!rs->in_txn)
            kf_throw(c, "Template", kprintf("CFTRANSACTION ACTION=\"%s\" must be nested inside a CFTRANSACTION block.", kf_upper(action)), "");
        txn_end(rs, !kf_stricmp(action, "rollback"));
        return;
    }
    if (rs->in_txn) { exec_nodes(c, n->kids, n->nkids, flow); return; }   /* nested: part of the outer one */
    rs->in_txn = 1;
    JmpFrame jf; jf.prev = rs->jf; rs->jf = &jf;
    if (setjmp(jf.jb) == 0) {
        exec_nodes(c, n->kids, n->nkids, flow);
        rs->jf = jf.prev;
        txn_end(rs, 0);
        rs->in_txn = 0;
        return;
    }
    rs->jf = jf.prev;
    KfError *e = rs->err;
    /* an error inside the transaction rolls it back; CFABORT/CFLOCATION commit */
    txn_end(rs, strcmp(e->type, "__abort") != 0);
    rs->in_txn = 0;
    kf_throw_err(rs, e);
}

/* ================================================================ CFINSERT / CFUPDATE */
static Query *describe(Ctx *c, const char *dsn, const char *table) {
    Dsn d;
    if (!dsn_lookup(dsn, &d)) throw_db(c, kprintf("Data source %s could not be found.", kf_upper(dsn)), NULL, dsn);
    Query *q;
    char err[1024];
    if (!sql_describe(d.path, table, &q, err, sizeof err)) throw_db(c, err, NULL, d.name);
    return q;
}

static Array *form_field_list(Ctx *c, Node *n) {
    const char *ff = attr_str(c, n, "formfields", NULL);
    if (!ff) {
        Val *fn = struct_get(c->rs->form, "FieldNames");
        ff = fn ? v_tostr(*fn) : "";
    }
    return list_to_array_k(ff, ",");
}

static void sql_literal(Buf *b, const char *val, const char *type) {
    const char *cls = sqltype_class(type);
    double d;
    if ((*cls == 'n' || *cls == 'b') && v_isnumeric_str(val, &d)) { buf_puts(b, fmt_number(d)); return; }
    if (*cls == 'n' && !*val) { buf_puts(b, "NULL"); return; }
    buf_putc(b, '\'');
    for (const char *p = val; *p; p++) { if (*p == '\'') buf_putc(b, '\''); buf_putc(b, *p); }
    buf_putc(b, '\'');
}

TAG(insert) {
    (void)flow;
    const char *dsn = require_attr(c, n, "datasource");
    const char *table = require_attr(c, n, "tablename");
    Query *cols = describe(c, dsn, table);
    Array *fields = form_field_list(c, n);
    Buf names, vals; buf_init(&names); buf_init(&vals);
    int cnt = 0;
    for (int i = 0; i < fields->n; i++) {
        const char *f = kf_trim(v_tostr(fields->v[i]));
        for (int r = 0; r < cols->nrows; r++) {
            const char *cn = v_tostr(query_get(cols, 0, r));
            if (kf_stricmp(cn, f)) continue;
            const char *type = v_tostr(query_get(cols, 1, r));
            if (kf_stristr(type, "COUNTER") || kf_stristr(type, "AUTO")) continue;
            Val *fv = struct_get(c->rs->form, f);
            if (!fv) continue;
            if (cnt++) { buf_puts(&names, ", "); buf_puts(&vals, ", "); }
            buf_puts(&names, cn);
            sql_literal(&vals, v_tostr(*fv), type);
        }
    }
    if (!cnt) kf_throw(c, "Database", "CFINSERT found no form fields that match columns of the table.",
                       kprintf("Table %s; form fields: %s", table, kf_html_escape(attr_str(c, n, "formfields", ""))));
    char *sql = kprintf("INSERT INTO %s (%s) VALUES (%s)", table, buf_cstr(&names), buf_cstr(&vals));
    long aff;
    run_sql(c, dsn, sql, "CFINSERT", &aff);
}

TAG(update) {
    (void)flow;
    const char *dsn = require_attr(c, n, "datasource");
    const char *table = require_attr(c, n, "tablename");
    Query *cols = describe(c, dsn, table);
    if (!cols->nrows) kf_throw(c, "Database", "Table has no columns.", "");
    /* the primary key is taken to be the first column (KoldFusion flat files have no catalog of keys) */
    const char *pk = v_tostr(query_get(cols, 0, 0));
    const char *pktype = v_tostr(query_get(cols, 1, 0));
    Val *pkv = struct_get(c->rs->form, pk);
    if (!pkv) kf_throw(c, "Database", kprintf("CFUPDATE requires the primary key field %s in the form.", kf_upper(pk)),
                       "The form must contain a field named after the table's primary key column.");
    Array *fields = form_field_list(c, n);
    Buf set; buf_init(&set);
    int cnt = 0;
    for (int i = 0; i < fields->n; i++) {
        const char *f = kf_trim(v_tostr(fields->v[i]));
        if (!kf_stricmp(f, pk)) continue;
        for (int r = 1; r < cols->nrows; r++) {
            const char *cn = v_tostr(query_get(cols, 0, r));
            if (kf_stricmp(cn, f)) continue;
            Val *fv = struct_get(c->rs->form, f);
            if (!fv) continue;
            if (cnt++) buf_puts(&set, ", ");
            buf_printf(&set, "%s = ", cn);
            sql_literal(&set, v_tostr(*fv), v_tostr(query_get(cols, 1, r)));
        }
    }
    if (!cnt) return;
    Buf where; buf_init(&where);
    sql_literal(&where, v_tostr(*pkv), pktype);
    char *sql = kprintf("UPDATE %s SET %s WHERE %s = %s", table, buf_cstr(&set), pk, buf_cstr(&where));
    long aff;
    run_sql(c, dsn, sql, "CFUPDATE", &aff);
}

/* ================================================================ CFSTOREDPROC
 * <CFSTOREDPROC PROCEDURE DATASOURCE ...> with nested <CFPROCPARAM> and
 * <CFPROCRESULT> tags. Like the ODBC driver of the day, the call is sent as
 * {? = call Proc(?, ?)} with the parameters bound by position (or by name
 * with DBVARNAME). */
typedef struct ProcParamInfo {
    const char *variable, *cfsqltype, *dbvarname, *type, *shown;
    int maxlength, scale, isnull;
} ProcParamInfo;

typedef struct ProcCall {
    SqlParam *p; ProcParamInfo *info; int np, cap;
    Array *results;              /* structs: name, resultset, maxrows */
} ProcCall;
static __thread ProcCall *t_proc;

static double num_or(Val *v, double def) {
    double d;
    return v && v_tonum(*v, &d) ? d : def;
}

static const char *CF_SQL_TYPES[] = {
    "CF_SQL_BIGINT", "CF_SQL_BIT", "CF_SQL_CHAR", "CF_SQL_DATE", "CF_SQL_DECIMAL", "CF_SQL_DOUBLE",
    "CF_SQL_FLOAT", "CF_SQL_IDSTAMP", "CF_SQL_INTEGER", "CF_SQL_LONGVARCHAR", "CF_SQL_MONEY", "CF_SQL_MONEY4",
    "CF_SQL_NUMERIC", "CF_SQL_REAL", "CF_SQL_REFCURSOR", "CF_SQL_SMALLINT", "CF_SQL_TIME", "CF_SQL_TIMESTAMP",
    "CF_SQL_TINYINT", "CF_SQL_VARCHAR", NULL
};

/* a CFPROCPARAM value converted the way the ODBC driver would bind it */
static Val proc_bind_value(Ctx *c, const char *val, const char *type, int maxlen) {
    const char *cls = sqltype_class(type);
    double d;
    if (*cls == 'n') {
        if (!v_isnumeric_str(kf_trim(val), &d) || (kf_stristr(type, "INT") && d != floor(d)))
            kf_throw(c, "Database", kprintf("Invalid data '%s' for CFSQLTYPE '%s'.", kf_html_escape(val), kf_upper(type)), "");
        return v_num(d);
    }
    if (*cls == 'b') {
        int bv;
        if (!v_tobool(v_str(val), &bv))
            kf_throw(c, "Database", kprintf("Invalid data '%s' for CFSQLTYPE '%s'.", kf_html_escape(val), kf_upper(type)), "");
        return v_num(bv ? 1 : 0);
    }
    if (*cls == 'd') {
        if (!date_parse(val, &d))
            kf_throw(c, "Database", kprintf("Invalid data '%s' for CFSQLTYPE '%s'.", kf_html_escape(val), kf_upper(type)), "");
        if (kf_stristr(type, "TIME") && !kf_stristr(type, "TIMESTAMP")) d -= floor(d);
        else if (!kf_stristr(type, "TIME")) d = floor(d);
        return v_date(d);
    }
    if (maxlen > 0 && (int)strlen(val) > maxlen)
        kf_throw(c, "Database", kprintf("Invalid data '%s' value exceeds MAXLENGTH setting '%d'.", kf_html_escape(val), maxlen),
                 kprintf("The value is %d characters long.", (int)strlen(val)));
    return v_strdup(val);
}

/* an OUT value as CF hands it back: NULL is an empty string, dates like query columns */
static Val proc_out_value(Val v, ProcParamInfo *pi) {
    if (v.t == VT_NULL) return v_str("");
    if (v.t == VT_DATE) {
        int y, mo, d, h, mi, s;
        date_to_parts(v.u.n, &y, &mo, &d, &h, &mi, &s);
        return v_str(kprintf("%04d-%02d-%02d %02d:%02d:%02d", y, mo, d, h, mi, s));
    }
    if (v.t == VT_NUM && pi->scale > 0) {
        double p = pow(10, pi->scale);
        return v_num(round(v.u.n * p) / p);
    }
    if (v.t == VT_STR && pi->maxlength > 0 && (int)v.u.str.len > pi->maxlength) return v_strn(v.u.str.s, pi->maxlength);
    return v;
}

TAG(storedproc) {
    RState *rs = c->rs;
    const char *proc = require_attr(c, n, "procedure");
    const char *dsn = attr_str(c, n, "datasource", NULL);
    if (!dsn) {
        Val *def = struct_get(c->variables, "__kf_default_dsn");
        if (!def) kf_throw(c, "Application", "Attribute validation error for tag CFSTOREDPROC.",
                           "The tag requires the attribute(s): DATASOURCE.");
        dsn = v_tostr(*def);
    }
    int retcode = attr_bool(c, n, "returncode", 0);
    int debug = attr_bool(c, n, "debug", 0);
    int present;
    Val bf = attr_val(c, n, "blockfactor", &present);
    double bfn;
    if (present && (!v_tonum(bf, &bfn) || bfn < 1 || bfn > 100 || bfn != floor(bfn)))
        kf_throw(c, "Application", "Attribute validation error for tag CFSTOREDPROC.",
                 kprintf("The value of the attribute BLOCKFACTOR, which is currently \"%s\", must be an integer between 1 and 100.",
                         kf_html_escape(val_simple_str(c, bf, NULL))));
    const char *dbtype = attr_str(c, n, "dbtype", "odbc");    /* every driver type reaches the same engine */
    static const char *DBTYPES[] = {"odbc", "oledb", "oracle73", "oracle80", "sybase11", "db2", "informix73", NULL};
    int okt = 0;
    for (int i = 0; DBTYPES[i]; i++) if (!kf_stricmp(DBTYPES[i], dbtype)) okt = 1;
    if (!okt)
        kf_throw(c, "Application", "Attribute validation error for tag CFSTOREDPROC.",
                 kprintf("The value of the attribute DBTYPE, which is currently \"%s\", must be one of the values: "
                         "ODBC, OLEDB, Oracle73, Oracle80, Sybase11, DB2, Informix73.", kf_html_escape(dbtype)));

    /* collect the CFPROCPARAM / CFPROCRESULT children */
    ProcCall pc; memset(&pc, 0, sizeof pc);
    pc.results = array_new();
    ProcCall *saved = t_proc;
    t_proc = &pc;
    JmpFrame jf; jf.prev = rs->jf; rs->jf = &jf;
    if (setjmp(jf.jb) != 0) {
        rs->jf = jf.prev;
        t_proc = saved;
        kf_throw_err(rs, rs->err);
    }
    exec_nodes(c, n->kids, n->nkids, flow);
    rs->jf = jf.prev;
    t_proc = saved;
    *flow = FL_OK;

    Dsn d;
    if (!dsn_lookup(dsn, &d)) throw_db(c, kprintf("Data source %s could not be found.", kf_upper(dsn)), NULL, dsn);
    Buf call; buf_init(&call);
    buf_printf(&call, "{%scall %s", retcode ? "? = " : "", proc);
    for (int i = 0; i < pc.np; i++) buf_puts(&call, i ? ", ?" : "(?");
    buf_puts(&call, pc.np ? ")}" : "}");
    const char *sqltext = buf_cstr(&call);
    if (d.disabled)
        throw_db(c, kprintf("Connections to the data source %s have been disabled by the KoldFusion Administrator.", d.name), sqltext, d.name);
    if (d.restrict_sp)
        throw_db(c, kprintf("The SQL operation is restricted for data source %s.", d.name), sqltext, d.name);

    txn_touch(c, d.path, sqltext, d.name);
    SqlProcResult res;
    char err[2048];
    double t0 = kf_time_ms();
    if (!sql_call_procedure(d.path, proc, pc.p, pc.np, &res, err, sizeof err)) throw_db(c, err, sqltext, d.name);
    double ms = kf_time_ms() - t0;

    /* CFPROCRESULT: result set n -> query */
    for (int i = 0; i < pc.results->n; i++) {
        Struct *r = pc.results->v[i].u.st;
        int set = (int)num_or(struct_get(r, "resultset"), 1);
        int maxrows = (int)num_or(struct_get(r, "maxrows"), -1);
        if (set < 1 || set > res.nsets) continue;          /* no such result set: the variable is not created */
        Query *q = query_copy(res.sets[set - 1]);
        if (maxrows >= 0 && q->nrows > maxrows) q->nrows = maxrows;
        q->name = kstrdup(v_tostr(*struct_get(r, "name")));
        q->sql = sqltext;
        q->datasource = d.name;
        q->exectime_ms = ms;
        q->currentrow = 0;
        assign_path(c, q->name, v_query(q));
    }
    /* CFPROCPARAM TYPE="OUT"/"INOUT": VARIABLE gets the value */
    for (int i = 0; i < pc.np; i++)
        if (pc.p[i].dir != SQL_PARAM_IN && pc.info[i].variable)
            assign_path(c, pc.info[i].variable, proc_out_value(pc.p[i].has_out ? pc.p[i].out : v_null(), &pc.info[i]));

    Struct *sp = struct_new();
    struct_set(sp, "ExecutionTime", v_num(floor(ms)));
    if (retcode) struct_set(sp, "StatusCode", v_num(res.status));
    struct_set(c->variables, "CFSTOREDPROC", v_struct(sp));

    if (rs->show_query_info || (debug && rs->show_debug)) {
        Buf dbg; buf_init(&dbg);
        buf_puts(&dbg, sqltext);
        for (int i = 0; i < pc.np; i++) {
            ProcParamInfo *pi = &pc.info[i];
            buf_printf(&dbg, "\n(param %d) = [type='%s', class='%s', value='%s'%s%s]", i + 1, pi->type, pi->cfsqltype,
                       pc.p[i].dir == SQL_PARAM_OUT ? "" : pi->isnull ? "[NULL]" : pi->shown,
                       pi->dbvarname ? kprintf(", dbvarname='%s'", pi->dbvarname) : "",
                       pc.p[i].dir != SQL_PARAM_IN ? kprintf(", variable='%s', out='%s'", pi->variable ? pi->variable : "",
                                                             v_tostr(proc_out_value(pc.p[i].out, pi))) : "");
        }
        if (retcode) buf_printf(&dbg, "\nStatusCode = %s", fmt_number(res.status));
        buf_printf(&dbg, "\nResult sets: %d", res.nsets);
        DebugQuery *dq = kmalloc(sizeof(DebugQuery));
        dq->name = kprintf("%s (stored procedure)", proc);
        dq->datasource = d.name; dq->sql = buf_cstr(&dbg); dq->ms = ms;
        dq->records = res.nsets ? res.sets[0]->nrows : 0;
        dq->template = rs->cur_tpl ? rs->cur_tpl->path : "";
        dq->next = rs->dq; rs->dq = dq;
    }
}

TAG(procparam) {
    (void)flow;
    ProcCall *pc = t_proc;
    if (!pc)
        kf_throw(c, "Template", "Context validation error for tag CFPROCPARAM.", "The tag must be nested inside a CFSTOREDPROC tag.");
    const char *type = attr_str(c, n, "type", "IN");
    int dir = !kf_stricmp(type, "in") ? SQL_PARAM_IN : !kf_stricmp(type, "out") ? SQL_PARAM_OUT :
              !kf_stricmp(type, "inout") ? SQL_PARAM_INOUT : 0;
    if (!dir)
        kf_throw(c, "Application", "Attribute validation error for tag CFPROCPARAM.",
                 kprintf("The value of the attribute TYPE, which is currently \"%s\", must be one of the values: IN, OUT, INOUT.", kf_html_escape(type)));
    const char *cfsqltype = require_attr(c, n, "cfsqltype");
    int known = 0;
    for (int i = 0; CF_SQL_TYPES[i]; i++) if (!kf_stricmp(CF_SQL_TYPES[i], cfsqltype)) known = 1;
    if (!known)
        kf_throw(c, "Application", "Attribute validation error for tag CFPROCPARAM.",
                 kprintf("The value of the attribute CFSQLTYPE, which is currently \"%s\", is invalid. Valid types are %s and CF_SQL_VARCHAR.",
                         kf_html_escape(cfsqltype), "CF_SQL_BIGINT, CF_SQL_BIT, CF_SQL_CHAR, CF_SQL_DATE, CF_SQL_DECIMAL, CF_SQL_DOUBLE, "
                         "CF_SQL_FLOAT, CF_SQL_IDSTAMP, CF_SQL_INTEGER, CF_SQL_LONGVARCHAR, CF_SQL_MONEY, CF_SQL_MONEY4, CF_SQL_NUMERIC, "
                         "CF_SQL_REAL, CF_SQL_REFCURSOR, CF_SQL_SMALLINT, CF_SQL_TIME, CF_SQL_TIMESTAMP, CF_SQL_TINYINT"));
    if (!kf_stricmp(cfsqltype, "CF_SQL_REFCURSOR"))
        kf_throw(c, "Database", "CF_SQL_REFCURSOR is only supported by the Oracle native drivers.",
                 "The KoldFusion Flat-File Driver returns result sets directly; use CFPROCRESULT.");
    ProcParamInfo pi; memset(&pi, 0, sizeof pi);
    pi.type = kf_upper(type);
    pi.cfsqltype = kf_upper(cfsqltype);
    pi.variable = attr_str(c, n, "variable", NULL);
    pi.dbvarname = attr_str(c, n, "dbvarname", NULL);
    if (pi.dbvarname && !*pi.dbvarname) pi.dbvarname = NULL;
    pi.maxlength = (int)attr_num(c, n, "maxlength", 0);
    pi.scale = (int)attr_num(c, n, "scale", 0);
    pi.isnull = attr_bool(c, n, "null", 0);
    if (dir != SQL_PARAM_IN && !pi.variable)
        kf_throw(c, "Application", "Attribute validation error for tag CFPROCPARAM.",
                 kprintf("The tag requires the attribute(s): VARIABLE when TYPE is %s.", pi.type));
    SqlParam sp; memset(&sp, 0, sizeof sp);
    sp.name = pi.dbvarname;
    sp.dir = dir;
    sp.value = v_null();
    if (dir != SQL_PARAM_OUT && !pi.isnull) {
        int present;
        Val v = attr_val(c, n, "value", &present);
        if (!present)
            kf_throw(c, "Application", "Attribute validation error for tag CFPROCPARAM.",
                     "The tag requires the attribute(s): VALUE (or NULL=\"Yes\") when TYPE is IN or INOUT.");
        pi.shown = val_simple_str(c, v, NULL);
        sp.value = proc_bind_value(c, pi.shown, cfsqltype, pi.maxlength);
    }
    if (!pi.shown) pi.shown = "";
    if (pc->np == pc->cap) {
        pc->cap = pc->cap ? pc->cap * 2 : 8;
        SqlParam *np = kmalloc(sizeof(SqlParam) * pc->cap);
        ProcParamInfo *ni = kmalloc(sizeof(ProcParamInfo) * pc->cap);
        if (pc->np) { memcpy(np, pc->p, sizeof(SqlParam) * pc->np); memcpy(ni, pc->info, sizeof(ProcParamInfo) * pc->np); }
        pc->p = np; pc->info = ni;
    }
    pc->p[pc->np] = sp;
    pc->info[pc->np] = pi;
    pc->np++;
}

TAG(procresult) {
    (void)flow;
    if (!t_proc)
        kf_throw(c, "Template", "Context validation error for tag CFPROCRESULT.", "The tag must be nested inside a CFSTOREDPROC tag.");
    const char *name = require_attr(c, n, "name");
    double set = attr_num(c, n, "resultset", 1);
    if (set < 1 || set != floor(set))
        kf_throw(c, "Application", "Attribute validation error for tag CFPROCRESULT.",
                 "The value of the attribute RESULTSET must be a positive integer.");
    Struct *r = struct_new();
    struct_set(r, "name", v_strdup(name));
    struct_set(r, "resultset", v_num(set));
    struct_set(r, "maxrows", v_num(attr_num(c, n, "maxrows", -1)));
    array_push(t_proc->results, v_struct(r));
}

/* CFOBJECTCACHE ACTION="Clear": the undocumented 4.x tag that empties the query cache */
TAG(objectcache) {
    (void)flow;
    const char *action = require_attr(c, n, "action");
    if (kf_stricmp(action, "clear"))
        kf_throw(c, "Application", "Attribute validation error for tag CFOBJECTCACHE.",
                 kprintf("The value of the attribute ACTION, which is currently \"%s\", must be CLEAR.", kf_html_escape(action)));
    qcache_flush();
}
