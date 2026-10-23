/*
 * kfjni.h - a minimal, hand-written subset of the Java Native Interface.
 *
 * KoldFusion loads the Java Virtual Machine at run time with dlopen(), so it
 * must build on machines without a JDK (and therefore without <jni.h>). The
 * JNI is a stable binary interface: a JNIEnv is a pointer to a table of
 * function pointers whose slot numbers are fixed by the JNI specification
 * (and have not changed since JDK 1.2). We declare the handful of types we
 * need and call the functions through their slot numbers.
 *
 * Only the functions KoldFusion uses are wrapped below. The slot numbers were
 * checked against the jni.h of JDK 1.2 through 17.
 */
#ifndef KFJNI_H
#define KFJNI_H

#include <stdint.h>

typedef int32_t  jint;
typedef int64_t  jlong;
typedef int8_t   jbyte;
typedef uint8_t  jboolean;
typedef uint16_t jchar;
typedef int16_t  jshort;
typedef float    jfloat;
typedef double   jdouble;
typedef jint     jsize;

typedef void *jobject;
typedef jobject jclass, jstring, jarray, jobjectArray, jthrowable, jbyteArray;
typedef void *jmethodID;
typedef void *jfieldID;

typedef union jvalue {
    jboolean z; jbyte b; jchar c; jshort s; jint i; jlong j; jfloat f; jdouble d; jobject l;
} jvalue;

typedef void *const *JNIEnv;       /* JNIEnv *env: (*env)[slot] is a function */
typedef void *const *JavaVM;       /* JavaVM *vm:  (*vm)[slot]  is a function */

#define JNI_OK          0
#define JNI_EDETACHED   (-2)
#define JNI_FALSE       0
#define JNI_TRUE        1
#define JNI_VERSION_1_2 0x00010002

typedef struct JavaVMOption { char *optionString; void *extraInfo; } JavaVMOption;
typedef struct JavaVMInitArgs { jint version; jint nOptions; JavaVMOption *options; jboolean ignoreUnrecognized; } JavaVMInitArgs;
typedef struct JavaVMAttachArgs { jint version; char *name; jobject group; } JavaVMAttachArgs;

typedef jint (*JNI_CreateJavaVM_fn)(JavaVM **pvm, void **penv, void *args);
typedef jint (*JNI_GetCreatedJavaVMs_fn)(JavaVM **vms, jsize n, jsize *count);

/* ---- JavaVM (invocation interface) slots */
#define JF_VM(vm, slot, type) ((type)((*(vm))[slot]))
static inline jint jvm_AttachCurrentThreadAsDaemon(JavaVM *vm, JNIEnv **env, void *args)
    { return JF_VM(vm, 7, jint (*)(JavaVM *, JNIEnv **, void *))(vm, env, args); }
static inline jint jvm_DetachCurrentThread(JavaVM *vm)
    { return JF_VM(vm, 5, jint (*)(JavaVM *))(vm); }
static inline jint jvm_GetEnv(JavaVM *vm, JNIEnv **env, jint version)
    { return JF_VM(vm, 6, jint (*)(JavaVM *, JNIEnv **, jint))(vm, env, version); }

/* ---- JNIEnv (native interface) slots */
#define JF(env, slot, type) ((type)((*(env))[slot]))
static inline jint j_GetVersion(JNIEnv *e) { return JF(e, 4, jint (*)(JNIEnv *))(e); }
static inline jclass j_FindClass(JNIEnv *e, const char *n) { return JF(e, 6, jclass (*)(JNIEnv *, const char *))(e, n); }
static inline jboolean j_IsAssignableFrom(JNIEnv *e, jclass a, jclass b)
    { return JF(e, 11, jboolean (*)(JNIEnv *, jclass, jclass))(e, a, b); }
static inline jint j_ThrowNew(JNIEnv *e, jclass c, const char *m) { return JF(e, 14, jint (*)(JNIEnv *, jclass, const char *))(e, c, m); }
static inline jthrowable j_ExceptionOccurred(JNIEnv *e) { return JF(e, 15, jthrowable (*)(JNIEnv *))(e); }
static inline void j_ExceptionClear(JNIEnv *e) { JF(e, 17, void (*)(JNIEnv *))(e); }
static inline jint j_PushLocalFrame(JNIEnv *e, jint cap) { return JF(e, 19, jint (*)(JNIEnv *, jint))(e, cap); }
static inline jobject j_PopLocalFrame(JNIEnv *e, jobject r) { return JF(e, 20, jobject (*)(JNIEnv *, jobject))(e, r); }
static inline jobject j_NewGlobalRef(JNIEnv *e, jobject o) { return JF(e, 21, jobject (*)(JNIEnv *, jobject))(e, o); }
static inline void j_DeleteGlobalRef(JNIEnv *e, jobject o) { JF(e, 22, void (*)(JNIEnv *, jobject))(e, o); }
static inline void j_DeleteLocalRef(JNIEnv *e, jobject o) { JF(e, 23, void (*)(JNIEnv *, jobject))(e, o); }
static inline jboolean j_IsSameObject(JNIEnv *e, jobject a, jobject b)
    { return JF(e, 24, jboolean (*)(JNIEnv *, jobject, jobject))(e, a, b); }
static inline jobject j_NewLocalRef(JNIEnv *e, jobject o) { return JF(e, 25, jobject (*)(JNIEnv *, jobject))(e, o); }
static inline jobject j_NewObjectA(JNIEnv *e, jclass c, jmethodID m, const jvalue *a)
    { return JF(e, 30, jobject (*)(JNIEnv *, jclass, jmethodID, const jvalue *))(e, c, m, a); }
static inline jclass j_GetObjectClass(JNIEnv *e, jobject o) { return JF(e, 31, jclass (*)(JNIEnv *, jobject))(e, o); }
static inline jboolean j_IsInstanceOf(JNIEnv *e, jobject o, jclass c)
    { return JF(e, 32, jboolean (*)(JNIEnv *, jobject, jclass))(e, o, c); }
static inline jmethodID j_GetMethodID(JNIEnv *e, jclass c, const char *n, const char *s)
    { return JF(e, 33, jmethodID (*)(JNIEnv *, jclass, const char *, const char *))(e, c, n, s); }
static inline jobject j_CallObjectMethodA(JNIEnv *e, jobject o, jmethodID m, const jvalue *a)
    { return JF(e, 36, jobject (*)(JNIEnv *, jobject, jmethodID, const jvalue *))(e, o, m, a); }
static inline jboolean j_CallBooleanMethodA(JNIEnv *e, jobject o, jmethodID m, const jvalue *a)
    { return JF(e, 39, jboolean (*)(JNIEnv *, jobject, jmethodID, const jvalue *))(e, o, m, a); }
static inline jint j_CallIntMethodA(JNIEnv *e, jobject o, jmethodID m, const jvalue *a)
    { return JF(e, 51, jint (*)(JNIEnv *, jobject, jmethodID, const jvalue *))(e, o, m, a); }
static inline jlong j_CallLongMethodA(JNIEnv *e, jobject o, jmethodID m, const jvalue *a)
    { return JF(e, 54, jlong (*)(JNIEnv *, jobject, jmethodID, const jvalue *))(e, o, m, a); }
static inline jdouble j_CallDoubleMethodA(JNIEnv *e, jobject o, jmethodID m, const jvalue *a)
    { return JF(e, 60, jdouble (*)(JNIEnv *, jobject, jmethodID, const jvalue *))(e, o, m, a); }
static inline void j_CallVoidMethodA(JNIEnv *e, jobject o, jmethodID m, const jvalue *a)
    { JF(e, 63, void (*)(JNIEnv *, jobject, jmethodID, const jvalue *))(e, o, m, a); }
static inline jmethodID j_GetStaticMethodID(JNIEnv *e, jclass c, const char *n, const char *s)
    { return JF(e, 113, jmethodID (*)(JNIEnv *, jclass, const char *, const char *))(e, c, n, s); }
static inline jobject j_CallStaticObjectMethodA(JNIEnv *e, jclass c, jmethodID m, const jvalue *a)
    { return JF(e, 116, jobject (*)(JNIEnv *, jclass, jmethodID, const jvalue *))(e, c, m, a); }
static inline jboolean j_CallStaticBooleanMethodA(JNIEnv *e, jclass c, jmethodID m, const jvalue *a)
    { return JF(e, 119, jboolean (*)(JNIEnv *, jclass, jmethodID, const jvalue *))(e, c, m, a); }
static inline jint j_CallStaticIntMethodA(JNIEnv *e, jclass c, jmethodID m, const jvalue *a)
    { return JF(e, 131, jint (*)(JNIEnv *, jclass, jmethodID, const jvalue *))(e, c, m, a); }
static inline jlong j_CallStaticLongMethodA(JNIEnv *e, jclass c, jmethodID m, const jvalue *a)
    { return JF(e, 134, jlong (*)(JNIEnv *, jclass, jmethodID, const jvalue *))(e, c, m, a); }
static inline jstring j_NewString(JNIEnv *e, const jchar *u, jsize n)
    { return JF(e, 163, jstring (*)(JNIEnv *, const jchar *, jsize))(e, u, n); }
static inline jsize j_GetStringLength(JNIEnv *e, jstring s) { return JF(e, 164, jsize (*)(JNIEnv *, jstring))(e, s); }
static inline jsize j_GetArrayLength(JNIEnv *e, jarray a) { return JF(e, 171, jsize (*)(JNIEnv *, jarray))(e, a); }
static inline jobjectArray j_NewObjectArray(JNIEnv *e, jsize n, jclass c, jobject init)
    { return JF(e, 172, jobjectArray (*)(JNIEnv *, jsize, jclass, jobject))(e, n, c, init); }
static inline jobject j_GetObjectArrayElement(JNIEnv *e, jobjectArray a, jsize i)
    { return JF(e, 173, jobject (*)(JNIEnv *, jobjectArray, jsize))(e, a, i); }
static inline void j_SetObjectArrayElement(JNIEnv *e, jobjectArray a, jsize i, jobject v)
    { JF(e, 174, void (*)(JNIEnv *, jobjectArray, jsize, jobject))(e, a, i, v); }
static inline jbyteArray j_NewByteArray(JNIEnv *e, jsize n) { return JF(e, 176, jbyteArray (*)(JNIEnv *, jsize))(e, n); }
static inline void j_GetByteArrayRegion(JNIEnv *e, jbyteArray a, jsize s, jsize n, jbyte *buf)
    { JF(e, 200, void (*)(JNIEnv *, jbyteArray, jsize, jsize, jbyte *))(e, a, s, n, buf); }
static inline void j_SetByteArrayRegion(JNIEnv *e, jbyteArray a, jsize s, jsize n, const jbyte *buf)
    { JF(e, 208, void (*)(JNIEnv *, jbyteArray, jsize, jsize, const jbyte *))(e, a, s, n, buf); }
static inline void j_GetStringRegion(JNIEnv *e, jstring str, jsize s, jsize n, jchar *buf)
    { JF(e, 220, void (*)(JNIEnv *, jstring, jsize, jsize, jchar *))(e, str, s, n, buf); }
static inline jboolean j_ExceptionCheck(JNIEnv *e) { return JF(e, 228, jboolean (*)(JNIEnv *))(e); }

#endif
