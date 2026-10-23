/*
 * main.c - KoldFusion Application Server 4.5 startup.
 *
 *   kfserver [-p port] [-b bindaddr] [-r installdir] [-w webroot]
 *            [--reset-admin-password pw]
 *
 * On first start an "installation" is performed: the registry is created
 * with the defaults a fresh ColdFusion 4.5 install had, and the sample data
 * sources are built from kfroot/seed/NAME.sql.
 */
#define _GNU_SOURCE
#include "engine.h"
#include "sql.h"
#include <stdlib.h>
#include <unistd.h>
#include <limits.h>
#include <pthread.h>
#include <sys/stat.h>
#include <sys/utsname.h>
#include <time.h>

Globals G;
char *kf_global_root(void) { return G.root; }
char *kf_global_webroot(void) { return G.webroot; }
extern Struct *g_server_scope;
extern Arena *g_server_arena;

static void set_default(const char *sub, const char *entry, const char *value) {
    if (!reg_exists(cfg_key(sub), entry)) reg_set(cfg_key(sub), entry, value, 0);
}

static void install_defaults(void) {
    const char *S = REG_SERVER;
    char *unsecured = kf_path_join(G.webroot, "CFIDE/administrator/");
    struct { const char *sub, *entry, *value; } D[] = {
        {S, "Version", KF_VERSION_STR},
        {S, "ProductName", "KoldFusion Server"},
        {S, "Edition", KF_EDITION},
        {S, "SerialNumber", "KFE450-0451999-2000-OLDSKOOL"},
        {S, "InstallDate", "1999-11-23"},
        {S, "LimitSimultaneousRequests", "15"},
        {S, "TimeoutRequests", "1"},
        {S, "RequestTimeout", "30"},
        {S, "RestartUnresponsive", "1"},
        {S, "RestartAt", "10"},
        {S, "RestartAbnormal", "1"},
        {S, "StrictAttributeValidation", "0"},
        {S, "SuppressWhitespace", "0"},
        {S, "MissingTemplateHandler", ""},
        {S, "SiteWideErrorHandler", ""},
        {S, "TemplateCacheSize", "1024"},
        {S, "TrustedCache", "0"},
        {S, "DBConnectionInactiveTime", "60"},
        {S, "MaxCachedQueries", "100"},
        {S, "UseAdminPassword", "1"},
        {S, "UseStudioPassword", "1"},
        {S, "UnsecuredTagsDirectory", unsecured},
        {S, "AdminEmail", ""},
        {S, "LogDirectory", kf_path_join(G.root, "log")},
        {S, "CFIDCounter", "1000"},
        {S, "MaxRequestMemoryMB", "256"},
        {"Server\\TagRestrictions", "CFCONTENT", "1"},
        {"Server\\TagRestrictions", "CFDIRECTORY", "1"},
        {"Server\\TagRestrictions", "CFFILE", "1"},
        {"Server\\TagRestrictions", "CFOBJECT", "1"},
        {"Server\\TagRestrictions", "CFREGISTRY", "1"},
        {"Server\\TagRestrictions", "CFADMINSECURITY", "1"},
        {"Server\\TagRestrictions", "CFEXECUTE", "1"},
        {"Variables", "EnableApplicationVariables", "1"},
        {"Variables", "EnableSessionVariables", "1"},
        {"Variables", "ApplicationTimeoutDefault", "2"},
        {"Variables", "ApplicationTimeoutMax", "2"},
        {"Variables", "SessionTimeoutDefault", "0.0138888888889"},
        {"Variables", "SessionTimeoutMax", "0.0138888888889"},
        {"Variables", "DefaultClientStorage", "Registry"},
        {"Variables", "DisableGlobalClientUpdates", "0"},
        {"Variables", "PurgeClientDays", "90"},
        {"Locking", "ServerScope", "none"},
        {"Locking", "ApplicationScope", "none"},
        {"Locking", "SessionScope", "none"},
        {"Locking", "SingleThreadedSessions", "0"},
        {"Debug", "EnablePerformanceMonitoring", "0"},
        {"Debug", "EnableStackTrace", "0"},
        {"Debug", "ShowVariables", "0"},
        {"Debug", "ShowProcessingTime", "0"},
        {"Debug", "DetailView", "0"},
        {"Debug", "ShowSQL", "1"},
        {"Debug", "ShowQueryInfo", "0"},
        {"Debug", "ShowTemplatePath", "1"},
        {"Debug", "DebugIPs", ""},
        {"Logging", "LogSlowPages", "0"},
        {"Logging", "SlowPageSeconds", "30"},
        {"Logging", "SystemLogging", "0"},
        {"Logging", "MailLogSeverity", "Warning"},
        {"Logging", "LogAllMail", "0"},
        {"Mail", "Server", ""},
        {"Mail", "Port", "25"},
        {"Mail", "Timeout", "60"},
        {"Mail", "SpoolInterval", "15"},
        {"Scheduler", "RefreshInterval", "15"},
        {"Scheduler", "LogActivity", "1"},
        {"Java", "JVMPath", "/usr/java/jdk1.2.2/jre/lib/i386/classic/libjvm.so"},
        {"Java", "ClassPath", ""},
        {"Java", "InitialHeap", "1024"},
        {"Java", "MaxHeap", "16384"},
        {"Java", "SystemOptions", ""},
        {"Java", "ImplementationOptions", ""},
        {"Java", "CFXJarPath", kf_path_join(G.root, "java/classes/cfx.jar")},
        {"SourceControl", "SrcSafeIni", ""},
        {"SourceControl", "WorkingDirectory", ""},
        {"SourceControl", "Timeout", "30"},
        {"Security", "UseAdvancedSecurity", "0"},
        {"Security", "SecurityServer", "127.0.0.1"},
        {"Security", "SharedSecret", ""},
        {"Security", "AuthPort", "2808"},
        {"Security", "AuthzPort", "2809"},
        {"Security", "PolicyStoreCache", "1"},
        {"Security", "PolicyStoreRefresh", "1"},
        {"Security", "LoadPolicyAtStartup", "1"},
        {"Security", "AuthorizationCache", "1"},
        {"Security", "AuthorizationRefresh", "1"},
        {"Security", "ServerCache", "1"},
        {"Security", "ServerCacheRefresh", "1"},
        {"Security", "MaxCacheEntries", "10000"},
        {"Security", "UseAdminAuthentication", "0"},
        {"Security", "UseStudioAuthentication", "0"},
        {"Security", "UseSandboxes", "0"},
        {"Security", "ProtectAllResources", "0"},
        {NULL, NULL, NULL}
    };
    for (int i = 0; D[i].sub; i++) set_default(D[i].sub, D[i].entry, D[i].value);
    if (!reg_exists(cfg_key(S), "AdminPassword")) cfg_set(S, "AdminPassword", kf_scramble("admin"));
    if (!reg_exists(cfg_key(S), "StudioPassword")) cfg_set(S, "StudioPassword", kf_scramble("studio"));

    /* sample data sources */
    struct { const char *name, *driver, *kind, *desc; } DS[] = {
        {"cfsnippets", "Microsoft Access Driver (*.mdb)", "ODBC", "KoldFusion CFML snippets and examples"},
        {"exampleapp", "Microsoft Access Driver (*.mdb)", "ODBC", "Company example application"},
        {"btg", "Microsoft Access Driver (*.mdb)", "ODBC", "BTG Contacts (demo gallery)"},
        {"cfexamples", "Microsoft Access Driver (*.mdb)", "ODBC", "Example applications (GlobalCorp intranet, HR app)"},
        {"CompanyInfo", "Microsoft Access Driver (*.mdb)", "ODBC", "Developing Web Applications tutorial database"},
        {"demos", "Microsoft Access Driver (*.mdb)", "ODBC", "Demo gallery scripts (event calendar etc.)"},
        {NULL, NULL, NULL, NULL}
    };
    struct { const char *name, *lib, *desc; } CX[] = {
        {"CFX_HELLO", "cfx_hello.so", "CFX_HELLO - the obligatory first CFX tag, written in C."},
        {"CFX_SYSINFO", "cfx_sysinfo.so", "CFX_SYSINFO - returns a query describing the server machine."},
        {"CFX_DICE", "cfx_dice.so", "CFX_DICE - rolls dice. Las Vegas-grade randomness."},
        {NULL, NULL, NULL}
    };
    for (int i = 0; CX[i].name; i++) {
        char *k = cfg_key(kprintf("CFX\\%s", CX[i].name));
        if (reg_exists(k, NULL)) continue;
        reg_set(k, "Type", "C++", 0);
        reg_set(k, "LibraryPath", CX[i].lib, 0);
        reg_set(k, "Procedure", "ProcessTagRequest", 0);
        reg_set(k, "KeepLoaded", "1", 0);
        reg_set(k, "Description", CX[i].desc, 0);
    }
    struct { const char *name, *code, *codebase, *w, *h; } AP[] = {
        {"copytext", "copytext.class", "/CFIDE/classes/allair/controls", "300", "40"},
        {"marquee", "Marquee.class", "/CFIDE/classes/applets", "468", "30"},
        {NULL, NULL, NULL, NULL, NULL}
    };
    for (int i = 0; AP[i].name; i++) {
        char *k = cfg_key(kprintf("Applets\\%s", AP[i].name));
        if (reg_exists(k, NULL)) continue;
        reg_set(k, "Code", AP[i].code, 0);
        reg_set(k, "Codebase", AP[i].codebase, 0);
        reg_set(k, "Method", "", 0);
        reg_set(k, "Width", AP[i].w, 0);
        reg_set(k, "Height", AP[i].h, 0);
        reg_set(k, "VSpace", "0", 0);
        reg_set(k, "HSpace", "0", 0);
        reg_set(k, "Align", "LEFT", 0);
        reg_set(k, "NotSupported", "<B>Browser must support Java to view ColdFusion Java Applets</B>", 0);
    }
    for (int i = 0; DS[i].name; i++) {
        char *k = cfg_key(kprintf("DataSources\\%s", DS[i].name));
        if (reg_exists(k, NULL)) continue;
        reg_set(k, "Driver", DS[i].driver, 0);
        reg_set(k, "Kind", DS[i].kind, 0);
        reg_set(k, "Database", DS[i].name, 0);
        reg_set(k, "Description", DS[i].desc, 0);
        reg_set(k, "Username", "", 0);
        reg_set(k, "Password", kf_scramble(""), 0);
        reg_set(k, "LoginTimeout", "30", 0);
        reg_set(k, "MaintainConnections", "1", 0);
        reg_set(k, "Disabled", "0", 0);
        reg_set(k, "Restrict", "", 0);
        reg_set(k, "PageTimeout", "600", 0);
        reg_set(k, "BufferSize", "0", 0);
    }
}

static void seed_databases(void) {
    const char *names[] = {"cfsnippets", "exampleapp", "btg", "cfexamples", "CompanyInfo", "demos", NULL};
    for (int i = 0; names[i]; i++) {
        char *dir = kf_path_join(kf_path_join(G.root, "db"), names[i]);
        struct stat st;
        if (stat(dir, &st) == 0) continue;
        char *seed = kf_path_join(kf_path_join(G.root, "seed"), kprintf("%s.sql", names[i]));
        size_t len;
        char *sql = kf_read_file(seed, &len);
        if (!sql) continue;
        kf_mkdirs(dir);
        char err[1024];
        if (!sql_exec_script(dir, sql, err, sizeof err))
            fprintf(stderr, "KoldFusion: seeding %s failed: %s\n", names[i], err);
        else
            fprintf(stderr, "  Created sample data source %s\n", names[i]);
        free(sql);
    }
}

static void init_server_scope(void) {
    g_server_arena = arena_new_shared();
    Arena *saved = g_arena;
    g_arena = g_server_arena;
    g_server_scope = struct_new();
    Struct *cf = struct_new();
    struct_set(cf, "ProductName", v_str("KoldFusion Server"));
    struct_set(cf, "ProductVersion", v_str(KF_VERSION));
    struct_set(cf, "ProductLevel", v_str(KF_EDITION));
    struct_set(cf, "SerialNumber", v_str(cfg(REG_SERVER, "SerialNumber", "")));
    struct_set(cf, "SupportedLocales", v_str("English (Australian),English (Canadian),English (New Zealand),English (UK),English (US),"
        "French (Belgian),French (Canadian),French (Standard),French (Swiss),German (Austrian),German (Standard),German (Swiss),"
        "Italian (Standard),Italian (Swiss),Norwegian (Bokmal),Norwegian (Nynorsk),Portuguese (Brazilian),Portuguese (Standard),"
        "Spanish (Mexican),Spanish (Modern),Spanish (Standard),Swedish,Dutch (Belgian),Dutch (Standard)"));
    struct_set(cf, "Expiration", v_str(""));
    struct_set(cf, "AppServer", v_str("KoldFusion"));
    struct_set(g_server_scope, "ColdFusion", v_struct(cf));
    struct_set(g_server_scope, "KoldFusion", v_struct(cf));
    Struct *os = struct_new();
    struct utsname u;
    uname(&u);
    struct_set(os, "Name", v_strdup(u.sysname));
    struct_set(os, "Version", v_strdup(u.release));
    struct_set(os, "AdditionalInformation", v_strdup(u.version));
    struct_set(os, "BuildNumber", v_strdup(u.machine));
    struct_set(os, "Arch", v_strdup(u.machine));
    struct_set(g_server_scope, "OS", v_struct(os));
    g_arena = saved;
}

static void *housekeeping(void *arg) {
    (void)arg;
    for (;;) {
        sleep(60);
        session_housekeeping();
    }
    return NULL;
}

void mail_spooler_start(void);
void sched_start(void);
int kf_run_cli(const char *file, const char *query);

int main(int argc, char **argv) {
    char cwd[PATH_MAX];
    if (!getcwd(cwd, sizeof cwd)) strcpy(cwd, ".");
    char exe[PATH_MAX];
    ssize_t el = readlink("/proc/self/exe", exe, sizeof exe - 1);
    if (el > 0) exe[el] = 0; else snprintf(exe, sizeof exe, "%s", argv[0]);
    G.exe_path = strdup(exe);
    G.argv = argv;
    G.port = 8500;
    G.bind = "127.0.0.1";
    const char *root = NULL, *web = NULL, *reset_pw = NULL, *run_file = NULL, *run_query = NULL;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-p") && i + 1 < argc) G.port = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-b") && i + 1 < argc) G.bind = argv[++i];
        else if (!strcmp(argv[i], "-r") && i + 1 < argc) root = argv[++i];
        else if (!strcmp(argv[i], "-w") && i + 1 < argc) web = argv[++i];
        else if (!strcmp(argv[i], "--reset-admin-password") && i + 1 < argc) reset_pw = argv[++i];
        else if (!strcmp(argv[i], "--run") && i + 1 < argc) { run_file = argv[++i]; if (i + 1 < argc && argv[i + 1][0] != '-') run_query = argv[++i]; }
        else {
            fprintf(stderr, "usage: %s [-p port] [-b bind-address] [-r install-dir] [-w webroot] [--reset-admin-password pw]\n", argv[0]);
            return 2;
        }
    }
    char rbuf[PATH_MAX], wbuf[PATH_MAX];
    if (!root) {
        /* default: <exe dir>/../kfroot, falling back to ./kfroot */
        char tmp[PATH_MAX]; snprintf(tmp, sizeof tmp, "%s", G.exe_path);
        char *sl = strrchr(tmp, '/'); if (sl) *sl = 0;
        /* <exe dir>/kfroot, then <exe dir>/../kfroot (bin/kfserver), then ./kfroot */
        struct stat st;
        snprintf(rbuf, sizeof rbuf, "%s/kfroot", tmp);
        if (stat(rbuf, &st)) {
            char *sl2 = strrchr(tmp, '/');
            if (sl2) { *sl2 = 0; snprintf(rbuf, sizeof rbuf, "%s/kfroot", tmp); }
            if (!sl2 || stat(rbuf, &st)) snprintf(rbuf, sizeof rbuf, "%s/kfroot", cwd);
        }
        root = rbuf;
    }
    if (!web) {
        char tmp[PATH_MAX]; snprintf(tmp, sizeof tmp, "%s", root);
        char *sl = strrchr(tmp, '/'); if (sl) *sl = 0;
        snprintf(wbuf, sizeof wbuf, "%s/wwwroot", tmp);
        web = wbuf;
    }
    char rr[PATH_MAX], ww[PATH_MAX];
    G.root = strdup(realpath(root, rr) ? rr : root);
    G.webroot = strdup(realpath(web, ww) ? ww : web);
    srandom((unsigned)time(NULL) ^ (unsigned)getpid());

    Arena *a = arena_new();
    g_arena = a;
    const char *dirs[] = {"log", "temp", "drive_c/temp", "mail/spool", "mail/undelivr", "mail/log", "verity/collections",
                          "customtags", "cfx", "db", "registry", NULL};
    for (int i = 0; dirs[i]; i++) kf_mkdirs(kf_path_join(G.root, dirs[i]));
    reg_init(kf_path_join(G.root, "registry/kf.registry"));
    install_defaults();
    if (reset_pw) {
        cfg_set(REG_SERVER, "AdminPassword", kf_scramble(reset_pw));
        printf("Administrator password reset.\n");
    }
    G.started_at = date_now();
    G.started_ms = kf_time_ms();

    if (run_file) {
        seed_databases();
        session_init();
        init_server_scope();
        g_arena = NULL;
        return kf_run_cli(run_file, run_query);
    }
    printf("\n  KoldFusion Application Server %s %s\n", KF_EDITION, KF_VERSION_STR);
    printf("  Copyright (c) 1995-1999 Allair Corporation. All rights reserved.\n");
    printf("  (A nostalgic tribute. Not affiliated with anyone, living or acquired.)\n\n");
    printf("  Install directory : %s\n  Web root          : %s\n", G.root, G.webroot);
    seed_databases();
    session_init();
    init_server_scope();
    arena_free(a);
    g_arena = NULL;

    pthread_t hk;
    pthread_create(&hk, NULL, housekeeping, NULL);
    pthread_detach(hk);
    mail_spooler_start();
    sched_start();

    printf("  Listening on      : http://%s:%d/\n", G.bind, G.port);
    printf("  Administrator     : http://%s:%d/CFIDE/administrator/index.cfm\n\n", G.bind, G.port);
    fflush(stdout);
    int rc = http_serve();
    if (G.restart_requested) {
        printf("  Restarting KoldFusion Application Server...\n");
        fflush(stdout);
        execv(G.exe_path, argv);
        perror("execv");
    }
    return rc;
}
