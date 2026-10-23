/*
 * java.c - the embedded Java Virtual Machine (new in ColdFusion 4.5).
 *
 * KoldFusion has no build-time dependency on Java. The first time a page
 * needs Java (CFOBJECT TYPE="Java", CreateObject("Java", ...), a Java CFX tag
 * or CFSERVLET) we find libjvm.so, dlopen() it and call JNI_CreateJavaVM()
 * once per process, with the class path, heap sizes and options from the
 * Java page of the Administrator. Request threads attach to the VM as daemon
 * threads on first use and detach when they exit (pthread key destructor).
 *
 * Java objects are CF values of type VT_OBJECT. A KfObject holds a JNI
 * global reference that is released when the arena owning the KfObject is
 * freed: the request arena for ordinary variables, the session/application
 * arena when the object was stored in a shared scope (the deep copy made by
 * struct_set takes a new global reference, see kfobj_copy). Method calls go
 * through java.lang.reflect: the public methods of a class are read once and
 * cached, and overloads are resolved by argument count and a type score, with
 * JavaCast() hints. Every JNI call sequence runs inside Push/PopLocalFrame,
 * and CF errors are thrown only after the frame has been popped.
 */
#define _GNU_SOURCE
#include "kfjava.h"
#include "func.h"
#include <stdlib.h>
#include <ctype.h>
#include <math.h>
#include <dlfcn.h>
#include <dirent.h>
#include <unistd.h>
#include <limits.h>
#include <pthread.h>
#include <sys/stat.h>

/* ================================================================ state */
static pthread_mutex_t jvm_mu = PTHREAD_MUTEX_INITIALIZER;
static JavaVM *g_vm;
static int g_state;                 /* 0 not tried, 1 loaded, -1 creation failed (permanent) */
static char g_error[8192];          /* why the JVM is not available */
static char g_libpath[PATH_MAX];    /* libjvm.so in use */
static char g_libsource[64];        /* where we found it */
static char g_classpath[8192];
static char g_options[4096];        /* options passed to JNI_CreateJavaVM, for the Administrator */
static char g_version[256];
static double g_loaded_at;
static int g_attached;              /* threads currently attached */
static long g_objects;              /* Java object references currently held */
static pthread_mutex_t obj_mu = PTHREAD_MUTEX_INITIALIZER;

static pthread_key_t env_key;
static pthread_once_t key_once = PTHREAD_ONCE_INIT;
static __thread JNIEnv *t_env;

/* ---------------------------------------------------------------- the runtime classes we use */
static struct {
    jclass Object, Class, ClassLoader, String, Method, Constructor, Field, ITE, Throwable, Number, Integer, Long,
           Short, Byte, Float, Double, Boolean, Character, Date, List, Map, Set, Vector, Hashtable, RArray, System,
           Runtime, ByteArr, Modifier;
    jobject loader;
    jmethodID toString, getClass, Class_getName, getMethods, getConstructors, getFields, Class_getModifiers,
              isArray, getComponentType, getSuperclass, getInterfaces, getMethod, forName, isPrimitive,
              Method_getName, Method_getParameterTypes, Method_getModifiers, Method_getDeclaringClass, Method_invoke,
              Ctor_getParameterTypes, Ctor_getModifiers, Ctor_newInstance,
              Field_getName, Field_getType, Field_getModifiers, Field_get, Field_set,
              getTargetException, getMessage,
              Integer_valueOf, Long_valueOf, Short_valueOf, Byte_valueOf, Float_valueOf, Double_valueOf,
              Boolean_valueOf, Character_valueOf, doubleValue, intValue, booleanValue,
              Date_init, getTime, List_size, List_get, Map_keySet, Map_get, Set_toArray,
              Vector_init, addElement, Hashtable_init, put,
              Array_getLength, Array_get, Array_newInstance, Array_set, getProperty,
              getRuntime, totalMemory, freeMemory, maxMemory;
} R;

/* ================================================================ finding libjvm.so */
static int file_exists(const char *p) { struct stat st; return stat(p, &st) == 0 && S_ISREG(st.st_mode); }
static int dir_exists(const char *p) { struct stat st; return stat(p, &st) == 0 && S_ISDIR(st.st_mode); }

/* a JDK/JRE home (or a directory inside it) -> its libjvm.so */
static int probe_home(const char *home, char *out, size_t n) {
    static const char *sub[] = {
        "lib/server/libjvm.so", "jre/lib/server/libjvm.so", "lib/amd64/server/libjvm.so",
        "jre/lib/amd64/server/libjvm.so", "lib/aarch64/server/libjvm.so", "jre/lib/aarch64/server/libjvm.so",
        "lib/i386/server/libjvm.so", "jre/lib/i386/server/libjvm.so", "lib/client/libjvm.so",
        "jre/lib/i386/client/libjvm.so", "jre/lib/i386/classic/libjvm.so", "server/libjvm.so", "libjvm.so", NULL };
    if (!home || !*home) return 0;
    if (file_exists(home)) {
        const char *b = strrchr(home, '/');
        if (b && !strcmp(b + 1, "libjvm.so")) { snprintf(out, n, "%s", home); return 1; }
        return 0;
    }
    if (!dir_exists(home)) return 0;
    for (int i = 0; sub[i]; i++) {
        char p[PATH_MAX];
        snprintf(p, sizeof p, "%s/%s", home, sub[i]);
        if (file_exists(p)) { char r[PATH_MAX]; snprintf(out, n, "%s", realpath(p, r) ? r : p); return 1; }
    }
    return 0;
}

static int probe_glob_dir(const char *dir, char *out, size_t n) {
    DIR *d = opendir(dir);
    if (!d) return 0;
    char best[PATH_MAX] = "";
    char bestname[256] = "";
    struct dirent *de;
    while ((de = readdir(d))) {
        if (de->d_name[0] == '.') continue;
        char home[PATH_MAX], lib[PATH_MAX];
        snprintf(home, sizeof home, "%s/%s", dir, de->d_name);
        /* prefer the highest-sorting name (newest JDK) */
        if (probe_home(home, lib, sizeof lib) && strcmp(de->d_name, bestname) > 0) {
            snprintf(best, sizeof best, "%s", lib);
            snprintf(bestname, sizeof bestname, "%s", de->d_name);
        }
    }
    closedir(d);
    if (!*best) return 0;
    snprintf(out, n, "%s", best);
    return 1;
}

/* Registry (Administrator > Java), JAVA_HOME, java on the PATH, /usr/lib/jvm/<any>, ~/.local/jdk/<any> */
static int jvm_find(char *out, size_t n, char *src, size_t sn) {
    const char *no = getenv("KF_NOJVM");
    if (no && *no && strcmp(no, "0")) { snprintf(src, sn, "disabled by KF_NOJVM"); return 0; }
    char *reg = cfg("Java", "JVMPath", "");
    if (reg && *reg && probe_home(kf_native_path(reg), out, n)) { snprintf(src, sn, "Administrator setting"); return 1; }
    const char *jh = getenv("JAVA_HOME");
    if (jh && probe_home(jh, out, n)) { snprintf(src, sn, "JAVA_HOME"); return 1; }
    const char *path = getenv("PATH");
    if (path) {
        char *p = strdup(path), *save = NULL;
        for (char *d = strtok_r(p, ":", &save); d; d = strtok_r(NULL, ":", &save)) {
            char j[PATH_MAX], r[PATH_MAX];
            snprintf(j, sizeof j, "%s/java", d);
            if (!file_exists(j) || !realpath(j, r)) continue;
            char *sl = strrchr(r, '/'); if (sl) *sl = 0;           /* .../bin */
            sl = strrchr(r, '/'); if (sl) *sl = 0;                 /* home */
            if (probe_home(r, out, n)) { snprintf(src, sn, "java on the PATH"); free(p); return 1; }
        }
        free(p);
    }
    if (probe_glob_dir("/usr/lib/jvm", out, n)) { snprintf(src, sn, "/usr/lib/jvm"); return 1; }
    const char *home = getenv("HOME");
    if (home) {
        char d[PATH_MAX];
        snprintf(d, sizeof d, "%s/.local/jdk", home);
        if (probe_glob_dir(d, out, n)) { snprintf(src, sn, "~/.local/jdk"); return 1; }
    }
    if (probe_glob_dir("/usr/java", out, n) || probe_glob_dir("/opt/java", out, n)) { snprintf(src, sn, "/usr/java"); return 1; }
    snprintf(src, sn, "looked at the Administrator setting, JAVA_HOME, java on the PATH, /usr/lib/jvm and ~/.local/jdk");
    return 0;
}

/* ================================================================ class path and options */
const char *kfj_cfx_jar(void) {
    static __thread char buf[PATH_MAX];
    char *reg = cfg("Java", "CFXJarPath", "");
    if (reg && *reg) {
        char *p = kf_native_path(reg);
        if (file_exists(p)) { snprintf(buf, sizeof buf, "%s", p); return buf; }
    }
    snprintf(buf, sizeof buf, "%s/java/cfx.jar", G.root);
    return buf;
}

static void cp_add(Buf *b, const char *p) {
    if (!p || !*p) return;
    if (b->len) buf_putc(b, ':');
    buf_puts(b, p);
}

/* Class Path setting: entries separated by ';' (the NT way) or ':' (UNIX); C:\ paths map into the install */
static void build_classpath(Buf *b) {
    cp_add(b, kfj_cfx_jar());
    cp_add(b, kf_path_join(G.root, "java/classes"));
    char *cp = cfg("Java", "ClassPath", "");
    if (!cp || !*cp) return;
    char *s = kstrdup(cp);
    char *start = s;
    for (char *p = s; ; p++) {
        int end = !*p;
        int sep = *p == ';' || (*p == ':' && !(p - start == 1 && isalpha((unsigned char)start[0])));
        if (end || sep) {
            char save = *p; *p = 0;
            char *t = kf_trim(start);
            if (*t) cp_add(b, kf_native_path(t));
            if (end) break;
            *p = save;
            start = p + 1;
        }
    }
}

static int heap_kb(const char *entry, int def) {
    int v = cfg_int("Java", entry, def);
    return v > 0 ? v : def;
}

/* ================================================================ JVM creation */
typedef struct CreateReq {
    JNI_CreateJavaVM_fn create;
    JavaVMInitArgs args;
    JavaVM *vm;
    jint rc;
    int done;
    pthread_mutex_t mu; pthread_cond_t cv;
} CreateReq;

/* The VM is created on a thread of its own that then stays parked for the life
 * of the process: HotSpot dislikes being created on the primordial thread, and
 * the creating thread may not simply exit while attached. */
static void *creator_thread(void *arg) {
    CreateReq *r = arg;
    JNIEnv *env = NULL;
    r->rc = r->create(&r->vm, (void **)&env, &r->args);
    pthread_mutex_lock(&r->mu);
    r->done = 1;
    pthread_cond_broadcast(&r->cv);
    int ok = r->rc == JNI_OK;
    pthread_mutex_unlock(&r->mu);
    if (!ok) return NULL;
    static pthread_mutex_t park_mu = PTHREAD_MUTEX_INITIALIZER;
    static pthread_cond_t park_cv = PTHREAD_COND_INITIALIZER;
    pthread_mutex_lock(&park_mu);
    for (;;) pthread_cond_wait(&park_cv, &park_mu);
    return NULL;
}

static void detach_thread(void *p) {
    (void)p;
    if (g_vm) {
        jvm_DetachCurrentThread(g_vm);
        __sync_fetch_and_sub(&g_attached, 1);
    }
}
static void make_key(void) { pthread_key_create(&env_key, detach_thread); }

static int rt_init(JNIEnv *env);

/* add one "-X..."/"-D..." option */
static void opt_add(JavaVMOption *o, int *n, int max, const char *s) {
    if (*n >= max || !s || !*s) return;
    o[*n].optionString = strdup(s);
    o[*n].extraInfo = NULL;
    (*n)++;
}

/* called with jvm_mu held */
static int jvm_create_locked(void) {
    if (g_state == 1) return 1;
    if (g_state == -1) return 0;
    char lib[PATH_MAX], src[64];
    if (!jvm_find(lib, sizeof lib, src, sizeof src)) {
        snprintf(g_error, sizeof g_error, "No Java Virtual Machine was found (KoldFusion %s). Set the Java Virtual Machine Path on the "
                 "Java page of the KoldFusion Administrator, or set JAVA_HOME.", src);
        return 0;
    }
    void *h = dlopen(lib, RTLD_NOW | RTLD_GLOBAL);
    if (!h) {
        snprintf(g_error, sizeof g_error, "The Java Virtual Machine library %s could not be loaded: %s", lib, dlerror());
        return 0;
    }
    JNI_GetCreatedJavaVMs_fn getvms = (JNI_GetCreatedJavaVMs_fn)dlsym(h, "JNI_GetCreatedJavaVMs");
    JNI_CreateJavaVM_fn create = (JNI_CreateJavaVM_fn)dlsym(h, "JNI_CreateJavaVM");
    if (!create || !getvms) {
        snprintf(g_error, sizeof g_error, "%s is not a Java Virtual Machine (JNI_CreateJavaVM is missing).", lib);
        return 0;
    }
    snprintf(g_libpath, sizeof g_libpath, "%s", lib);
    snprintf(g_libsource, sizeof g_libsource, "%s", src);
    JavaVM *vm = NULL; jsize nvm = 0;
    if (getvms(&vm, 1, &nvm) == JNI_OK && nvm > 0) {
        g_vm = vm;                       /* someone in this process already started one */
    } else {
        Buf cp; buf_init(&cp);
        build_classpath(&cp);
        snprintf(g_classpath, sizeof g_classpath, "%s", buf_cstr(&cp));
        JavaVMOption opts[64]; int no = 0;
        opt_add(opts, &no, 64, kprintf("-Djava.class.path=%s", g_classpath));
        int ih = heap_kb("InitialHeap", 1024), mh = heap_kb("MaxHeap", 16384);
        if (mh < 4096) mh = 4096;
        if (ih > mh) ih = mh;
        opt_add(opts, &no, 64, kprintf("-Xms%dk", ih));
        opt_add(opts, &no, 64, kprintf("-Xmx%dk", mh));
        opt_add(opts, &no, 64, "-Xrs");                         /* leave SIGINT/SIGTERM/SIGQUIT to KoldFusion */
        opt_add(opts, &no, 64, "-XX:-UsePerfData");             /* no /tmp/hsperfdata_* files */
        opt_add(opts, &no, 64, "-Djava.awt.headless=true");
        opt_add(opts, &no, 64, kprintf("-Dkoldfusion.root=%s", G.root));
        opt_add(opts, &no, 64, kprintf("-Dkoldfusion.webroot=%s", G.webroot));
        /* System Options: NAME=value;NAME2=value2 -> -DNAME=value */
        char *so = kstrdup(cfg("Java", "SystemOptions", "")), *save = NULL;
        for (char *t = strtok_r(so, ";", &save); t; t = strtok_r(NULL, ";", &save)) {
            t = kf_trim(t);
            if (!*t) continue;
            opt_add(opts, &no, 64, t[0] == '-' ? t : kprintf("-D%s", t));
        }
        /* Implementation Options: raw JVM options (-Xss512k -XX:+UseSerialGC ...) */
        char *io = kstrdup(cfg("Java", "ImplementationOptions", ""));
        int gc_given = kf_stristr(io, "GC") != NULL;
        for (char *t = strtok_r(io, "; \t", &save); t; t = strtok_r(NULL, "; \t", &save))
            if (*t) opt_add(opts, &no, 64, t);
        if (!gc_given) opt_add(opts, &no, 64, "-XX:+UseSerialGC");
        Buf ob; buf_init(&ob);
        for (int i = 0; i < no; i++) { if (i) buf_putc(&ob, ' '); buf_puts(&ob, opts[i].optionString); }
        snprintf(g_options, sizeof g_options, "%s", buf_cstr(&ob));

        CreateReq *r = calloc(1, sizeof *r);
        r->create = create;
        r->args.version = JNI_VERSION_1_2;
        r->args.nOptions = no;
        r->args.options = opts;
        r->args.ignoreUnrecognized = JNI_TRUE;
        pthread_mutex_init(&r->mu, NULL);
        pthread_cond_init(&r->cv, NULL);
        pthread_attr_t at; pthread_attr_init(&at);
        pthread_attr_setdetachstate(&at, PTHREAD_CREATE_DETACHED);
        pthread_attr_setstacksize(&at, 8 * 1024 * 1024);
        pthread_t th;
        if (pthread_create(&th, &at, creator_thread, r)) {
            snprintf(g_error, sizeof g_error, "Could not start a thread for the Java Virtual Machine.");
            return 0;
        }
        pthread_attr_destroy(&at);
        pthread_mutex_lock(&r->mu);
        while (!r->done) pthread_cond_wait(&r->cv, &r->mu);
        pthread_mutex_unlock(&r->mu);
        for (int i = 0; i < no; i++) free(opts[i].optionString);
        if (r->rc != JNI_OK) {
            g_state = -1;
            snprintf(g_error, sizeof g_error, "JNI_CreateJavaVM failed (error %d) with the options [%s]. Check the Java settings "
                     "in the KoldFusion Administrator and restart the server.", (int)r->rc, g_options);
            kf_log("server.log", "Error", "%s", g_error);
            return 0;                    /* r is leaked on purpose: the creator thread may still use it */
        }
        g_vm = r->vm;
    }
    pthread_once(&key_once, make_key);
    JNIEnv *env = NULL;
    JavaVMAttachArgs aa = { JNI_VERSION_1_2, "KoldFusion", NULL };
    if (jvm_AttachCurrentThreadAsDaemon(g_vm, &env, &aa) != JNI_OK || !rt_init(env)) {
        g_state = -1;
        snprintf(g_error, sizeof g_error, "The Java Virtual Machine started but the core classes could not be initialised.");
        return 0;
    }
    t_env = env;
    pthread_setspecific(env_key, (void *)1);
    __sync_fetch_and_add(&g_attached, 1);
    /* java.version etc. */
    j_PushLocalFrame(env, 16);
    jvalue a[1];
    char *ver = "?", *vendor = "?";
    a[0].l = kfj_str(env, "java.version");
    jobject s = j_CallStaticObjectMethodA(env, R.System, R.getProperty, a);
    if (s) ver = kfj_cstr(env, s);
    a[0].l = kfj_str(env, "java.vendor");
    s = j_CallStaticObjectMethodA(env, R.System, R.getProperty, a);
    if (s) vendor = kfj_cstr(env, s);
    j_ExceptionClear(env);
    j_PopLocalFrame(env, NULL);
    snprintf(g_version, sizeof g_version, "%s (%s)", ver, vendor);
    g_state = 1;
    g_loaded_at = date_now();
    g_error[0] = 0;
    kf_log("server.log", "Information", "Java Virtual Machine %s loaded from %s.", g_version, g_libpath);
    return 1;
}

static int jvm_ensure(void) {
    if (g_state == 1) return 1;
    pthread_mutex_lock(&jvm_mu);
    int ok = jvm_create_locked();
    pthread_mutex_unlock(&jvm_mu);
    return ok;
}

int kfj_available(char *why, size_t wl) {
    if (jvm_ensure()) return 1;
    if (why) snprintf(why, wl, "%s", g_error);
    return 0;
}

/* attach the current thread (once); NULL when no JVM */
static JNIEnv *env_get(void) {
    if (t_env) return t_env;
    if (!jvm_ensure()) return NULL;
    if (t_env) return t_env;
    JNIEnv *env = NULL;
    if (jvm_GetEnv(g_vm, &env, JNI_VERSION_1_2) == JNI_OK) { t_env = env; return env; }
    JavaVMAttachArgs aa = { JNI_VERSION_1_2, "KoldFusion Request", NULL };
    if (jvm_AttachCurrentThreadAsDaemon(g_vm, &env, &aa) != JNI_OK) return NULL;
    t_env = env;
    pthread_setspecific(env_key, (void *)1);          /* detach_thread() runs when this thread exits */
    __sync_fetch_and_add(&g_attached, 1);
    return env;
}

JNIEnv *kfj_env(Ctx *c) {
    JNIEnv *env = env_get();
    if (env) return env;
    kf_throw(c, KFJ_ERRTYPE, "The Java Virtual Machine is not available.",
             kprintf("%s", kf_html_escape(g_error[0] ? g_error : "The thread could not be attached to the Java Virtual Machine.")));
}

/* ================================================================ core class table */
static jclass gclass(JNIEnv *env, const char *n) {
    jclass c = j_FindClass(env, n);
    if (!c) { j_ExceptionClear(env); return NULL; }
    jclass g = j_NewGlobalRef(env, c);
    j_DeleteLocalRef(env, c);
    return g;
}
#define MID(var, cls, name, sig) do { if (!(R.var = j_GetMethodID(env, R.cls, name, sig))) { j_ExceptionClear(env); return 0; } } while (0)
#define SMID(var, cls, name, sig) do { if (!(R.var = j_GetStaticMethodID(env, R.cls, name, sig))) { j_ExceptionClear(env); return 0; } } while (0)

static int rt_init(JNIEnv *env) {
    struct { jclass *slot; const char *name; } C[] = {
        {&R.Object, "java/lang/Object"}, {&R.Class, "java/lang/Class"}, {&R.ClassLoader, "java/lang/ClassLoader"},
        {&R.String, "java/lang/String"}, {&R.Method, "java/lang/reflect/Method"},
        {&R.Constructor, "java/lang/reflect/Constructor"}, {&R.Field, "java/lang/reflect/Field"},
        {&R.ITE, "java/lang/reflect/InvocationTargetException"}, {&R.Throwable, "java/lang/Throwable"},
        {&R.Number, "java/lang/Number"}, {&R.Integer, "java/lang/Integer"}, {&R.Long, "java/lang/Long"},
        {&R.Short, "java/lang/Short"}, {&R.Byte, "java/lang/Byte"}, {&R.Float, "java/lang/Float"},
        {&R.Double, "java/lang/Double"}, {&R.Boolean, "java/lang/Boolean"}, {&R.Character, "java/lang/Character"},
        {&R.Date, "java/util/Date"}, {&R.List, "java/util/List"}, {&R.Map, "java/util/Map"}, {&R.Set, "java/util/Set"},
        {&R.Vector, "java/util/Vector"}, {&R.Hashtable, "java/util/Hashtable"}, {&R.RArray, "java/lang/reflect/Array"},
        {&R.System, "java/lang/System"}, {&R.Runtime, "java/lang/Runtime"}, {&R.ByteArr, "[B"},
        {NULL, NULL}};
    for (int i = 0; C[i].slot; i++) if (!(*C[i].slot = gclass(env, C[i].name))) return 0;
    MID(toString, Object, "toString", "()Ljava/lang/String;");
    MID(getClass, Object, "getClass", "()Ljava/lang/Class;");
    MID(Class_getName, Class, "getName", "()Ljava/lang/String;");
    MID(getMethods, Class, "getMethods", "()[Ljava/lang/reflect/Method;");
    MID(getConstructors, Class, "getConstructors", "()[Ljava/lang/reflect/Constructor;");
    MID(getFields, Class, "getFields", "()[Ljava/lang/reflect/Field;");
    MID(Class_getModifiers, Class, "getModifiers", "()I");
    MID(isArray, Class, "isArray", "()Z");
    MID(isPrimitive, Class, "isPrimitive", "()Z");
    MID(getComponentType, Class, "getComponentType", "()Ljava/lang/Class;");
    MID(getSuperclass, Class, "getSuperclass", "()Ljava/lang/Class;");
    MID(getInterfaces, Class, "getInterfaces", "()[Ljava/lang/Class;");
    MID(getMethod, Class, "getMethod", "(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;");
    SMID(forName, Class, "forName", "(Ljava/lang/String;ZLjava/lang/ClassLoader;)Ljava/lang/Class;");
    MID(Method_getName, Method, "getName", "()Ljava/lang/String;");
    MID(Method_getParameterTypes, Method, "getParameterTypes", "()[Ljava/lang/Class;");
    MID(Method_getModifiers, Method, "getModifiers", "()I");
    MID(Method_getDeclaringClass, Method, "getDeclaringClass", "()Ljava/lang/Class;");
    MID(Method_invoke, Method, "invoke", "(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;");
    MID(Ctor_getParameterTypes, Constructor, "getParameterTypes", "()[Ljava/lang/Class;");
    MID(Ctor_getModifiers, Constructor, "getModifiers", "()I");
    MID(Ctor_newInstance, Constructor, "newInstance", "([Ljava/lang/Object;)Ljava/lang/Object;");
    MID(Field_getName, Field, "getName", "()Ljava/lang/String;");
    MID(Field_getType, Field, "getType", "()Ljava/lang/Class;");
    MID(Field_getModifiers, Field, "getModifiers", "()I");
    MID(Field_get, Field, "get", "(Ljava/lang/Object;)Ljava/lang/Object;");
    MID(Field_set, Field, "set", "(Ljava/lang/Object;Ljava/lang/Object;)V");
    MID(getTargetException, ITE, "getTargetException", "()Ljava/lang/Throwable;");
    MID(getMessage, Throwable, "getMessage", "()Ljava/lang/String;");
    SMID(Integer_valueOf, Integer, "valueOf", "(I)Ljava/lang/Integer;");
    SMID(Long_valueOf, Long, "valueOf", "(J)Ljava/lang/Long;");
    SMID(Short_valueOf, Short, "valueOf", "(S)Ljava/lang/Short;");
    SMID(Byte_valueOf, Byte, "valueOf", "(B)Ljava/lang/Byte;");
    SMID(Float_valueOf, Float, "valueOf", "(F)Ljava/lang/Float;");
    SMID(Double_valueOf, Double, "valueOf", "(D)Ljava/lang/Double;");
    SMID(Boolean_valueOf, Boolean, "valueOf", "(Z)Ljava/lang/Boolean;");
    SMID(Character_valueOf, Character, "valueOf", "(C)Ljava/lang/Character;");
    MID(doubleValue, Number, "doubleValue", "()D");
    MID(intValue, Number, "intValue", "()I");
    MID(booleanValue, Boolean, "booleanValue", "()Z");
    MID(Date_init, Date, "<init>", "(J)V");
    MID(getTime, Date, "getTime", "()J");
    MID(List_size, List, "size", "()I");
    MID(List_get, List, "get", "(I)Ljava/lang/Object;");
    MID(Map_keySet, Map, "keySet", "()Ljava/util/Set;");
    MID(Map_get, Map, "get", "(Ljava/lang/Object;)Ljava/lang/Object;");
    MID(Set_toArray, Set, "toArray", "()[Ljava/lang/Object;");
    MID(Vector_init, Vector, "<init>", "()V");
    MID(addElement, Vector, "addElement", "(Ljava/lang/Object;)V");
    MID(Hashtable_init, Hashtable, "<init>", "()V");
    MID(put, Hashtable, "put", "(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;");
    SMID(Array_getLength, RArray, "getLength", "(Ljava/lang/Object;)I");
    SMID(Array_get, RArray, "get", "(Ljava/lang/Object;I)Ljava/lang/Object;");
    SMID(Array_newInstance, RArray, "newInstance", "(Ljava/lang/Class;I)Ljava/lang/Object;");
    SMID(Array_set, RArray, "set", "(Ljava/lang/Object;ILjava/lang/Object;)V");
    SMID(getProperty, System, "getProperty", "(Ljava/lang/String;)Ljava/lang/String;");
    SMID(getRuntime, Runtime, "getRuntime", "()Ljava/lang/Runtime;");
    MID(totalMemory, Runtime, "totalMemory", "()J");
    MID(freeMemory, Runtime, "freeMemory", "()J");
    MID(maxMemory, Runtime, "maxMemory", "()J");
    jmethodID gsl = j_GetStaticMethodID(env, R.ClassLoader, "getSystemClassLoader", "()Ljava/lang/ClassLoader;");
    if (!gsl) { j_ExceptionClear(env); return 0; }
    jobject l = j_CallStaticObjectMethodA(env, R.ClassLoader, gsl, NULL);
    if (!l) { j_ExceptionClear(env); return 0; }
    R.loader = j_NewGlobalRef(env, l);
    j_DeleteLocalRef(env, l);
    return 1;
}

jclass kfj_object_class(void) { return R.Object; }

jmethodID kfj_static_method(JNIEnv *env, jclass c, const char *name, const char *sig) {
    jmethodID m = j_GetStaticMethodID(env, c, name, sig);
    if (!m) j_ExceptionClear(env);
    return m;
}

/* ================================================================ strings */
/* CF strings are bytes; we treat them as UTF-8 (bytes that are not valid UTF-8 are taken as Latin-1) */
jstring kfj_strn(JNIEnv *env, const char *s, size_t n) {
    jchar stackbuf[256] = {0};
    jchar *u = n < 256 ? stackbuf : malloc(sizeof(jchar) * (n + 1));
    u[0] = 0;
    size_t k = 0;
    const unsigned char *p = (const unsigned char *)s, *e = p + n;
    while (p < e) {
        uint32_t cp; int len = 1;
        unsigned char c = *p;
        if (c < 0x80) cp = c;
        else if ((c & 0xE0) == 0xC0 && p + 1 < e && (p[1] & 0xC0) == 0x80 && c >= 0xC2) { cp = ((c & 0x1F) << 6) | (p[1] & 0x3F); len = 2; }
        else if ((c & 0xF0) == 0xE0 && p + 2 < e && (p[1] & 0xC0) == 0x80 && (p[2] & 0xC0) == 0x80) {
            cp = ((c & 0x0F) << 12) | ((p[1] & 0x3F) << 6) | (p[2] & 0x3F); len = 3;
            if (cp < 0x800) { cp = c; len = 1; }
        } else if ((c & 0xF8) == 0xF0 && p + 3 < e && (p[1] & 0xC0) == 0x80 && (p[2] & 0xC0) == 0x80 && (p[3] & 0xC0) == 0x80) {
            cp = ((c & 0x07) << 18) | ((p[1] & 0x3F) << 12) | ((p[2] & 0x3F) << 6) | (p[3] & 0x3F); len = 4;
            if (cp < 0x10000 || cp > 0x10FFFF) { cp = c; len = 1; }
        } else cp = c;                                   /* Latin-1 */
        p += len;
        if (cp >= 0x10000) { cp -= 0x10000; u[k++] = (jchar)(0xD800 + (cp >> 10)); u[k++] = (jchar)(0xDC00 + (cp & 0x3FF)); }
        else u[k++] = (jchar)cp;
    }
    jstring r = j_NewString(env, u, (jsize)k);
    if (u != stackbuf) free(u);
    return r;
}
jstring kfj_str(JNIEnv *env, const char *s) { return kfj_strn(env, s ? s : "", s ? strlen(s) : 0); }

char *kfj_cstr(JNIEnv *env, jstring s) {
    if (!s) return kstrdup("");
    jsize n = j_GetStringLength(env, s);
    jchar stackbuf[256] = {0};
    jchar *u = n < 256 ? stackbuf : malloc(sizeof(jchar) * (n + 1));
    j_GetStringRegion(env, s, 0, n, u);
    char *out = kmalloc((size_t)n * 3 + 1), *o = out;
    for (jsize i = 0; i < n; i++) {
        uint32_t cp = u[i];
        if (cp >= 0xD800 && cp < 0xDC00 && i + 1 < n && u[i + 1] >= 0xDC00 && u[i + 1] < 0xE000) {
            cp = 0x10000 + ((cp - 0xD800) << 10) + (u[i + 1] - 0xDC00); i++;
        }
        if (cp < 0x80) *o++ = (char)cp;
        else if (cp < 0x800) { *o++ = (char)(0xC0 | (cp >> 6)); *o++ = (char)(0x80 | (cp & 0x3F)); }
        else if (cp < 0x10000) { *o++ = (char)(0xE0 | (cp >> 12)); *o++ = (char)(0x80 | ((cp >> 6) & 0x3F)); *o++ = (char)(0x80 | (cp & 0x3F)); }
        else { *o++ = (char)(0xF0 | (cp >> 18)); *o++ = (char)(0x80 | ((cp >> 12) & 0x3F)); *o++ = (char)(0x80 | ((cp >> 6) & 0x3F)); *o++ = (char)(0x80 | (cp & 0x3F)); }
    }
    *o = 0;
    if (u != stackbuf) free(u);
    return out;
}

jobjectArray kfj_strarray(JNIEnv *env, int n, const char *const *items) {
    jobjectArray a = j_NewObjectArray(env, n, R.String, NULL);
    for (int i = 0; a && i < n; i++) {
        jstring s = kfj_str(env, items[i]);
        j_SetObjectArrayElement(env, a, i, s);
        j_DeleteLocalRef(env, s);
    }
    return a;
}

static char *class_name(JNIEnv *env, jclass c) {
    jstring s = j_CallObjectMethodA(env, c, R.Class_getName, NULL);
    char *r = kfj_cstr(env, s);
    if (s) j_DeleteLocalRef(env, s);
    return r;
}

jclass kfj_class_for_name(JNIEnv *env, const char *dotted) {
    jvalue a[3];
    a[0].l = kfj_str(env, dotted);
    a[1].z = JNI_TRUE;
    a[2].l = R.loader;
    jclass c = j_CallStaticObjectMethodA(env, R.Class, R.forName, a);
    j_DeleteLocalRef(env, a[0].l);
    return c;
}

/* pending exception -> class name and message (and an optional global ref), cleared */
int kfj_take_exception(JNIEnv *env, char **cls, char **msg, jobject *gref) {
    jthrowable t = j_ExceptionOccurred(env);
    if (!t) return 0;
    j_ExceptionClear(env);
    /* unwrap reflection's InvocationTargetException */
    while (j_IsInstanceOf(env, t, R.ITE)) {
        jthrowable inner = j_CallObjectMethodA(env, t, R.getTargetException, NULL);
        if (j_ExceptionCheck(env)) j_ExceptionClear(env);
        if (!inner) break;
        t = inner;
    }
    jclass c = j_GetObjectClass(env, t);
    if (cls) *cls = class_name(env, c);
    jstring m = j_CallObjectMethodA(env, t, R.getMessage, NULL);
    if (j_ExceptionCheck(env)) { j_ExceptionClear(env); m = NULL; }
    if (msg) *msg = m ? kfj_cstr(env, m) : kstrdup("");
    if (gref) *gref = j_NewGlobalRef(env, t);
    return 1;
}

/* ================================================================ objects */
typedef struct JClassInfo JClassInfo;
struct KfObject {
    int kind;                       /* 1 = Java */
    JClassInfo *jc;
    jobject inst;                   /* global ref; NULL until the object is constructed */
    jobject exc;                    /* global ref to the last exception thrown by a call on this object */
};

static void obj_release(void *p) {
    KfObject *o = p;
    if (!o->inst && !o->exc) return;
    JNIEnv *env = env_get();
    if (!env) return;
    pthread_mutex_lock(&obj_mu);
    jobject i = o->inst, x = o->exc;
    o->inst = o->exc = NULL;
    pthread_mutex_unlock(&obj_mu);
    if (i) { j_DeleteGlobalRef(env, i); __sync_fetch_and_sub(&g_objects, 1); }
    if (x) j_DeleteGlobalRef(env, x);
}

static KfObject *obj_new(JClassInfo *jc, jobject inst_local_or_global, JNIEnv *env) {
    KfObject *o = kmalloc(sizeof(KfObject));
    o->kind = 1;
    o->jc = jc;
    if (inst_local_or_global) { o->inst = j_NewGlobalRef(env, inst_local_or_global); __sync_fetch_and_add(&g_objects, 1); }
    arena_on_free(g_arena, obj_release, o);
    return o;
}

/* deep copy into another arena (Session/Application/Server scope, Duplicate()): a new global reference
 * to the same Java object, released when that arena goes away */
Val kfobj_copy(Val v) {
    KfObject *src = v.u.obj;
    JNIEnv *env = env_get();
    if (!env || !src) return v;
    KfObject *o = kmalloc(sizeof(KfObject));
    o->kind = src->kind;
    o->jc = src->jc;
    pthread_mutex_lock(&obj_mu);
    jobject i = src->inst, x = src->exc;
    if (i) { o->inst = j_NewGlobalRef(env, i); __sync_fetch_and_add(&g_objects, 1); }
    if (x) o->exc = j_NewGlobalRef(env, x);
    pthread_mutex_unlock(&obj_mu);
    arena_on_free(g_arena, obj_release, o);
    return v_object(o);
}

/* ================================================================ reflection cache */
enum { K_OTHER = 0, K_INT, K_LONG, K_SHORT, K_BYTE, K_FLOAT, K_DOUBLE, K_CHAR, K_BOOL,
       K_STRING, K_CHARSEQ, K_OBJECT, K_NUMBER, K_DATE, K_LIST, K_MAP, K_ARRAY, K_BYTES };

typedef struct JParam { int kind; int boxed; jclass cls; } JParam;
typedef struct JMember {
    char *name;
    int np; JParam *p;
    int is_static, bridge, varargs;
    JParam vcomp;                   /* varargs: the element type of the last parameter */
    jobject ref;                    /* global: Method / Constructor / Field */
    JParam type;                    /* fields */
} JMember;
struct JClassInfo {
    char *name;
    jclass cls;
    int is_interface;
    JMember *m; int nm;
    JMember *ct; int nct;
    JMember *f; int nf;
    JClassInfo *next;
};
static JClassInfo *jci_list;
static pthread_mutex_t jci_mu = PTHREAD_MUTEX_INITIALIZER;

/* malloc'd copy of an arena string (the cache outlives requests) */
static char *pstrdup(const char *s) { return strdup(s ? s : ""); }

static JParam classify(JNIEnv *env, jclass p) {
    JParam r = { K_OTHER, 0, j_NewGlobalRef(env, p) };
    char *n = class_name(env, p);
    static const struct { const char *name; int kind, boxed; } T[] = {
        {"int", K_INT, 0}, {"long", K_LONG, 0}, {"short", K_SHORT, 0}, {"byte", K_BYTE, 0}, {"float", K_FLOAT, 0},
        {"double", K_DOUBLE, 0}, {"char", K_CHAR, 0}, {"boolean", K_BOOL, 0},
        {"java.lang.Integer", K_INT, 1}, {"java.lang.Long", K_LONG, 1}, {"java.lang.Short", K_SHORT, 1},
        {"java.lang.Byte", K_BYTE, 1}, {"java.lang.Float", K_FLOAT, 1}, {"java.lang.Double", K_DOUBLE, 1},
        {"java.lang.Character", K_CHAR, 1}, {"java.lang.Boolean", K_BOOL, 1},
        {"java.lang.String", K_STRING, 0}, {"java.lang.Object", K_OBJECT, 0}, {"java.lang.Number", K_NUMBER, 0},
        {"[B", K_BYTES, 0}, {NULL, 0, 0}};
    for (int i = 0; T[i].name; i++) if (!strcmp(n, T[i].name)) { r.kind = T[i].kind; r.boxed = T[i].boxed; return r; }
    if (n[0] == '[') { r.kind = K_ARRAY; return r; }
    if (j_IsAssignableFrom(env, R.String, p)) r.kind = K_CHARSEQ;          /* CharSequence, Comparable, Serializable */
    else if (j_IsAssignableFrom(env, R.Vector, p)) r.kind = K_LIST;        /* Vector, List, Collection */
    else if (j_IsAssignableFrom(env, R.Hashtable, p)) r.kind = K_MAP;      /* Hashtable, Map, Dictionary */
    else if (j_IsAssignableFrom(env, R.Date, p)) r.kind = K_DATE;
    return r;
}

static void set_varargs(JNIEnv *env, JMember *m, int mods) {
    if (!(mods & 0x80) || m->np < 1 || m->p[m->np - 1].kind != K_ARRAY) return;   /* ACC_VARARGS (Java 5) */
    jclass comp = j_CallObjectMethodA(env, m->p[m->np - 1].cls, R.getComponentType, NULL);
    if (!comp) return;
    m->varargs = 1;
    m->vcomp = classify(env, comp);
    j_DeleteLocalRef(env, comp);
}

static void params_of(JNIEnv *env, jobject member, jmethodID getter, JMember *m) {
    jobjectArray pa = j_CallObjectMethodA(env, member, getter, NULL);
    m->np = pa ? j_GetArrayLength(env, pa) : 0;
    m->p = calloc(m->np ? m->np : 1, sizeof(JParam));
    for (int i = 0; i < m->np; i++) {
        jclass pc = j_GetObjectArrayElement(env, pa, i);
        m->p[i] = classify(env, pc);
        j_DeleteLocalRef(env, pc);
    }
    if (pa) j_DeleteLocalRef(env, pa);
}

/* a public method declared by a non-public class (HashMap$KeySet.size) cannot be invoked through its
 * own Method object; find the same method on a public superclass or interface */
static jobject public_equivalent(JNIEnv *env, jclass cls, jobject meth) {
    jclass todo[64]; int nt = 0, seen = 0;
    todo[nt++] = cls;
    jstring name = j_CallObjectMethodA(env, meth, R.Method_getName, NULL);
    jobjectArray ptypes = j_CallObjectMethodA(env, meth, R.Method_getParameterTypes, NULL);
    while (seen < nt) {
        jclass c = todo[seen++];
        int mods = j_CallIntMethodA(env, c, R.Class_getModifiers, NULL);
        if (seen > 1 && (mods & 0x1)) {
            jvalue a[2]; a[0].l = name; a[1].l = ptypes;
            jobject m = j_CallObjectMethodA(env, c, R.getMethod, a);
            if (m && !j_ExceptionCheck(env)) return m;
            j_ExceptionClear(env);
        }
        jclass sup = j_CallObjectMethodA(env, c, R.getSuperclass, NULL);
        if (sup && nt < 64) todo[nt++] = sup;
        jobjectArray ifs = j_CallObjectMethodA(env, c, R.getInterfaces, NULL);
        int ni = ifs ? j_GetArrayLength(env, ifs) : 0;
        for (int i = 0; i < ni && nt < 64; i++) todo[nt++] = j_GetObjectArrayElement(env, ifs, i);
    }
    return meth;
}

static JClassInfo *jci_build(JNIEnv *env, jclass cls, const char *name) {
    j_PushLocalFrame(env, 256);
    JClassInfo *ci = calloc(1, sizeof *ci);
    ci->name = pstrdup(name);
    ci->cls = j_NewGlobalRef(env, cls);
    int cmods = j_CallIntMethodA(env, cls, R.Class_getModifiers, NULL);
    ci->is_interface = (cmods & 0x200) != 0;
    /* methods */
    jobjectArray ms = j_CallObjectMethodA(env, cls, R.getMethods, NULL);
    if (j_ExceptionCheck(env)) { j_ExceptionClear(env); ms = NULL; }
    ci->nm = ms ? j_GetArrayLength(env, ms) : 0;
    ci->m = calloc(ci->nm ? ci->nm : 1, sizeof(JMember));
    for (int i = 0; i < ci->nm; i++) {
        j_PushLocalFrame(env, 32);
        jobject m = j_GetObjectArrayElement(env, ms, i);
        JMember *jm = &ci->m[i];
        jstring nm = j_CallObjectMethodA(env, m, R.Method_getName, NULL);
        jm->name = pstrdup(kfj_cstr(env, nm));
        int mods = j_CallIntMethodA(env, m, R.Method_getModifiers, NULL);
        jm->is_static = (mods & 0x8) != 0;
        jm->bridge = (mods & 0x40) != 0;
        params_of(env, m, R.Method_getParameterTypes, jm);
        set_varargs(env, jm, mods);
        jclass dc = j_CallObjectMethodA(env, m, R.Method_getDeclaringClass, NULL);
        int dmods = dc ? j_CallIntMethodA(env, dc, R.Class_getModifiers, NULL) : 1;
        if (!(dmods & 0x1) && !jm->is_static) m = public_equivalent(env, cls, m);
        j_ExceptionClear(env);
        jm->ref = j_NewGlobalRef(env, m);
        j_PopLocalFrame(env, NULL);
    }
    /* constructors */
    jobjectArray cs = j_CallObjectMethodA(env, cls, R.getConstructors, NULL);
    if (j_ExceptionCheck(env)) { j_ExceptionClear(env); cs = NULL; }
    ci->nct = cs ? j_GetArrayLength(env, cs) : 0;
    ci->ct = calloc(ci->nct ? ci->nct : 1, sizeof(JMember));
    for (int i = 0; i < ci->nct; i++) {
        j_PushLocalFrame(env, 32);
        jobject m = j_GetObjectArrayElement(env, cs, i);
        ci->ct[i].name = pstrdup("<init>");
        params_of(env, m, R.Ctor_getParameterTypes, &ci->ct[i]);
        set_varargs(env, &ci->ct[i], j_CallIntMethodA(env, m, R.Ctor_getModifiers, NULL));
        ci->ct[i].ref = j_NewGlobalRef(env, m);
        j_PopLocalFrame(env, NULL);
    }
    /* public fields */
    jobjectArray fs = j_CallObjectMethodA(env, cls, R.getFields, NULL);
    if (j_ExceptionCheck(env)) { j_ExceptionClear(env); fs = NULL; }
    ci->nf = fs ? j_GetArrayLength(env, fs) : 0;
    ci->f = calloc(ci->nf ? ci->nf : 1, sizeof(JMember));
    for (int i = 0; i < ci->nf; i++) {
        j_PushLocalFrame(env, 32);
        jobject f = j_GetObjectArrayElement(env, fs, i);
        jstring nm = j_CallObjectMethodA(env, f, R.Field_getName, NULL);
        ci->f[i].name = pstrdup(kfj_cstr(env, nm));
        int mods = j_CallIntMethodA(env, f, R.Field_getModifiers, NULL);
        ci->f[i].is_static = (mods & 0x8) != 0;
        jclass t = j_CallObjectMethodA(env, f, R.Field_getType, NULL);
        ci->f[i].type = classify(env, t);
        ci->f[i].ref = j_NewGlobalRef(env, f);
        j_PopLocalFrame(env, NULL);
    }
    j_ExceptionClear(env);
    j_PopLocalFrame(env, NULL);
    return ci;
}

static JClassInfo *jci_get(JNIEnv *env, jclass cls) {
    char *name = class_name(env, cls);
    pthread_mutex_lock(&jci_mu);
    for (JClassInfo *ci = jci_list; ci; ci = ci->next)
        if (!strcmp(ci->name, name) && j_IsSameObject(env, ci->cls, cls)) { pthread_mutex_unlock(&jci_mu); return ci; }
    JClassInfo *ci = jci_build(env, cls, name);
    ci->next = jci_list;
    jci_list = ci;
    pthread_mutex_unlock(&jci_mu);
    return ci;
}

static JClassInfo *obj_class(JNIEnv *env, KfObject *o) {
    if (!o->jc && o->inst) {
        jclass c = j_GetObjectClass(env, o->inst);
        o->jc = jci_get(env, c);
        j_DeleteLocalRef(env, c);
    }
    return o->jc;
}


/* ================================================================ JavaCast hints */
/* JavaCast() returns a fresh string, and we remember (per request) which strings were cast to which type,
 * so the hint survives <cfset x = JavaCast("int", y)> followed by obj.method(x). A JavaCast() written
 * directly in an argument list is recognised from the expression itself. */
static __thread struct { RState *rs; double start; const char **key; unsigned char *hint; int cap, n; } HT;

static void hint_put(const char *p, int hint) {
    RState *rs = t_rs;
    if (!rs || !p) return;
    if (HT.rs != rs || HT.start != rs->start_ms) { HT.rs = rs; HT.start = rs->start_ms; HT.key = NULL; HT.hint = NULL; HT.cap = HT.n = 0; }
    if ((HT.n + 1) * 2 >= HT.cap) {
        int nc = HT.cap ? HT.cap * 2 : 64;
        const char **nk = kmalloc(sizeof(char *) * nc);
        unsigned char *nh = kmalloc(nc);
        for (int i = 0; i < HT.cap; i++) if (HT.key[i]) {
            size_t h = ((uintptr_t)HT.key[i] >> 4) & (nc - 1);
            while (nk[h]) h = (h + 1) & (nc - 1);
            nk[h] = HT.key[i]; nh[h] = HT.hint[i];
        }
        HT.key = nk; HT.hint = nh; HT.cap = nc;
    }
    size_t h = ((uintptr_t)p >> 4) & (HT.cap - 1);
    while (HT.key[h] && HT.key[h] != p) h = (h + 1) & (HT.cap - 1);
    if (!HT.key[h]) HT.n++;
    HT.key[h] = p;
    HT.hint[h] = (unsigned char)hint;
}

static int hint_get(Val v) {
    RState *rs = t_rs;
    if (v.t != VT_STR || !HT.cap || HT.rs != rs || !rs || HT.start != rs->start_ms) return H_NONE;
    size_t h = ((uintptr_t)v.u.str.s >> 4) & (HT.cap - 1);
    while (HT.key[h]) {
        if (HT.key[h] == v.u.str.s) return HT.hint[h];
        h = (h + 1) & (HT.cap - 1);
    }
    return H_NONE;
}

static int hint_parse(const char *t) {
    static const struct { const char *n; int h; } T[] = {
        {"int", H_INT}, {"integer", H_INT}, {"long", H_LONG}, {"double", H_DOUBLE}, {"float", H_FLOAT},
        {"bool", H_BOOL}, {"boolean", H_BOOL}, {"string", H_STRING}, {"null", H_NULL}, {NULL, 0}};
    for (int i = 0; T[i].n; i++) if (!kf_stricmp(t, T[i].n)) return T[i].h;
    return -1;
}

static Val javacast_value(Ctx *c, Expr *where, const char *type, Val v, int *hint_out) {
    int h = hint_parse(type);
    if (h < 0)
        kf_throw_at(c, where, "Expression", kprintf("Invalid JavaCast type %s.", kf_html_escape(type)),
                    "The type must be one of bool, int, long, float, double, String (or null).");
    char *s;
    switch (h) {
    case H_INT: case H_LONG: {
        double d = val_number(c, v, where);
        s = h == H_INT ? kprintf("%d", (int)trunc(d)) : kprintf("%lld", (long long)trunc(d));
        break;
    }
    case H_DOUBLE: case H_FLOAT: {
        double d = val_number(c, v, where);
        s = fmt_number(h == H_FLOAT ? (double)(float)d : d);
        break;
    }
    case H_BOOL: s = kstrdup(val_truth(c, v, where) ? "YES" : "NO"); break;
    case H_NULL: s = kstrdup(""); break;
    default: s = kstrdup(val_simple_str(c, v, where)); break;
    }
    if (hint_out) *hint_out = h;
    hint_put(s, h);
    return v_str(s);
}

F(javacast) {
    (void)argc;
    return javacast_value(c, call, fa_str(c, call, argv, 0), argv[1], NULL);
}

/* ================================================================ CF -> Java */
static double dnum(Val v) { double d = 0; v_tonum(v, &d); return d; }

static jobject box(JNIEnv *env, int kind, double d) {
    jvalue a[1];
    switch (kind) {
    case K_INT: a[0].i = (jint)d; return j_CallStaticObjectMethodA(env, R.Integer, R.Integer_valueOf, a);
    case K_LONG: a[0].j = (jlong)d; return j_CallStaticObjectMethodA(env, R.Long, R.Long_valueOf, a);
    case K_SHORT: a[0].s = (jshort)d; return j_CallStaticObjectMethodA(env, R.Short, R.Short_valueOf, a);
    case K_BYTE: a[0].b = (jbyte)d; return j_CallStaticObjectMethodA(env, R.Byte, R.Byte_valueOf, a);
    case K_FLOAT: a[0].f = (jfloat)d; return j_CallStaticObjectMethodA(env, R.Float, R.Float_valueOf, a);
    case K_BOOL: a[0].z = d != 0; return j_CallStaticObjectMethodA(env, R.Boolean, R.Boolean_valueOf, a);
    case K_CHAR: a[0].c = (jchar)d; return j_CallStaticObjectMethodA(env, R.Character, R.Character_valueOf, a);
    default: a[0].d = d; return j_CallStaticObjectMethodA(env, R.Double, R.Double_valueOf, a);
    }
}
jobject kfj_box_int(JNIEnv *env, int i) { return box(env, K_INT, i); }
int kfj_int_value(JNIEnv *env, jobject o, int def) {
    if (!o || !j_IsInstanceOf(env, o, R.Number)) return def;
    return j_CallIntMethodA(env, o, R.intValue, NULL);
}

static jobject date_obj(JNIEnv *env, double oledate) {
    jvalue a[1];
    a[0].j = (jlong)llround((date_local_to_utc(oledate) - 25569.0) * 86400000.0);
    return j_NewObjectA(env, R.Date, R.Date_init, a);
}

static jobject bytes_obj(JNIEnv *env, const char *p, size_t n) {
    jbyteArray a = j_NewByteArray(env, (jsize)n);
    if (a && n) j_SetByteArrayRegion(env, a, 0, (jsize)n, (const jbyte *)p);
    return a;
}

static void ensure_constructed(JNIEnv *env, KfObject *o, int *ok, const char **why);

/* the natural Java form of a CF value (for Object parameters, Vector elements, servlet attributes) */
jobject kfj_to_java(JNIEnv *env, Val v, int hint) {
    switch (hint) {
    case H_NULL: return NULL;
    case H_INT: return box(env, K_INT, dnum(v));
    case H_LONG: return box(env, K_LONG, dnum(v));
    case H_DOUBLE: return box(env, K_DOUBLE, dnum(v));
    case H_FLOAT: return box(env, K_FLOAT, dnum(v));
    case H_BOOL: { int b = 0; v_tobool(v, &b); return box(env, K_BOOL, b); }
    case H_STRING: return kfj_str(env, v_is_simple(v) ? v_tostr(v) : "");
    }
    switch (v.t) {
    case VT_NULL: return kfj_str(env, "");
    case VT_STR: return kfj_strn(env, v.u.str.s, v.u.str.len);
    case VT_NUM: return box(env, K_DOUBLE, v.u.n);
    case VT_BOOL: return box(env, K_BOOL, v.u.b);
    case VT_DATE: return date_obj(env, v.u.n);
    case VT_BINARY: return bytes_obj(env, v.u.str.s, v.u.str.len);
    case VT_ARRAY: {
        jobject vec = j_NewObjectA(env, R.Vector, R.Vector_init, NULL);
        for (int i = 0; vec && i < v.u.a->n; i++) {
            jvalue a[1];
            a[0].l = kfj_to_java(env, v.u.a->v[i], hint_get(v.u.a->v[i]));
            j_CallVoidMethodA(env, vec, R.addElement, a);
            if (a[0].l) j_DeleteLocalRef(env, a[0].l);
        }
        return vec;
    }
    case VT_STRUCT: {
        jobject ht = j_NewObjectA(env, R.Hashtable, R.Hashtable_init, NULL);
        Struct *s = v.u.st;
        for (int i = 0; ht && i < s->n; i++) {
            jvalue a[2];
            a[0].l = kfj_str(env, s->e[i].key);
            a[1].l = kfj_to_java(env, s->e[i].v, hint_get(s->e[i].v));
            if (!a[1].l) a[1].l = kfj_str(env, "");          /* Hashtable refuses null values */
            jobject old = j_CallObjectMethodA(env, ht, R.put, a);
            if (old) j_DeleteLocalRef(env, old);
            j_DeleteLocalRef(env, a[0].l); j_DeleteLocalRef(env, a[1].l);
        }
        return ht;
    }
    case VT_OBJECT: {
        KfObject *o = v.u.obj;
        if (!o->inst) { int ok; const char *why; ensure_constructed(env, o, &ok, &why); }
        return o->inst ? j_NewLocalRef(env, o->inst) : NULL;
    }
    default: return NULL;
    }
}

static int str_is_boolword(const char *s) {
    return !kf_stricmp(s, "yes") || !kf_stricmp(s, "no") || !kf_stricmp(s, "true") || !kf_stricmp(s, "false");
}
static int utf8_one_char(const char *s, size_t n) {
    if (n == 0) return 0;
    unsigned char c = (unsigned char)s[0];
    size_t l = c < 0x80 ? 1 : (c & 0xE0) == 0xC0 ? 2 : (c & 0xF0) == 0xE0 ? 3 : (c & 0xF8) == 0xF0 ? 4 : 1;
    return l == n;
}
static int first_char(const char *s) {
    unsigned char c = (unsigned char)s[0];
    if (c < 0x80) return c;
    if ((c & 0xE0) == 0xC0) return ((c & 0x1F) << 6) | (s[1] & 0x3F);
    if ((c & 0xF0) == 0xE0) return ((c & 0x0F) << 12) | ((s[1] & 0x3F) << 6) | (s[2] & 0x3F);
    return c;
}

static JParam classify_local(JNIEnv *env, jclass p) {
    JParam r = classify(env, p);
    j_DeleteGlobalRef(env, r.cls);
    r.cls = p;
    return r;
}

/* convert a CF value for a parameter of a given type (boxed: Method.invoke unboxes and widens) */
static jobject to_param(JNIEnv *env, Val v, int hint, JParam *p) {
    if (hint == H_NULL) return NULL;
    if (v.t == VT_OBJECT) return kfj_to_java(env, v, H_NONE);
    switch (p->kind) {
    case K_INT: case K_LONG: case K_SHORT: case K_BYTE: case K_FLOAT: case K_DOUBLE:
        return box(env, p->kind, dnum(v));
    case K_BOOL: { int b = 0; v_tobool(v, &b); return box(env, K_BOOL, b); }
    case K_CHAR: {
        if (v.t == VT_NUM) return box(env, K_CHAR, v.u.n);
        const char *s = v_is_simple(v) ? v_tostr(v) : "";
        return box(env, K_CHAR, *s ? first_char(s) : 0);
    }
    case K_STRING: case K_CHARSEQ:
        if (v.t == VT_STR) return kfj_strn(env, v.u.str.s, v.u.str.len);
        return kfj_str(env, v_is_simple(v) || v.t == VT_BINARY ? v_tostr(v) : "");
    case K_NUMBER: return box(env, K_DOUBLE, dnum(v));
    case K_DATE: { double d = 0; v_todate(v, &d); return date_obj(env, d); }
    case K_BYTES:
        if (v.t == VT_BINARY || v.t == VT_STR) return bytes_obj(env, v.u.str.s, v.u.str.len);
        return bytes_obj(env, "", 0);
    case K_ARRAY: {
        if (v.t != VT_ARRAY) return NULL;
        jclass comp = j_CallObjectMethodA(env, p->cls, R.getComponentType, NULL);
        JParam cp = classify_local(env, comp);
        jvalue a[3];
        a[0].l = comp; a[1].i = v.u.a->n;
        jobject arr = j_CallStaticObjectMethodA(env, R.RArray, R.Array_newInstance, a);
        for (int i = 0; arr && i < v.u.a->n && !j_ExceptionCheck(env); i++) {
            Val el = v.u.a->v[i];
            a[0].l = arr; a[1].i = i; a[2].l = to_param(env, el, hint_get(el), &cp);
            j_CallStaticObjectMethodA(env, R.RArray, R.Array_set, a);   /* void; A-call works for any return */
            if (a[2].l) j_DeleteLocalRef(env, a[2].l);
        }
        return arr;
    }
    default: return kfj_to_java(env, v, hint);
    }
}

/* ================================================================ overload resolution */
static double score_arg(JNIEnv *env, Val v, int hint, JParam *p) {
    int k = p->kind;
    int prim = k >= K_INT && k <= K_BOOL && !p->boxed;
    if (hint == H_NULL) return prim ? 0 : 5;
    if (v.t == VT_OBJECT) {
        KfObject *o = v.u.obj;
        if (k == K_OBJECT) return 5;
        if (!o->inst) return k == K_OTHER ? 3 : 0;
        if (k >= K_INT && k <= K_BOOL) {
            static jclass *bx[] = { NULL, &R.Integer, &R.Long, &R.Short, &R.Byte, &R.Float, &R.Double, &R.Character, &R.Boolean };
            return j_IsInstanceOf(env, o->inst, *bx[k]) ? 8 : 0;
        }
        return j_IsInstanceOf(env, o->inst, p->cls) ? 9 : 0;
    }
    if (hint) {
        static const int hk[] = { 0, K_INT, K_LONG, K_DOUBLE, K_FLOAT, K_BOOL, K_STRING };
        int want = hk[hint];
        if (k == want) return p->boxed ? 9 : 10;
        if (want == K_STRING) return k == K_CHARSEQ ? 8 : k == K_OBJECT ? 5 : 0;
        if (k == K_OBJECT) return 4;
        if (want == K_BOOL) return 0;
        if (k == K_NUMBER) return 6;
        if (p->boxed) return 0;                       /* no widening into a different wrapper class */
        if (want == K_INT && k == K_LONG) return 6;
        if ((want == K_INT || want == K_LONG) && (k == K_FLOAT || k == K_DOUBLE)) return 4;
        if (want == K_FLOAT && k == K_DOUBLE) return 6;
        return 0;
    }
    double d = 0;
    int b = p->boxed;
    switch (v.t) {
    case VT_NULL: case VT_STR: {
        const char *s = v.t == VT_STR ? v.u.str.s : "";
        size_t n = v.t == VT_STR ? v.u.str.len : 0;
        if (k == K_STRING) return 9;
        if (k == K_CHARSEQ) return 8;
        if (k == K_OBJECT) return 6;
        if (v_isnumeric_str(s, &d)) {
            int integral = d == floor(d);
            switch (k) {
            case K_INT: return integral && fabs(d) <= 2147483647.0 ? 7 - b : 0;
            case K_LONG: return integral && fabs(d) < 9.2e18 ? (fabs(d) > 2147483647.0 ? 7 : 6) - b : 0;
            case K_DOUBLE: return (integral ? 5 : 7) - b;
            case K_FLOAT: return (integral ? 4 : 5) - b;
            case K_SHORT: return integral && fabs(d) <= 32767 ? 3 - b : 0;
            case K_BYTE: return integral && fabs(d) <= 127 ? 3 - b : 0;
            case K_NUMBER: return 5;
            case K_BOOL: return 2 - b;
            case K_CHAR: return n == 1 ? 4 - b : 0;
            default: return 0;
            }
        }
        if (k == K_BOOL) return str_is_boolword(s) ? 7 - b : 0;
        if (k == K_CHAR) return utf8_one_char(s, n) ? 4 - b : 0;
        if (k == K_DATE) return date_parse(s, &d) ? 4 : 0;
        if (k == K_BYTES) return 2;
        return 0;
    }
    case VT_NUM: {
        d = v.u.n;
        int integral = d == floor(d);
        switch (k) {
        case K_INT: return integral && fabs(d) <= 2147483647.0 ? 9 - b : 0;
        case K_LONG: return integral && fabs(d) < 9.2e18 ? 8 - b : 0;
        case K_DOUBLE: return (integral ? 7 : 9) - b;
        case K_FLOAT: return (integral ? 5 : 7) - b;
        case K_SHORT: return integral && fabs(d) <= 32767 ? 3 - b : 0;
        case K_BYTE: return integral && fabs(d) <= 127 ? 3 - b : 0;
        case K_NUMBER: return 6;
        case K_STRING: return 4;
        case K_CHARSEQ: return 3;
        case K_OBJECT: return 5;
        case K_BOOL: return 2 - b;
        default: return 0;
        }
    }
    case VT_BOOL:
        return k == K_BOOL ? 10 - b : k == K_OBJECT ? 5 : k == K_STRING ? 4 : k == K_CHARSEQ ? 3 : k == K_INT ? 1 : 0;
    case VT_DATE:
        return k == K_DATE ? 10 : k == K_OBJECT ? 5 : k == K_STRING ? 4 : k == K_CHARSEQ ? 3 : k == K_DOUBLE ? 2 : 0;
    case VT_ARRAY:
        return k == K_LIST ? 9 : k == K_ARRAY ? 8 : k == K_OBJECT ? 5 : 0;
    case VT_STRUCT:
        return k == K_MAP ? 9 : k == K_OBJECT ? 5 : 0;
    case VT_BINARY:
        return k == K_BYTES ? 10 : k == K_OBJECT ? 5 : k == K_STRING ? 2 : 0;
    default:
        return 0;
    }
}

/* best member by name (NULL = constructors), argument count and type score; *ambiguous when two different
 * signatures tie; *named counts members with that name at all (for the error message) */
static JMember *choose(JNIEnv *env, JMember *ms, int n, const char *name, int argc, Val *argv, int *hints,
                       int *ambiguous, int *named, int *packed) {
    JMember *best = NULL;
    double bests = -1;
    *ambiguous = 0; *named = 0; *packed = 0;
    for (int i = 0; i < n; i++) {
        JMember *m = &ms[i];
        if (name && kf_stricmp(m->name, name)) continue;
        (*named)++;
        /* exact arity, or a varargs method with the trailing arguments packed into its array */
        for (int pack = 0; pack < 2; pack++) {
            if (!pack && m->np != argc) continue;
            if (pack && (!m->varargs || argc < m->np - 1)) continue;
            double total = 0;
            int ok = 1;
            for (int a = 0; a < argc; a++) {
                JParam *pp = pack && a >= m->np - 1 ? &m->vcomp : &m->p[a];
                double sc = score_arg(env, argv[a], hints[a], pp);
                if (sc <= 0) { ok = 0; break; }
                total += sc;
            }
            if (!ok) continue;
            if (pack) total = total * 0.9 - 1;           /* prefer a fixed-arity match */
            if (m->bridge) total -= 0.5;
            if (name && !strcmp(m->name, name)) total += 0.1;
            if (total > bests + 1e-9) { best = m; bests = total; *ambiguous = 0; *packed = pack; }
        else if (fabs(total - bests) < 1e-9 && best) {
            int same = best->np == m->np;
            for (int a = 0; same && a < argc; a++) if (best->p[a].kind != m->p[a].kind) same = 0;
            if (!same) *ambiguous = 1;
            }
        }
    }
    return best;
}

/* ================================================================ Java -> CF */
static Val to_cf(JNIEnv *env, jobject o, int depth);

static KfObject *wrap(JNIEnv *env, jobject o) { return obj_new(NULL, o, env); }

static Val to_cf(JNIEnv *env, jobject o, int depth) {
    if (!o) return v_str("");
    if (j_IsInstanceOf(env, o, R.String)) return v_str(kfj_cstr(env, o));
    if (j_IsInstanceOf(env, o, R.Boolean)) return v_bool(j_CallBooleanMethodA(env, o, R.booleanValue, NULL));
    if (j_IsInstanceOf(env, o, R.Number)) return v_num(j_CallDoubleMethodA(env, o, R.doubleValue, NULL));
    if (j_IsInstanceOf(env, o, R.Character)) {
        /* as in ColdFusion: a Java char comes back as its character code (use Chr() to display it) */
        jstring s = j_CallObjectMethodA(env, o, R.toString, NULL);
        char *u = kfj_cstr(env, s);
        return v_num(*u ? first_char(u) : 0);
    }
    if (j_IsInstanceOf(env, o, R.Date)) {
        jlong ms = j_CallLongMethodA(env, o, R.getTime, NULL);
        return v_date(date_utc_to_local(ms / 86400000.0 + 25569.0));
    }
    if (j_IsInstanceOf(env, o, R.ByteArr)) {
        jsize n = j_GetArrayLength(env, o);
        char *p = kmalloc((size_t)n + 1);
        if (n) j_GetByteArrayRegion(env, o, 0, n, (jbyte *)p);
        return v_binary(p, (size_t)n);
    }
    if (depth < 32) {
        jclass c = j_GetObjectClass(env, o);
        int isarr = j_CallBooleanMethodA(env, c, R.isArray, NULL);
        j_DeleteLocalRef(env, c);
        if (isarr) {
            jvalue a[2]; a[0].l = o;
            int n = j_CallStaticIntMethodA(env, R.RArray, R.Array_getLength, a);
            Array *arr = array_new();
            for (int i = 0; i < n; i++) {
                a[1].i = i;
                j_PushLocalFrame(env, 16);
                jobject el = j_CallStaticObjectMethodA(env, R.RArray, R.Array_get, a);
                array_push(arr, to_cf(env, el, depth + 1));
                j_PopLocalFrame(env, NULL);
            }
            return v_arr(arr);
        }
        if (j_IsInstanceOf(env, o, R.List)) {
            int n = j_CallIntMethodA(env, o, R.List_size, NULL);
            Array *arr = array_new();
            for (int i = 0; i < n && !j_ExceptionCheck(env); i++) {
                jvalue a[1]; a[0].i = i;
                j_PushLocalFrame(env, 16);
                jobject el = j_CallObjectMethodA(env, o, R.List_get, a);
                array_push(arr, to_cf(env, el, depth + 1));
                j_PopLocalFrame(env, NULL);
            }
            j_ExceptionClear(env);
            return v_arr(arr);
        }
        if (j_IsInstanceOf(env, o, R.Map)) {
            Struct *st = struct_new();
            j_PushLocalFrame(env, 16);
            jobject ks = j_CallObjectMethodA(env, o, R.Map_keySet, NULL);
            jobjectArray keys = ks ? j_CallObjectMethodA(env, ks, R.Set_toArray, NULL) : NULL;
            int n = keys ? j_GetArrayLength(env, keys) : 0;
            for (int i = 0; i < n && !j_ExceptionCheck(env); i++) {
                j_PushLocalFrame(env, 16);
                jobject k = j_GetObjectArrayElement(env, keys, i);
                jvalue a[1]; a[0].l = k;
                jobject val = j_CallObjectMethodA(env, o, R.Map_get, a);
                jstring ksn = k ? j_CallObjectMethodA(env, k, R.toString, NULL) : NULL;
                struct_set(st, kfj_cstr(env, ksn), to_cf(env, val, depth + 1));
                j_PopLocalFrame(env, NULL);
            }
            j_ExceptionClear(env);
            j_PopLocalFrame(env, NULL);
            return v_struct(st);
        }
    }
    return v_object(wrap(env, o));
}

Val kfj_to_cf(JNIEnv *env, jobject o) { return to_cf(env, o, 0); }

/* ================================================================ invoking */
typedef struct JErr { int set; const char *msg, *detail, *extended; jobject exc; } JErr;

static void jerr(JErr *e, const char *msg, const char *detail) {
    if (e->set) return;
    e->set = 1; e->msg = msg; e->detail = detail;
}

/* a pending Java exception -> JErr. ColdFusion 4.5 put the class name of the exception in CFCATCH.Message. */
static int jerr_java(JNIEnv *env, JErr *e, const char *where) {
    char *cls, *msg; jobject g;
    if (!kfj_take_exception(env, &cls, &msg, &g)) return 0;
    if (e->set) { if (g) j_DeleteGlobalRef(env, g); return 1; }
    e->set = 1;
    e->msg = cls;
    e->detail = kprintf("%s threw %s%s%s", where, cls, *msg ? ": " : "", msg);
    e->extended = msg;
    e->exc = g;
    return 1;
}

static void ensure_constructed(JNIEnv *env, KfObject *o, int *ok, const char **why) {
    *ok = 1; *why = NULL;
    if (o->inst) return;
    JClassInfo *jc = o->jc;
    JMember *ct = NULL;
    for (int i = 0; jc && i < jc->nct; i++) if (jc->ct[i].np == 0) ct = &jc->ct[i];
    if (!ct) {
        *ok = 0;
        *why = jc && jc->is_interface ? kprintf("%s is an interface and cannot be instantiated.", jc->name)
                                      : kprintf("The class %s has no public constructor that takes no arguments; call init() "
                                                "with the constructor's arguments first.", jc ? jc->name : "?");
        return;
    }
    jvalue a[1];
    a[0].l = j_NewObjectArray(env, 0, R.Object, NULL);
    jobject inst = j_CallObjectMethodA(env, ct->ref, R.Ctor_newInstance, a);
    if (j_ExceptionCheck(env) || !inst) { *ok = 0; return; }   /* the caller reads the exception */
    jobject g = j_NewGlobalRef(env, inst);
    pthread_mutex_lock(&obj_mu);
    if (!o->inst) { o->inst = g; g = NULL; __sync_fetch_and_add(&g_objects, 1); }
    pthread_mutex_unlock(&obj_mu);
    if (g) j_DeleteGlobalRef(env, g);
}

static jobjectArray build_args(JNIEnv *env, JMember *m, int argc, Val *argv, int *hints, int packed) {
    if (packed) {
        int nf = m->np - 1;
        jobjectArray arr = j_NewObjectArray(env, m->np, R.Object, NULL);
        for (int i = 0; arr && i < nf && !j_ExceptionCheck(env); i++) {
            jobject a = to_param(env, argv[i], hints[i], &m->p[i]);
            j_SetObjectArrayElement(env, arr, i, a);
            if (a) j_DeleteLocalRef(env, a);
        }
        jvalue a[3];
        a[0].l = m->vcomp.cls; a[1].i = argc - nf;
        jobject va = j_CallStaticObjectMethodA(env, R.RArray, R.Array_newInstance, a);
        for (int i = nf; va && i < argc && !j_ExceptionCheck(env); i++) {
            a[0].l = va; a[1].i = i - nf; a[2].l = to_param(env, argv[i], hints[i], &m->vcomp);
            j_CallStaticObjectMethodA(env, R.RArray, R.Array_set, a);
            if (a[2].l) j_DeleteLocalRef(env, a[2].l);
        }
        if (arr) j_SetObjectArrayElement(env, arr, nf, va);
        return arr;
    }
    jobjectArray arr = j_NewObjectArray(env, argc, R.Object, NULL);
    for (int i = 0; arr && i < argc && !j_ExceptionCheck(env); i++) {
        jobject a = to_param(env, argv[i], hints[i], &m->p[i]);
        j_SetObjectArrayElement(env, arr, i, a);
        if (a) j_DeleteLocalRef(env, a);
    }
    return arr;
}

static const char *sig_text(JMember *m, const char *cls) {
    (void)m;
    return cls;
}

static const char *argtypes(int argc, Val *argv, int *hints) {
    static const char *hn[] = {"", "int", "long", "double", "float", "boolean", "String", "null"};
    Buf b; buf_init(&b);
    for (int i = 0; i < argc; i++) {
        if (i) buf_puts(&b, ", ");
        buf_puts(&b, hints[i] ? hn[hints[i]] : v_typename(argv[i]));
    }
    return buf_cstr(&b);
}

static void throw_jerr(Ctx *c, Expr *where, KfObject *o, JErr *e) __attribute__((noreturn));
static void throw_jerr(Ctx *c, Expr *where, KfObject *o, JErr *e) {
    if (o && e->exc) {
        /* GetException(obj) returns it */
        JNIEnv *env = env_get();
        pthread_mutex_lock(&obj_mu);
        jobject old = o->exc;
        o->exc = e->exc;
        pthread_mutex_unlock(&obj_mu);
        if (old && env) j_DeleteGlobalRef(env, old);
    } else if (e->exc) {
        JNIEnv *env = env_get();
        if (env) j_DeleteGlobalRef(env, e->exc);
    }
    KfError *err = kf_error_new(KFJ_ERRTYPE, kf_html_escape(e->msg), kf_html_escape(e->detail));
    if (e->extended) err->extended = kstrdup(e->extended);
    if (where && where->line) { err->line = where->line; err->col = where->col; }
    if (where && where->src && where->srclen > 0) {
        err->heading = "An error occurred while evaluating the expression:";
        err->snippet = kstrndup(where->src, where->srclen);
    }
    kf_throw_err(c->rs, err);
}

static void clear_exc(JNIEnv *env, KfObject *o) {
    if (!o->exc) return;
    pthread_mutex_lock(&obj_mu);
    jobject old = o->exc; o->exc = NULL;
    pthread_mutex_unlock(&obj_mu);
    if (old) j_DeleteGlobalRef(env, old);
}

/* obj.method(args) */
Val java_invoke(Ctx *c, Expr *call, Val ov, const char *mname) {
    KfObject *o = ov.u.obj;
    int argc = call->nargs;
    Val *argv = kmalloc(sizeof(Val) * (argc ? argc : 1));
    int *hints = kmalloc(sizeof(int) * (argc ? argc : 1));
    for (int i = 0; i < argc; i++) {
        Expr *a = call->args[i];
        if (a->k == E_CALL && !kf_stricmp(a->name, "javacast") && a->nargs == 2) {
            const char *t = eval_str(c, a->args[0]);
            argv[i] = javacast_value(c, a, t, eval(c, a->args[1]), &hints[i]);
        } else {
            argv[i] = eval(c, a);
            hints[i] = hint_get(argv[i]);
        }
        if (argv[i].t == VT_QUERY)
            kf_throw_at(c, a, KFJ_ERRTYPE, "Queries cannot be passed to Java methods.",
                        "Pass the values of the query's columns (for example as arrays) instead.");
    }
    JNIEnv *env = kfj_env(c);
    JErr err = {0};
    Val result = v_str("");
    int is_init = !kf_stricmp(mname, "init");
    j_PushLocalFrame(env, 64 + argc * 4);
    JClassInfo *jc = obj_class(env, o);
    const char *cname = jc ? jc->name : "?";
    int amb = 0, named = 0;
    if (is_init && !o->inst) {
        /* obj.init(args) runs a constructor, as in ColdFusion 4.5 */
        int packed = 0;
        JMember *ct = choose(env, jc->ct, jc->nct, NULL, argc, argv, hints, &amb, &named, &packed);
        if (!ct)
            jerr(&err, kprintf("No constructor of %s takes %d argument%s of the given types.", cname, argc, argc == 1 ? "" : "s"),
                 kprintf("The class has %d public constructor%s. Arguments: (%s). Use JavaCast() to choose a constructor.",
                         jc->nct, jc->nct == 1 ? "" : "s", argtypes(argc, argv, hints)));
        else if (amb)
            jerr(&err, kprintf("The constructor call for %s is ambiguous.", cname),
                 kprintf("More than one constructor of %s matches the arguments (%s). Use JavaCast() to choose one.",
                         cname, argtypes(argc, argv, hints)));
        else {
            jvalue a[1];
            a[0].l = build_args(env, ct, argc, argv, hints, packed);
            jobject inst = j_ExceptionCheck(env) ? NULL : j_CallObjectMethodA(env, ct->ref, R.Ctor_newInstance, a);
            if (!jerr_java(env, &err, kprintf("The constructor of %s", cname)) && inst) {
                jobject g = j_NewGlobalRef(env, inst);
                pthread_mutex_lock(&obj_mu);
                if (!o->inst) { o->inst = g; g = NULL; __sync_fetch_and_add(&g_objects, 1); }
                pthread_mutex_unlock(&obj_mu);
                if (g) j_DeleteGlobalRef(env, g);
                result = ov;
            }
        }
    } else {
        int packed = 0;
        JMember *m = choose(env, jc->m, jc->nm, mname, argc, argv, hints, &amb, &named, &packed);
        if (!m && is_init)
            jerr(&err, kprintf("The object of class %s has already been initialized.", cname),
                 "init() calls a constructor and can only be used once, before any other method of the object is called.");
        else if (!m)
            jerr(&err, kprintf("The method %s could not be found in the Java class %s.", mname, cname),
                 named ? kprintf("The class has %d public method%s named %s, but none of them takes %d argument%s of the types "
                                 "given (%s). Use JavaCast() to choose an overloaded method.", named, named == 1 ? "" : "s",
                                 mname, argc, argc == 1 ? "" : "s", argtypes(argc, argv, hints))
                       : kprintf("There is no public method named %s. Method names are not case sensitive; check the "
                                 "spelling and the documentation of %s.", mname, cname));
        else if (amb)
            jerr(&err, kprintf("The method %s of %s is overloaded and the call is ambiguous.", mname, cname),
                 kprintf("More than one method %s takes the arguments (%s). Use JavaCast() to say which Java type to pass.",
                         mname, argtypes(argc, argv, hints)));
        else {
            int ok = 1; const char *why = NULL;
            if (!m->is_static) ensure_constructed(env, o, &ok, &why);
            if (!ok) {
                if (!jerr_java(env, &err, kprintf("The default constructor of %s", cname)))
                    jerr(&err, kprintf("Unable to create an instance of %s.", cname), why);
            } else {
                jvalue a[2];
                a[0].l = m->is_static ? NULL : o->inst;
                a[1].l = build_args(env, m, argc, argv, hints, packed);
                jobject r = j_ExceptionCheck(env) ? NULL : j_CallObjectMethodA(env, m->ref, R.Method_invoke, a);
                if (!jerr_java(env, &err, kprintf("The method %s of %s", m->name, cname))) {
                    result = to_cf(env, r, 0);
                    clear_exc(env, o);             /* each successful call resets GetException() */
                }
            }
        }
    }
    j_ExceptionClear(env);
    j_PopLocalFrame(env, NULL);
    if (err.set) throw_jerr(c, call, o, &err);
    (void)sig_text;
    return result;
}

static JMember *find_field(JClassInfo *jc, const char *name) {
    JMember *ci = NULL;
    for (int i = 0; jc && i < jc->nf; i++) {
        if (!strcmp(jc->f[i].name, name)) return &jc->f[i];
        if (!ci && !kf_stricmp(jc->f[i].name, name)) ci = &jc->f[i];
    }
    return ci;
}

/* obj.field */
int java_get_field(Ctx *c, Expr *where, Val ov, const char *name, Val *out, int soft) {
    KfObject *o = ov.u.obj;
    JNIEnv *env = kfj_env(c);
    JErr err = {0};
    int found = 0;
    j_PushLocalFrame(env, 32);
    JClassInfo *jc = obj_class(env, o);
    JMember *f = find_field(jc, name);
    if (f) {
        int ok = 1; const char *why = NULL;
        if (!f->is_static) ensure_constructed(env, o, &ok, &why);
        if (!ok) {
            if (!jerr_java(env, &err, kprintf("The default constructor of %s", jc->name)))
                jerr(&err, kprintf("Unable to create an instance of %s.", jc->name), why);
        } else {
            jvalue a[1]; a[0].l = f->is_static ? NULL : o->inst;
            jobject r = j_CallObjectMethodA(env, f->ref, R.Field_get, a);
            if (!jerr_java(env, &err, kprintf("Reading the field %s of %s", f->name, jc->name))) { *out = to_cf(env, r, 0); found = 1; }
        }
    } else if (!soft) {
        jerr(&err, kprintf("The field %s could not be found in the Java class %s.", name, jc ? jc->name : "?"),
             "Only public fields can be read. To call a method, write obj.method() with parentheses.");
    }
    j_ExceptionClear(env);
    j_PopLocalFrame(env, NULL);
    if (err.set) { if (soft) { if (err.exc) j_DeleteGlobalRef(env, err.exc); return 0; } throw_jerr(c, where, o, &err); }
    return found;
}

/* <cfset obj.field = value> */
void java_set_field(Ctx *c, Expr *where, Val ov, const char *name, Val v) {
    KfObject *o = ov.u.obj;
    int hint = hint_get(v);
    JNIEnv *env = kfj_env(c);
    JErr err = {0};
    j_PushLocalFrame(env, 32);
    JClassInfo *jc = obj_class(env, o);
    JMember *f = find_field(jc, name);
    if (!f)
        jerr(&err, kprintf("The field %s could not be found in the Java class %s.", name, jc ? jc->name : "?"),
             "Only public fields can be set.");
    else if (score_arg(env, v, hint, &f->type) <= 0)
        jerr(&err, kprintf("The value cannot be converted for the field %s of %s.", f->name, jc->name),
             kprintf("A %s cannot be stored in this field. Use JavaCast() to convert it.", hint ? "value of that type" : v_typename(v)));
    else {
        int ok = 1; const char *why = NULL;
        if (!f->is_static) ensure_constructed(env, o, &ok, &why);
        if (!ok) {
            if (!jerr_java(env, &err, kprintf("The default constructor of %s", jc->name)))
                jerr(&err, kprintf("Unable to create an instance of %s.", jc->name), why);
        } else {
            jvalue a[2];
            a[0].l = f->is_static ? NULL : o->inst;
            a[1].l = to_param(env, v, hint, &f->type);
            j_CallVoidMethodA(env, f->ref, R.Field_set, a);
            jerr_java(env, &err, kprintf("Setting the field %s of %s", f->name, jc->name));
        }
    }
    j_ExceptionClear(env);
    j_PopLocalFrame(env, NULL);
    if (err.set) throw_jerr(c, where, o, &err);
}

/* ================================================================ creating objects */
static Val create_java(Ctx *c, Expr *where, const char *cls) {
    JNIEnv *env = kfj_env(c);
    char *dotted = kstrdup(kf_trim(cls));
    for (char *p = dotted; *p; p++) if (*p == '/') *p = '.';     /* "weblogic/jndi/Environment" worked too */
    JErr err = {0};
    KfObject *o = NULL;
    j_PushLocalFrame(env, 32);
    jclass k = kfj_class_for_name(env, dotted);
    if (!k || j_ExceptionCheck(env)) {
        char *ecls = "", *emsg = "";
        kfj_take_exception(env, &ecls, &emsg, NULL);
        if (strstr(ecls, "ClassNotFound") || strstr(ecls, "NoClassDefFound"))
            jerr(&err, kprintf("Object Instantiation Exception. The Java class %s could not be found.", dotted),
                 kprintf("%s: %s. Class names are case sensitive. Put the class on the Class Path set on the Java page of "
                         "the KoldFusion Administrator, or into %s/java/classes.", ecls, emsg, G.root));
        else
            jerr(&err, kprintf("Object Instantiation Exception. The Java class %s could not be loaded.", dotted),
                 kprintf("%s: %s", ecls, emsg));
    } else {
        o = obj_new(jci_get(env, k), NULL, env);   /* loaded but not constructed: init() or the first call does that */
    }
    j_ExceptionClear(env);
    j_PopLocalFrame(env, NULL);
    if (err.set) throw_jerr(c, where, NULL, &err);
    return v_object(o);
}

static void corba_error(Ctx *c, Expr *where, const char *cls) {
    kf_throw_at(c, where, "Object", "Unable to initialise the CORBA ORB.",
                kprintf("CFOBJECT TYPE=\"CORBA\" (object %s) needs the VisiBroker for C++ ORB, which is not part of KoldFusion, "
                        "and the Java runtime no longer includes an ORB (Java IDL was removed in Java 11).",
                        kf_html_escape(cls)));
}

static void com_error(Ctx *c, Expr *where, const char *cls) {
    kf_throw_at(c, where, "Object", "COM objects are not supported on this platform.",
                kprintf("KoldFusion for UNIX cannot create the COM object %s. On UNIX, CFOBJECT and CreateObject() "
                        "support TYPE=\"Java\".", kf_html_escape(cls)));
}

F(createobject) {
    const char *type = fa_str(c, call, argv, 0);
    tag_security_check(c, "cfobject");
    const char *cls = argc > 1 ? fa_str(c, call, argv, 1) : "";
    if (!kf_stricmp(type, "com")) com_error(c, call, cls);
    if (!kf_stricmp(type, "corba")) corba_error(c, call, cls);
    if (kf_stricmp(type, "java"))
        kf_throw_at(c, call, "Expression", kprintf("Invalid object type %s.", kf_html_escape(type)),
                    "The first parameter of CreateObject must be COM, CORBA or JAVA.");
    if (argc < 2) kf_throw_at(c, call, "Expression", "Parameter validation error for function CREATEOBJECT.",
                              "CreateObject(\"Java\", class) needs the name of the Java class.");
    return create_java(c, call, cls);
}

/* <CFOBJECT TYPE="Java" ACTION="Create" CLASS="java.util.Hashtable" NAME="h"> */
void tag_object(Ctx *c, Node *n, int *flow) {
    (void)flow;
    tag_security_check(c, "cfobject");
    const char *type = attr_str(c, n, "type", "COM");
    const char *cls = attr_str(c, n, "class", "");
    if (!kf_stricmp(type, "com")) com_error(c, NULL, cls);
    if (!kf_stricmp(type, "corba")) corba_error(c, NULL, cls);
    if (kf_stricmp(type, "java"))
        kf_throw(c, "Application", "Attribute validation error for tag CFOBJECT.",
                 kprintf("The value of the attribute TYPE, which is currently \"%s\", must be one of COM, CORBA or JAVA.",
                         kf_html_escape(type)));
    const char *action = attr_str(c, n, "action", "Create");
    if (kf_stricmp(action, "create"))
        kf_throw(c, "Application", "Attribute validation error for tag CFOBJECT.",
                 kprintf("The value of the attribute ACTION, which is currently \"%s\", must be CREATE for Java objects.",
                         kf_html_escape(action)));
    require_attr(c, n, "class");
    const char *name = require_attr(c, n, "name");
    assign_path(c, name, create_java(c, NULL, cls));
}

/* GetException(obj): the Java exception thrown by the last method call on obj (introduced with ColdFusion 5) */
F(getexception) {
    (void)argc;
    if (argv[0].t != VT_OBJECT)
        kf_throw_at(c, call, "Expression", "Parameter 1 of function GetException must be a Java object.",
                    kprintf("The value is a %s.", v_typename(argv[0])));
    KfObject *o = argv[0].u.obj;
    JNIEnv *env = kfj_env(c);
    pthread_mutex_lock(&obj_mu);
    jobject x = o->exc ? j_NewLocalRef(env, o->exc) : NULL;
    pthread_mutex_unlock(&obj_mu);
    if (!x) {
        /* no exception: an object wrapping java.lang.Throwable's absence would be useless; CF returned an empty object */
        return v_str("");
    }
    KfObject *w = obj_new(NULL, x, env);
    j_DeleteLocalRef(env, x);
    return v_object(w);
}

/* ================================================================ Administrator */
F(kfusion_java) {
    const char *p = c->rs->cur_tpl ? c->rs->cur_tpl->path : "";
    char *dir = kf_path_join(G.webroot, "CFIDE/administrator");
    if (strncmp(p, dir, strlen(dir)))
        kf_throw_at(c, call, "Security", "The function KFUSION_JAVA is reserved for the KoldFusion Administrator.",
                    "Undocumented KFUSION_ functions may only be called by templates in /CFIDE/administrator.");
    const char *action = argc > 0 ? fa_str(c, call, argv, 0) : "status";
    if (!kf_stricmp(action, "load")) jvm_ensure();
    Struct *s = struct_new();
    char lib[PATH_MAX] = "", src[64] = "";
    int found = g_state == 1 ? 1 : jvm_find(lib, sizeof lib, src, sizeof src);
    struct_set(s, "Loaded", v_bool(g_state == 1));
    struct_set(s, "Failed", v_bool(g_state == -1));
    struct_set(s, "Found", v_bool(found));
    struct_set(s, "Path", v_strdup(g_state == 1 ? g_libpath : lib));
    struct_set(s, "Source", v_strdup(g_state == 1 ? g_libsource : src));
    struct_set(s, "Version", v_strdup(g_version));
    struct_set(s, "Error", v_strdup(g_error));
    struct_set(s, "ClassPath", v_strdup(g_classpath));
    struct_set(s, "Options", v_strdup(g_options));
    struct_set(s, "LoadedAt", g_state == 1 ? v_date(g_loaded_at) : v_str(""));
    struct_set(s, "Threads", v_num(g_attached));
    struct_set(s, "Objects", v_num(g_objects));
    const char *jar = kfj_cfx_jar();
    struct_set(s, "CFXJar", v_strdup(jar));
    struct_set(s, "CFXJarExists", v_bool(file_exists(jar)));
    struct_set(s, "ClassesDir", v_strdup(kf_path_join(G.root, "java/classes")));
    double used = 0, total = 0, max = 0;
    if (g_state == 1) {
        JNIEnv *env = env_get();
        if (env) {
            j_PushLocalFrame(env, 8);
            jobject rt = j_CallStaticObjectMethodA(env, R.Runtime, R.getRuntime, NULL);
            if (rt) {
                total = (double)j_CallLongMethodA(env, rt, R.totalMemory, NULL);
                used = total - (double)j_CallLongMethodA(env, rt, R.freeMemory, NULL);
                max = (double)j_CallLongMethodA(env, rt, R.maxMemory, NULL);
            }
            j_ExceptionClear(env);
            j_PopLocalFrame(env, NULL);
        }
    }
    struct_set(s, "HeapUsedKB", v_num(floor(used / 1024)));
    struct_set(s, "HeapTotalKB", v_num(floor(total / 1024)));
    struct_set(s, "HeapMaxKB", v_num(floor(max / 1024)));
    return v_struct(s);
}
