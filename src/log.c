/*
 * log.c - C:\CFUSION\LOG\*.log, in the 4.x quoted comma format:
 *   "Severity","ThreadID","Date","Time","Details"
 */
#define _GNU_SOURCE
#include "engine.h"
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <sys/stat.h>
#include <syslog.h>

static pthread_mutex_t log_mu = PTHREAD_MUTEX_INITIALIZER;

char *kf_log_dir(void) {
    char *d = cfg(REG_SERVER, "LogDirectory", NULL);
    if (d && *d) return d;
    return kf_path_join(G.root, "log");
}

void kf_log(const char *file, const char *severity, const char *fmt, ...) {
    char msg[4096];
    va_list ap; va_start(ap, fmt);
    vsnprintf(msg, sizeof msg, fmt, ap);
    va_end(ap);
    for (char *p = msg; *p; p++) { if (*p == '"') *p = '\''; if (*p == '\n' || *p == '\r') *p = ' '; }

    Arena *tmp = NULL, *saved = g_arena;
    if (!g_arena) { tmp = arena_new(); g_arena = tmp; }
    char *dir = kf_log_dir();
    char path[4096];
    snprintf(path, sizeof path, "%s/%s", dir, file);
    if (tmp) { g_arena = saved; arena_free(tmp); }

    time_t t = time(NULL);
    struct tm tm; localtime_r(&t, &tm);
    pthread_mutex_lock(&log_mu);
    struct stat st;
    int fresh = stat(path, &st) != 0 || st.st_size == 0;
    FILE *f = fopen(path, "a");
    if (f) {
        if (fresh) fprintf(f, "\"Severity\",\"ThreadID\",\"Date\",\"Time\",\"Details\"\n");
        fprintf(f, "\"%s\",\"TID=%lu\",\"%02d/%02d/%02d\",\"%02d:%02d:%02d\",\"%s\"\n",
                severity, (unsigned long)pthread_self() % 100000,
                tm.tm_mon + 1, tm.tm_mday, tm.tm_year % 100, tm.tm_hour, tm.tm_min, tm.tm_sec, msg);
        fclose(f);
    }
    pthread_mutex_unlock(&log_mu);
    /* Logging > System Logging: also send to the UNIX syslog */
    Arena *t2 = NULL, *sv2 = g_arena;
    if (!g_arena) { t2 = arena_new(); g_arena = t2; }
    int use_syslog = cfg_int("Logging", "SystemLogging", 0);
    if (t2) { g_arena = sv2; arena_free(t2); }
    if (use_syslog) {
        int pri = !strcmp(severity, "Error") ? LOG_ERR : !strcmp(severity, "Warning") ? LOG_WARNING : LOG_INFO;
        syslog(LOG_DAEMON | pri, "KoldFusion %s: %s", file, msg);
    }
}
