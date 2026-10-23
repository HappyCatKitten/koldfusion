/*
 * session.c - Application, Session and Client variable storage; named locks.
 *
 * Application and Session scopes live in their own long-lived arenas; values
 * stored into them are deep-copied (see struct_set in core.c). Client
 * variables are simple strings kept in the registry or in a cookie, just like
 * ColdFusion 4.5 did it.
 */
#define _GNU_SOURCE
#include "engine.h"
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <errno.h>
#include "sql.h"

static pthread_mutex_t mu = PTHREAD_MUTEX_INITIALIZER;
static AppState *apps;
#define SESS_BUCKETS 256
static SessState *sessions[SESS_BUCKETS];

void session_init(void) {
    char *v = NULL;
    Arena *a = arena_new(); Arena *saved = g_arena; g_arena = a;
    v = cfg(REG_SERVER, "CFIDCounter", "1000");
    G.cfid_counter = atol(v);
    g_arena = saved; arena_free(a);
}

long next_cfid(void) {
    pthread_mutex_lock(&mu);
    long id = ++G.cfid_counter;
    pthread_mutex_unlock(&mu);
    char tmp[32]; snprintf(tmp, sizeof tmp, "%ld", id);
    reg_set(cfg_key(REG_SERVER), "CFIDCounter", tmp, 0);
    return id;
}

static Struct *new_scope(Arena *a) {
    Arena *saved = g_arena;
    g_arena = a;
    Struct *s = struct_new();
    g_arena = saved;
    return s;
}

AppState *app_get(const char *name, double timeout_days, int *created) {
    double now = date_now();
    *created = 0;
    pthread_mutex_lock(&mu);
    AppState *a;
    for (a = apps; a; a = a->next) if (!kf_stricmp(a->name, name)) break;
    if (a && a->last_access + a->timeout_days < now) {
        /* expired: start the application afresh */
        arena_free(a->arena);
        a->arena = arena_new_shared();
        a->scope = new_scope(a->arena);
        a->created = now;
        *created = 1;
    }
    if (!a) {
        a = calloc(1, sizeof(AppState));
        a->name = strdup(name);
        a->arena = arena_new_shared();
        a->scope = new_scope(a->arena);
        a->created = now;
        a->next = apps; apps = a;
        *created = 1;
    }
    a->last_access = now;
    a->timeout_days = timeout_days;
    pthread_mutex_unlock(&mu);
    return a;
}

static unsigned bucket(const char *k) { return kf_hash_nocase(k) % SESS_BUCKETS; }

SessState *sess_get(const char *app, const char *cfid, const char *cftoken, double timeout_days, int *created) {
    char key[512];
    snprintf(key, sizeof key, "%s_%s_%s", app, cfid, cftoken);
    for (char *p = key; *p; p++) if (*p >= 'a' && *p <= 'z') *p -= 32;
    double now = date_now();
    *created = 0;
    pthread_mutex_lock(&mu);
    unsigned b = bucket(key);
    SessState *s;
    for (s = sessions[b]; s; s = s->next) if (!strcmp(s->key, key)) break;
    if (s && s->last_access + s->timeout_days < now && s->refs == 0) {
        arena_free(s->arena);
        s->arena = arena_new_shared();
        s->scope = new_scope(s->arena);
        s->created = now;
        *created = 1;
    }
    if (!s) {
        s = calloc(1, sizeof(SessState));
        s->key = strdup(key);
        s->app = strdup(app);
        s->arena = arena_new_shared();
        s->scope = new_scope(s->arena);
        s->created = now;
        pthread_mutex_init(&s->mu, NULL);
        s->next = sessions[b]; sessions[b] = s;
        *created = 1;
    }
    s->refs++;
    s->last_access = now;
    s->timeout_days = timeout_days;
    pthread_mutex_unlock(&mu);
    return s;
}

void sess_release(SessState *s) {
    pthread_mutex_lock(&mu);
    s->refs--;
    s->last_access = date_now();
    pthread_mutex_unlock(&mu);
}

void session_housekeeping(void) {
    double now = date_now();
    pthread_mutex_lock(&mu);
    for (int b = 0; b < SESS_BUCKETS; b++) {
        SessState **pp = &sessions[b];
        while (*pp) {
            SessState *s = *pp;
            if (s->refs == 0 && s->last_access + s->timeout_days < now) {
                *pp = s->next;
                arena_free(s->arena);
                pthread_mutex_destroy(&s->mu);
                free(s->key); free(s->app); free(s);
                continue;
            }
            pp = &s->next;
        }
    }
    pthread_mutex_unlock(&mu);
}

Query *session_stats(void) {
    const char *cols[] = {"Type", "Name", "Created", "LastAccess", "Timeout", "Variables", "Bytes"};
    Query *q = query_new(7, cols);
    pthread_mutex_lock(&mu);
    for (AppState *a = apps; a; a = a->next) {
        int r = query_add_row(q);
        query_set(q, 0, r, v_str("Application"));
        query_set(q, 1, r, v_strdup(a->name));
        query_set(q, 2, r, v_date(a->created));
        query_set(q, 3, r, v_date(a->last_access));
        query_set(q, 4, r, v_num(a->timeout_days));
        query_set(q, 5, r, v_num(a->scope->n));
        query_set(q, 6, r, v_num((double)arena_used(a->arena)));
    }
    for (int b = 0; b < SESS_BUCKETS; b++) {
        for (SessState *s = sessions[b]; s; s = s->next) {
            int r = query_add_row(q);
            query_set(q, 0, r, v_str("Session"));
            query_set(q, 1, r, v_strdup(s->key));
            query_set(q, 2, r, v_date(s->created));
            query_set(q, 3, r, v_date(s->last_access));
            query_set(q, 4, r, v_num(s->timeout_days));
            query_set(q, 5, r, v_num(s->scope->n));
            query_set(q, 6, r, v_num((double)arena_used(s->arena)));
        }
    }
    pthread_mutex_unlock(&mu);
    return q;
}

/* ================================================================ client vars */
static char *client_key(RState *rs, const char *app) {
    return kprintf("%s\\%s\\%s:%s", cfg_key("Clients"), kf_upper(app), rs->cfid, rs->cftoken);
}

void add_set_cookie(RState *rs, const char *name, const char *value, const char *expires, const char *path,
                    const char *domain, int secure);

static int is_dsn_storage(const char *st) { return kf_stricmp(st, "cookie") && kf_stricmp(st, "registry"); }

static char *sql_q(const char *s) {
    Buf b; buf_init(&b);
    buf_putc(&b, '\'');
    for (; *s; s++) { if (*s == '\'') buf_putc(&b, '\''); buf_putc(&b, *s); }
    buf_putc(&b, '\'');
    return buf_cstr(&b);
}

static void parse_packed(Struct *into, const char *data) {
    char *d = kstrdup(data);
    for (char *tok = strtok(d, "#"); tok; tok = strtok(NULL, "#")) {
        char *eq = strchr(tok, '=');
        if (!eq) continue;
        *eq = 0;
        struct_set(into, kf_urldecode(tok, strlen(tok)), v_str(kf_urldecode(eq + 1, strlen(eq + 1))));
    }
}

static char *pack(Struct *s) {
    Buf b; buf_init(&b);
    for (int i = 0; i < s->n; i++) {
        Val v = s->e[i].v;
        if (!v_is_simple(v)) continue;
        buf_printf(&b, "%s=%s#", kf_urlencode(s->e[i].key), kf_urlencode(v_tostr(v)));
    }
    return buf_cstr(&b);
}

void client_load(RState *rs, const char *app) {
    rs->client = struct_new();
    double now = date_now();
    if (is_dsn_storage(rs->client_storage)) {
        Dsn d;
        if (dsn_lookup(rs->client_storage, &d)) {
            Query *q = NULL; long aff; char err[512];
            char *sql = kprintf("SELECT data FROM CDATA WHERE cfid = %s AND app = %s",
                                sql_q(kprintf("%s:%s", rs->cfid, rs->cftoken)), sql_q(kf_upper(app)));
            if (sql_exec(d.path, sql, &q, &aff, err, sizeof err) && q && q->nrows)
                parse_packed(rs->client, v_tostr(query_get(q, 0, 0)));
            else if (!q) kf_log("application.log", "Warning", "Client variable storage %s: %s", rs->client_storage, err);
        }
    } else if (!kf_stricmp(rs->client_storage, "cookie")) {
        Val *v = struct_get(rs->cookie, kprintf("CFCLIENT_%s", kf_upper(app)));
        if (v) {
            char *data = kstrdup(v_tostr(*v));
            for (char *tok = strtok(data, "#"); tok; tok = strtok(NULL, "#")) {
                char *eq = strchr(tok, '=');
                if (!eq) continue;
                *eq = 0;
                struct_set(rs->client, kf_urldecode(tok, strlen(tok)), v_str(kf_urldecode(eq + 1, strlen(eq + 1))));
            }
        }
    } else {
        Query *q = reg_list(client_key(rs, app), 0, 1);
        for (int r = 0; r < q->nrows; r++)
            struct_set(rs->client, v_tostr(query_get(q, 0, r)), query_get(q, 2, r));
    }
    struct_set(rs->client, "CFID", v_strdup(rs->cfid));
    struct_set(rs->client, "CFTOKEN", v_strdup(rs->cftoken));
    struct_set(rs->client, "URLToken", v_str(kprintf("CFID=%s&CFTOKEN=%s", rs->cfid, rs->cftoken)));
    Val *hc = struct_get(rs->client, "HitCount");
    double hits = 0;
    if (hc) v_tonum(*hc, &hits);
    struct_set(rs->client, "HitCount", v_num(hits + 1));
    if (!struct_get(rs->client, "TimeCreated")) struct_set(rs->client, "TimeCreated", v_str(date_odbc(now)));
    Val *lv = struct_get(rs->client, "LastVisit");
    struct_set(rs->client, "__PrevVisit", lv ? *lv : v_str(date_odbc(now)));
    struct_set(rs->client, "LastVisit", v_str(date_odbc(now)));
    struct_delete(rs->client, "__PrevVisit");
    rs->client_dirty = !cfg_int("Variables", "DisableGlobalClientUpdates", 0);
}

void client_save(RState *rs, const char *app) {
    if (!rs->client_enabled || !rs->client || !rs->client_dirty) return;
    if (is_dsn_storage(rs->client_storage)) {
        Dsn d;
        if (!dsn_lookup(rs->client_storage, &d)) return;
        char *id = sql_q(kprintf("%s:%s", rs->cfid, rs->cftoken)), *ap = sql_q(kf_upper(app));
        char *script = kprintf("DELETE FROM CDATA WHERE cfid = %s AND app = %s;\nINSERT INTO CDATA (cfid, app, data) VALUES (%s, %s, %s)",
                               id, ap, id, ap, sql_q(pack(rs->client)));
        char err[512];
        if (!sql_exec_script(d.path, script, err, sizeof err))
            kf_log("application.log", "Warning", "Client variable storage %s: %s", rs->client_storage, err);
        return;
    }
    if (!kf_stricmp(rs->client_storage, "cookie")) {
        Buf b; buf_init(&b);
        for (int i = 0; i < rs->client->n; i++) {
            Val v = rs->client->e[i].v;
            if (!v_is_simple(v)) continue;
            buf_printf(&b, "%s=%s#", kf_urlencode(rs->client->e[i].key), kf_urlencode(v_tostr(v)));
        }
        Arena *saved = g_arena; (void)saved;
        add_set_cookie(rs, kprintf("CFCLIENT_%s", kf_upper(app)), buf_cstr(&b), NULL, "/", NULL, 0);
        return;
    }
    char *key = client_key(rs, app);
    reg_delete_key(key);
    for (int i = 0; i < rs->client->n; i++) {
        Val v = rs->client->e[i].v;
        if (!v_is_simple(v)) continue;   /* client variables hold simple values only */
        reg_set(key, rs->client->e[i].key, v_tostr(v), 0);
    }
}

/* ================================================================ named locks */
typedef struct NLock { char *name; pthread_rwlock_t rw; int exclusive_holders; } NLock;
static NLock locks[1024];
static int nlocks;
static pthread_mutex_t lock_mu = PTHREAD_MUTEX_INITIALIZER;
static __thread int held_mode[1024];   /* per-thread: 1 = write, 2 = read */

int named_lock(const char *name, int exclusive, double timeout_s) {
    pthread_mutex_lock(&lock_mu);
    int i;
    for (i = 0; i < nlocks; i++) if (!strcmp(locks[i].name, name)) break;
    if (i == nlocks) {
        if (nlocks == 1024) { i = (int)(kf_hash_nocase(name) % 1024); }
        else {
            locks[i].name = strdup(name);
            pthread_rwlock_init(&locks[i].rw, NULL);
            nlocks++;
        }
    }
    pthread_mutex_unlock(&lock_mu);
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    double t = timeout_s > 0 ? timeout_s : 0.001;
    ts.tv_sec += (time_t)t;
    ts.tv_nsec += (long)((t - (long)t) * 1e9);
    if (ts.tv_nsec >= 1000000000) { ts.tv_sec++; ts.tv_nsec -= 1000000000; }
    int rc = exclusive ? pthread_rwlock_timedwrlock(&locks[i].rw, &ts) : pthread_rwlock_timedrdlock(&locks[i].rw, &ts);
    if (rc == EDEADLK) return -1;
    if (rc) return -1;
    held_mode[i] = exclusive ? 1 : 2;
    return i;
}

void named_unlock(int h) {
    if (h < 0 || h >= 1024) return;
    pthread_rwlock_unlock(&locks[h].rw);
    held_mode[h] = 0;
}
