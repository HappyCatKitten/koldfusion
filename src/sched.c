/*
 * sched.c - the ColdFusion Executive's scheduler: runs HTTP requests on a
 * timetable kept in the registry (Schedule\<task>), optionally publishing the
 * result to a static file - the original 1999 "static site generator".
 */
#define _GNU_SOURCE
#include "engine.h"
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

static pthread_mutex_t run_mu = PTHREAD_MUTEX_INITIALIZER;

static double parse_dt(const char *date, const char *time) {
    double d;
    if (!date || !*date) return 0;
    if (!date_parse(kprintf("%s %s", date, time && *time ? time : "00:00:00"), &d)) return 0;
    return d;
}

static void run_task(const char *name) {
    char *key = cfg_key(kprintf("Schedule\\%s", name));
    char *url = reg_get(key, "url", "");
    if (url[0] == '/') url = kprintf("http://127.0.0.1:%d%s", G.port, url);
    int timeout = atoi(reg_get(key, "requesttimeout", "30"));
    if (timeout <= 0) timeout = 30;
    char *user = reg_get(key, "username", ""), *pass = kf_unscramble(reg_get(key, "password", ""));
    char *proxy = reg_get(key, "proxyserver", "");
    Buf body; buf_init(&body);
    int status; char *sl; Struct *rh; char err[512];
    Struct *hdrs = struct_new();
    struct_set(hdrs, "User-Agent", v_str("KoldFusion Scheduler"));
    double t0 = kf_time_ms();
    int ok = http_client("GET", url, hdrs, NULL, 0, timeout, proxy, 80, user, pass, &body, &status, &sl, &rh, err, sizeof err);
    reg_set(key, "LastRun", date_odbc(date_now()), 0);
    if (!ok) {
        kf_log("schedule.log", "Error", "Task %s failed: %s", name, err);
        reg_set(key, "LastResult", err, 0);
        return;
    }
    if (atoi(reg_get(key, "publish", "0")) || !kf_stricmp(reg_get(key, "publish", "no"), "yes")) {
        char *path = reg_get(key, "path", ""), *file = reg_get(key, "file", "");
        if (*path && *file) kf_write_file(kf_path_join(path, file), body.s ? body.s : "", body.len, 0);
    }
    kf_log("schedule.log", "Information", "Task %s completed in %.0f ms (%s).", name, kf_time_ms() - t0, sl);
    reg_set(key, "LastResult", sl, 0);
}

typedef struct RunArg { char *name; } RunArg;
static void *run_thread(void *p) {
    RunArg *ra = p;
    Arena *a = arena_new(); g_arena = a;
    pthread_mutex_lock(&run_mu);
    run_task(ra->name);
    pthread_mutex_unlock(&run_mu);
    g_arena = NULL; arena_free(a);
    free(ra->name); free(ra);
    return NULL;
}

int sched_run_task(const char *name, char *msg, size_t msglen) {
    if (!reg_exists(cfg_key(kprintf("Schedule\\%s", name)), NULL)) {
        snprintf(msg, msglen, "The scheduled task %s does not exist.", name);
        return 0;
    }
    RunArg *ra = malloc(sizeof *ra);
    ra->name = strdup(name);
    pthread_t t;
    pthread_create(&t, NULL, run_thread, ra);
    pthread_detach(t);
    snprintf(msg, msglen, "The task %s has been started.", name);
    kf_log("schedule.log", "Information", "Task %s run on demand.", name);
    return 1;
}

static int is_due(const char *name, double now) {
    char *key = cfg_key(kprintf("Schedule\\%s", name));
    double start = parse_dt(reg_get(key, "startdate", ""), reg_get(key, "starttime", ""));
    if (!start || now < start) return 0;
    char *ed = reg_get(key, "enddate", "");
    if (*ed) {
        double end = parse_dt(ed, reg_get(key, "endtime", "23:59:59"));
        if (end && now > end) return 0;
    }
    char *interval = reg_get(key, "interval", "once");
    char *lr = reg_get(key, "LastRun", "");
    double last = 0;
    if (*lr) date_parse(lr, &last);
    if (!kf_stricmp(interval, "once")) return last == 0;
    double period;
    if (!kf_stricmp(interval, "daily")) period = 1;
    else if (!kf_stricmp(interval, "weekly")) period = 7;
    else if (!kf_stricmp(interval, "monthly")) period = 30.4375;
    else {
        double secs = atof(interval);
        if (secs < 60) secs = 60;
        /* "Daily every N minutes" runs between starttime and endtime each day */
        char *st = reg_get(key, "starttime", ""), *et = reg_get(key, "endtime", "");
        if (*et) {
            double frac = now - (long)now;
            double s = parse_dt("1/1/1900", st) - parse_dt("1/1/1900", "00:00:00");
            double e = parse_dt("1/1/1900", et) - parse_dt("1/1/1900", "00:00:00");
            if (frac < s || frac > e) return 0;
        }
        return !last || (now - last) * 86400 >= secs - 1;
    }
    /* next occurrence after the last run */
    double k = last ? (long)((last - start) / period) + 1 : 0;
    double next = start + k * period;
    return now >= next;
}

static void *scheduler(void *arg) {
    (void)arg;
    sleep(5);
    for (;;) {
        Arena *a = arena_new(); g_arena = a;
        Query *q = reg_list(cfg_key("Schedule"), 1, 0);
        double now = date_now();
        for (int r = 0; r < q->nrows; r++) {
            const char *name = v_tostr(query_get(q, 0, r));
            if (is_due(name, now)) {
                pthread_mutex_lock(&run_mu);
                if (cfg_int("Scheduler", "LogActivity", 1)) kf_log("schedule.log", "Information", "Running task %s.", name);
                run_task(name);
                pthread_mutex_unlock(&run_mu);
            }
        }
        g_arena = NULL; arena_free(a);
        sleep(60);
    }
    return NULL;
}

void sched_start(void) {
    pthread_t t;
    pthread_create(&t, NULL, scheduler, NULL);
    pthread_detach(t);
}
