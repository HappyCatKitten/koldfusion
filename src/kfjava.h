/*
 * kfjava.h - internals shared by java.c (the embedded JVM, Java objects) and
 * java_ext.c (Java CFX tags, CFSERVLET).
 */
#ifndef KFJAVA_H
#define KFJAVA_H

#include "engine.h"
#include "kfjni.h"

/* JavaCast() hints */
enum { H_NONE = 0, H_INT, H_LONG, H_DOUBLE, H_FLOAT, H_BOOL, H_STRING, H_NULL, H_SHORT, H_BYTE, H_CHAR };

/* the CFCATCH type of every Java/servlet/CFX-in-Java failure, as in ColdFusion 4.5 */
#define KFJ_ERRTYPE "Object"

JNIEnv *kfj_env(Ctx *c);                       /* loads the JVM on first use and attaches this thread; throws if impossible */
int     kfj_available(char *why, size_t wl);   /* 1 if a JVM is (or can be) loaded */
jstring kfj_str(JNIEnv *env, const char *s);
jstring kfj_strn(JNIEnv *env, const char *s, size_t n);
char   *kfj_cstr(JNIEnv *env, jstring s);      /* arena UTF-8 copy ("" for null) */
jobjectArray kfj_strarray(JNIEnv *env, int n, const char *const *items);
jclass  kfj_class_for_name(JNIEnv *env, const char *dotted);   /* local ref, NULL with exception pending */
jclass  kfj_object_class(void);                /* global ref to java.lang.Object */
Val     kfj_to_cf(JNIEnv *env, jobject o);     /* Java -> CF (strings, numbers, arrays, Vector, Hashtable...) */
jobject kfj_to_java(JNIEnv *env, Val v, int hint);          /* CF -> Java, natural mapping (local ref) */
/* take (and clear) the pending exception; *gref (optional) receives a global ref to the Throwable */
int     kfj_take_exception(JNIEnv *env, char **cls, char **msg, jobject *gref);
jmethodID kfj_static_method(JNIEnv *env, jclass c, const char *name, const char *sig);
const char *kfj_cfx_jar(void);                 /* path of cfx.jar that is put on the class path */
int     kfj_int_value(JNIEnv *env, jobject boxed, int def);
jobject kfj_box_int(JNIEnv *env, int i);

#endif
