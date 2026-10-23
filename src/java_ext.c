/*
 * java_ext.c - Java CFX tags and CFSERVLET/CFSERVLETPARAM.
 *
 * Both run Java code from kfroot/java/cfx.jar (com.gibson.kf.Bridge, built from java/src by "make" when a JDK is
 * found). The C side passes plain strings and arrays in one JNI call and applies the results (page output,
 * variables, queries, servlet attributes) after the call has returned, so Java never calls back into the engine
 * and no CFML error is ever thrown while a JNI local frame is open.
 *
 * ColdFusion 4.5 sent CFSERVLET requests to a JRun server (JRUNPROXY); KoldFusion runs the servlet in the
 * embedded JVM against a small Servlet API 2.2 implementation that ships in cfx.jar.
 */
#define _GNU_SOURCE
#include "kfjava.h"
#include <stdlib.h>
#include <pthread.h>
#include <sys/stat.h>

/* ================================================================ the bridge class */
static jclass g_bridge;
static jmethodID g_run_cfx, g_run_servlet;
static pthread_mutex_t bridge_mu = PTHREAD_MUTEX_INITIALIZER;

static jclass bridge(Ctx *c, JNIEnv *env, const char *what) {
    if (g_bridge) return g_bridge;
    pthread_mutex_lock(&bridge_mu);
    if (!g_bridge) {
        j_PushLocalFrame(env, 8);
        jclass b = kfj_class_for_name(env, "com.gibson.kf.Bridge");
        if (b && !j_ExceptionCheck(env)) {
            g_run_cfx = kfj_static_method(env, b, "runCFX",
                "(Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;"
                "[Ljava/lang/String;I[Ljava/lang/String;[Ljava/lang/String;Z)[Ljava/lang/Object;");
            g_run_servlet = kfj_static_method(env, b, "runServlet",
                "(Ljava/lang/String;[Ljava/lang/String;[Ljava/lang/String;[Ljava/lang/String;[Ljava/lang/String;"
                "[Ljava/lang/String;[Ljava/lang/String;[Ljava/lang/Object;[BLjava/lang/String;I)[Ljava/lang/Object;");
            if (g_run_cfx && g_run_servlet) g_bridge = j_NewGlobalRef(env, b);
        }
        j_ExceptionClear(env);
        j_PopLocalFrame(env, NULL);
    }
    pthread_mutex_unlock(&bridge_mu);
    if (g_bridge) return g_bridge;
    struct stat st;
    const char *jar = kfj_cfx_jar();
    if (stat(jar, &st) != 0)
        kf_throw(c, KFJ_ERRTYPE, kprintf("%s needs cfx.jar, which was not found.", what),
                 kprintf("The CFX Jar Path (%s) does not exist. Build it with <TT>make</TT> on a machine with a Java "
                         "Development Kit (javac), or correct the path on the Java page of the KoldFusion Administrator.",
                         kf_html_escape(jar)));
    kf_throw(c, KFJ_ERRTYPE, kprintf("%s needs cfx.jar, which is not on the Java class path.", what),
             kprintf("%s exists, but the Java Virtual Machine was started without it (the class path is fixed when the "
                     "JVM starts). Restart the KoldFusion Application Server.", kf_html_escape(jar)));
}

/* ---------------------------------------------------------------- result helpers */
static jobject el(JNIEnv *env, jobjectArray a, int i) { return a ? j_GetObjectArrayElement(env, a, i) : NULL; }

static char **strings(JNIEnv *env, jobjectArray a, int *n) {
    *n = a ? j_GetArrayLength(env, a) : 0;
    char **r = kmalloc(sizeof(char *) * (*n + 1));
    for (int i = 0; i < *n; i++) {
        jobject s = j_GetObjectArrayElement(env, a, i);
        r[i] = kfj_cstr(env, s);
        if (s) j_DeleteLocalRef(env, s);
    }
    return r;
}

/* class name and message of a Throwable returned by the bridge */
static void exc_text(JNIEnv *env, jobject t, char **cls, char **msg) {
    j_ExceptionClear(env);
    JF(env, 13, jint (*)(JNIEnv *, jobject))(env, t);       /* Throw(t): make it pending ... */
    kfj_take_exception(env, cls, msg, NULL);                 /* ... and read it back the usual way */
}

static Query *query_from(JNIEnv *env, jobjectArray cols, jobjectArray data, int rows) {
    int nc, nd;
    char **cn = strings(env, cols, &nc);
    char **dv = strings(env, data, &nd);
    Query *q = query_new(nc, (const char **)cn);
    for (int r = 0; r < rows; r++) {
        int row = query_add_row(q);
        for (int ci = 0; ci < nc && r * nc + ci < nd; ci++) query_set(q, ci, row, v_str(dv[r * nc + ci]));
    }
    return q;
}

/* ================================================================ Java CFX tags */
void java_cfx_call(Ctx *c, Node *n, const char *tagname, const char *regkey) {
    const char *cls = reg_get(regkey, "ClassName", "");
    if (!cls || !*cls)
        kf_throw(c, "Application", kprintf("The Java CFX tag %s has no class name.", tagname),
                 "Enter the name of the Java class that implements the tag on the CFX Tags page of the KoldFusion Administrator.");
    /* attributes (RELOAD="Auto|Always|Never" is for the server, not the tag) */
    int na = 0;
    const char **an = kmalloc(sizeof(char *) * (n->nattrs + 1)), **av = kmalloc(sizeof(char *) * (n->nattrs + 1));
    const char *reload = "auto", *qattr = NULL;
    int debug = 0;
    Query *q = NULL;
    for (int i = 0; i < n->nattrs; i++) {
        Val v = eval(c, n->attrs[i].val);
        if (v.t == VT_QUERY && !kf_stricmp(n->attrs[i].name, "query")) {    /* QUERY="#q#" as well as QUERY="q" */
            q = v.u.q;
            v = v_str(q->name ? q->name : "query");
        }
        const char *s = val_simple_str(c, v, n->attrs[i].val);
        if (!kf_stricmp(n->attrs[i].name, "reload")) { reload = s; continue; }
        if (!kf_stricmp(n->attrs[i].name, "query")) qattr = s;
        if (!kf_stricmp(n->attrs[i].name, "debug")) debug = 1;
        an[na] = n->attrs[i].name; av[na] = s; na++;
    }
    if (qattr && !q) {
        Val qv;
        if (!resolve_path(c, qattr, &qv) || qv.t != VT_QUERY)
            kf_throw(c, "Application", kprintf("The query %s passed to %s was not found.", kf_html_escape(qattr), tagname),
                     "The QUERY attribute of a CFX tag must name a query, e.g. QUERY=\"GetEmployees\".");
        q = qv.u.q;
    }
    /* the query: column names and row-major data */
    const char **qcols = NULL, **qdata = NULL;
    if (q) {
        qcols = kmalloc(sizeof(char *) * (q->ncols + 1));
        for (int i = 0; i < q->ncols; i++) qcols[i] = q->cols[i];
        qdata = kmalloc(sizeof(char *) * ((size_t)q->ncols * q->nrows + 1));
        for (int r = 0; r < q->nrows; r++)
            for (int ci = 0; ci < q->ncols; ci++) qdata[(size_t)r * q->ncols + ci] = v_tostr(query_get(q, ci, r));
    }
    /* the tag's registry settings, for Request.getSetting() */
    Query *sq = reg_list(regkey, 0, 1);
    const char **sn = kmalloc(sizeof(char *) * (sq->nrows + 1)), **sv = kmalloc(sizeof(char *) * (sq->nrows + 1));
    for (int r = 0; r < sq->nrows; r++) { sn[r] = v_tostr(query_get(sq, 0, r)); sv[r] = v_tostr(query_get(sq, 2, r)); }

    JNIEnv *env = kfj_env(c);
    jclass b = bridge(c, env, "A Java CFX tag");
    const char *errmsg = NULL, *errdetail = NULL;
    Array *assigns = array_new();             /* applied after popping the frame: assign_path may throw */
    char *out = "", *dbg = "";
    j_PushLocalFrame(env, 64);
    jvalue a[11];
    a[0].l = kfj_str(env, cls);
    a[1].l = kfj_str(env, reload);
    a[2].l = kfj_strarray(env, na, an);
    a[3].l = kfj_strarray(env, na, av);
    a[4].l = kfj_str(env, qattr ? qattr : "");
    a[5].l = q ? kfj_strarray(env, q->ncols, qcols) : NULL;
    a[6].l = q ? kfj_strarray(env, q->ncols * q->nrows, qdata) : NULL;
    a[7].i = q ? q->nrows : 0;
    a[8].l = kfj_strarray(env, sq->nrows, sn);
    a[9].l = kfj_strarray(env, sq->nrows, sv);
    a[10].z = (jboolean)debug;
    jobjectArray r = j_CallStaticObjectMethodA(env, b, g_run_cfx, a);
    char *ecls, *emsg;
    if (kfj_take_exception(env, &ecls, &emsg, NULL) || !r) {
        errmsg = kprintf("An error occurred while processing %s.", tagname);
        errdetail = r ? kprintf("%s: %s", ecls, emsg) : "The CFX bridge returned nothing.";
    } else {
        /* output and variables are applied even when the tag then threw, as with C++ CFX tags */
        out = kfj_cstr(env, el(env, r, 0));
        dbg = kfj_cstr(env, el(env, r, 1));
        jobjectArray ops = el(env, r, 2);
        int nops = ops ? j_GetArrayLength(env, ops) : 0;
        for (int i = 0; i < nops; i++) {
            j_PushLocalFrame(env, 16);
            jobjectArray op = el(env, ops, i);
            char *kind = kfj_cstr(env, el(env, op, 0));
            Struct *s = struct_new();
            struct_set(s, "name", v_str(kfj_cstr(env, el(env, op, 1))));
            if (!strcmp(kind, "var")) struct_set(s, "value", v_str(kfj_cstr(env, el(env, op, 2))));
            else struct_set(s, "value", v_query(query_from(env, el(env, op, 2), el(env, op, 3), kfj_int_value(env, el(env, op, 4), 0))));
            array_push(assigns, v_struct(s));
            j_PopLocalFrame(env, NULL);
        }
        jobjectArray nq = el(env, r, 3);
        if (nq && q) {
            /* the tag changed the query it was given (setData/addRow) */
            int nd;
            char **dv = strings(env, nq, &nd);
            int rows = q->ncols ? nd / q->ncols : 0;
            while (q->nrows < rows) query_add_row(q);
            for (int rr = 0; rr < rows; rr++)
                for (int ci = 0; ci < q->ncols; ci++) query_set(q, ci, rr, v_str(dv[(size_t)rr * q->ncols + ci]));
        }
        jobject t = el(env, r, 4);
        if (t) {
            exc_text(env, t, &ecls, &emsg);
            if (strstr(ecls, "ClassNotFound") || strstr(ecls, "NoClassDefFound")) {
                errmsg = kprintf("The Java class %s for the CFX tag %s could not be found.", cls, tagname);
                errdetail = kprintf("%s: %s. Put the class into %s/java/classes, or a directory or JAR on the Class Path "
                                    "set on the Java page of the KoldFusion Administrator.", ecls, emsg, G.root);
            } else {
                errmsg = kprintf("An error occurred while processing %s: %s", tagname, *emsg ? emsg : ecls);
                errdetail = kprintf("The Java CFX class %s threw %s%s%s", cls, ecls, *emsg ? ": " : "", emsg);
            }
        }
    }
    j_ExceptionClear(env);
    j_PopLocalFrame(env, NULL);
    if (*out) out_puts(c, out);
    if (*dbg) out_puts(c, kprintf("<PRE><B>Debug output (%s):</B>\n%s</PRE>", tagname, kf_html_escape(dbg)));
    for (int i = 0; i < assigns->n; i++) {
        Struct *s = assigns->v[i].u.st;
        assign_path(c, v_tostr(*struct_get(s, "name")), *struct_get(s, "value"));
    }
    if (errmsg) kf_throw(c, "Application", kf_html_escape(errmsg), kf_html_escape(errdetail));
}

/* ================================================================ CFSERVLET */
typedef struct SParam { const char *name, *value, *variable, *type; } SParam;
static __thread Array *t_sparams;

void tag_servletparam(Ctx *c, Node *n, int *flow) {
    (void)flow;
    if (!t_sparams)
        kf_throw(c, "Template", "Context validation error for tag CFSERVLETPARAM.", "The tag must be nested inside a CFSERVLET tag.");
    const char *name = require_attr(c, n, "name");
    int hv = has_attr(n, "value"), hr = has_attr(n, "variable");
    if (hv == hr)
        kf_throw(c, "Application", "Attribute validation error for tag CFSERVLETPARAM.",
                 "Specify either VALUE (a request parameter) or VARIABLE (a CFML variable passed by reference as a request "
                 "attribute), but not both.");
    SParam *p = kmalloc(sizeof(SParam));
    p->name = name;
    if (hv) p->value = attr_str(c, n, "value", "");
    else {
        p->variable = attr_str(c, n, "variable", "");
        p->type = attr_str(c, n, "type", "");
        if (*p->type && kf_stricmp(p->type, "int") && kf_stricmp(p->type, "double") && kf_stricmp(p->type, "bool") &&
            kf_stricmp(p->type, "date") && kf_stricmp(p->type, "string"))
            kf_throw(c, "Application", "Attribute validation error for tag CFSERVLETPARAM.",
                     kprintf("The value of the attribute TYPE, which is currently \"%s\", must be one of INT, DOUBLE, BOOL, "
                             "DATE or STRING.", kf_html_escape(p->type)));
    }
    array_push(t_sparams, v_binary((const char *)p, sizeof *p));
}

typedef struct SList { const char **n, **v; int len, cap; } SList;
static void sl_add(SList *l, const char *n, const char *v) {
    if (l->len == l->cap) {
        int nc = l->cap ? l->cap * 2 : 16;
        const char **a = kmalloc(sizeof(char *) * nc), **b = kmalloc(sizeof(char *) * nc);
        if (l->len) { memcpy(a, l->n, sizeof(char *) * l->len); memcpy(b, l->v, sizeof(char *) * l->len); }
        l->n = a; l->v = b; l->cap = nc;
    }
    l->n[l->len] = n; l->v[l->len] = v; l->len++;
}
static void sl_struct(SList *l, Struct *s) {
    for (int i = 0; s && i < s->n; i++)
        if (kf_stricmp(s->e[i].key, "FieldNames") && v_is_simple(s->e[i].v)) sl_add(l, s->e[i].key, v_tostr(s->e[i].v));
}

void tag_servlet(Ctx *c, Node *n, int *flow) {
    RState *rs = c->rs;
    const char *code = require_attr(c, n, "code");
    const char *proxy = attr_str(c, n, "jrunproxy", "");      /* accepted; the servlet runs in-process */
    int timeout = (int)attr_num(c, n, "timeout", 0);
    int writeoutput = attr_bool(c, n, "writeoutput", 1);
    int debug = attr_bool(c, n, "debug", 0);

    /* the body: only CFSERVLETPARAM tags count, any other output is discarded */
    Array *saved = t_sparams;
    t_sparams = array_new();
    Buf *saved_out = rs->out;
    Buf junk; buf_init(&junk);
    rs->out = &junk;
    JmpFrame jf; jf.prev = rs->jf; rs->jf = &jf;
    if (setjmp(jf.jb) == 0) {
        exec_nodes(c, n->kids, n->nkids, flow);
        rs->jf = jf.prev;
    } else {
        /* an error in the body: put things back before passing it on */
        rs->jf = jf.prev;
        rs->out = saved_out;
        t_sparams = saved;
        kf_throw_err(rs, rs->err);
    }
    rs->out = saved_out;
    Array *params = t_sparams;
    t_sparams = saved;

    /* parameters: the page's URL (and form) fields, as JRun saw them, then CFSERVLETPARAM VALUE= */
    SList pl = {0};
    sl_struct(&pl, rs->url);
    if (rs->http && rs->http->method && !strcmp(rs->http->method, "POST")) sl_struct(&pl, rs->form);
    int nattr = 0;
    for (int i = 0; i < params->n; i++) {
        SParam *p = (SParam *)params->v[i].u.str.s;
        if (p->value) sl_add(&pl, p->name, p->value);
        else nattr++;
    }
    /* attributes: CFSERVLETPARAM VARIABLE= (by reference) */
    SParam **ap = kmalloc(sizeof(SParam *) * (nattr + 1));
    Val *avals = kmalloc(sizeof(Val) * (nattr + 1));
    const char **anames = kmalloc(sizeof(char *) * (nattr + 1));
    int na = 0;
    for (int i = 0; i < params->n; i++) {
        SParam *p = (SParam *)params->v[i].u.str.s;
        if (p->value) continue;
        Val v;
        if (!resolve_path(c, p->variable, &v))
            kf_throw(c, "Application", kprintf("Error resolving parameter <B>%s</B>", kf_upper(p->variable)),
                     kprintf("The variable %s, passed by CFSERVLETPARAM NAME=\"%s\", is not defined.", kf_upper(p->variable),
                             kf_html_escape(p->name)));
        if (v.t == VT_QUERY)
            kf_throw(c, "Application", "Queries cannot be passed to servlets.",
                     "KoldFusion has no com.allaire.util.RecordSet; pass the columns as arrays instead.");
        double d;
        if (!kf_stricmp(p->type, "int") || !kf_stricmp(p->type, "double")) {
            if (!v_tonum(v, &d)) kf_throw(c, "Application", kprintf("The variable %s is not a number.", kf_upper(p->variable)),
                                         kprintf("CFSERVLETPARAM TYPE=\"%s\" needs a numeric value.", kf_upper(p->type)));
        } else if (!kf_stricmp(p->type, "date")) {
            if (!v_todate(v, &d)) kf_throw(c, "Application", kprintf("The variable %s is not a date.", kf_upper(p->variable)),
                                          "CFSERVLETPARAM TYPE=\"DATE\" needs a date/time value.");
            v = v_date(d);
        } else if (!kf_stricmp(p->type, "bool")) {
            int bb;
            if (!v_tobool(v, &bb)) kf_throw(c, "Application", kprintf("The variable %s is not a boolean.", kf_upper(p->variable)),
                                           "CFSERVLETPARAM TYPE=\"BOOL\" needs YES/NO, TRUE/FALSE or a number.");
        }
        ap[na] = p; avals[na] = v; anames[na] = p->name; na++;
    }
    /* request headers and information */
    HttpReq *hr = rs->http;
    SList hl = {0};
    for (int i = 0; hr && hr->headers && i < hr->headers->n; i++) sl_add(&hl, hr->headers->e[i].key, v_tostr(hr->headers->e[i].v));
    Val *ru = struct_get(rs->cgi, "REMOTE_USER");
    const char *uri = kprintf("/servlet/%s", code);
    const char *info[15] = {
        hr && hr->method ? hr->method : "GET", uri, hr && hr->query ? hr->query : "",
        hr && hr->version ? hr->version : "HTTP/1.0", hr && hr->server_name ? hr->server_name : "localhost",
        kprintf("%d", hr && hr->server_port ? hr->server_port : G.port), hr && hr->remote_addr ? hr->remote_addr : "127.0.0.1",
        hr && hr->remote_addr ? hr->remote_addr : "127.0.0.1", "http", "", uri, "",
        ru ? v_tostr(*ru) : "", hr && hr->content_type ? hr->content_type : "", "" };
    /* HttpSession: shared with the CFML session (or the CFID/CFTOKEN client) */
    const char *sid = NULL;
    if (rs->sess && rs->sess->key) sid = rs->sess->key;
    else {
        Val *cf = struct_get(rs->cookie, "CFID"), *ct = struct_get(rs->cookie, "CFTOKEN");
        if (cf && ct) sid = kprintf("%s_%s", v_tostr(*cf), v_tostr(*ct));
    }

    JNIEnv *env = kfj_env(c);
    jclass b = bridge(c, env, "CFSERVLET");
    double t0 = kf_time_ms();
    const char *errmsg = NULL, *errdetail = NULL;
    Struct *result = struct_new();
    char *body = ""; size_t bodylen = 0;
    Array *back = array_new();
    j_PushLocalFrame(env, 64 + na * 4);
    jvalue a[11];
    a[0].l = kfj_str(env, code);
    a[1].l = kfj_strarray(env, 15, info);
    a[2].l = kfj_strarray(env, pl.len, pl.n);
    a[3].l = kfj_strarray(env, pl.len, pl.v);
    a[4].l = kfj_strarray(env, hl.len, hl.n);
    a[5].l = kfj_strarray(env, hl.len, hl.v);
    a[6].l = kfj_strarray(env, na, anames);
    a[7].l = j_NewObjectArray(env, na, kfj_object_class(), NULL);
    for (int i = 0; i < na; i++) {
        const char *t = ap[i]->type;
        /* without TYPE, simple values travel as strings (as in ColdFusion 4.5); arrays become Vectors, structures Hashtables */
        int hint = !kf_stricmp(t, "int") ? H_INT : !kf_stricmp(t, "double") ? H_DOUBLE : !kf_stricmp(t, "bool") ? H_BOOL
                 : !kf_stricmp(t, "string") ? H_STRING : (!*t && v_is_simple(avals[i])) ? H_STRING : H_NONE;
        jobject o = kfj_to_java(env, avals[i], hint);
        j_SetObjectArrayElement(env, a[7].l, i, o);
        if (o) j_DeleteLocalRef(env, o);
    }
    if (hr && hr->body && hr->bodylen) {
        a[8].l = j_NewByteArray(env, (jsize)hr->bodylen);
        if (a[8].l) j_SetByteArrayRegion(env, a[8].l, 0, (jsize)hr->bodylen, (const jbyte *)hr->body);
    } else a[8].l = NULL;
    a[9].l = sid ? kfj_str(env, sid) : NULL;
    a[10].i = timeout;
    jobjectArray r = j_CallStaticObjectMethodA(env, b, g_run_servlet, a);
    char *ecls, *emsg;
    if (kfj_take_exception(env, &ecls, &emsg, NULL) || !r) {
        errmsg = kprintf("An error occurred while running the servlet %s.", code);
        errdetail = r ? kprintf("%s: %s", ecls, emsg) : "The servlet bridge returned nothing.";
    } else {
        int status = kfj_int_value(env, el(env, r, 0), 200);
        int nhn, nhv;
        char **rhn = strings(env, el(env, r, 2), &nhn), **rhv = strings(env, el(env, r, 3), &nhv);
        jbyteArray bb = el(env, r, 4);
        bodylen = bb ? (size_t)j_GetArrayLength(env, bb) : 0;
        body = kmalloc(bodylen + 1);
        if (bodylen) j_GetByteArrayRegion(env, bb, 0, (jsize)bodylen, (jbyte *)body);
        body[bodylen] = 0;
        /* CFSERVLET.Output plus one entry per response header (and StatusCode/StatusText, a KoldFusion extra) */
        struct_set(result, "Output", v_strn(body, bodylen));
        for (int i = 0; i < nhn && i < nhv; i++) {
            if (!kf_stricmp(rhn[i], "Output")) continue;
            Val *old = struct_get(result, rhn[i]);
            struct_set(result, rhn[i], v_str(old ? kprintf("%s, %s", v_tostr(*old), rhv[i]) : rhv[i]));
        }
        struct_set(result, "StatusCode", v_num(status));
        struct_set(result, "StatusText", v_str(kfj_cstr(env, el(env, r, 1))));
        /* attributes passed by reference come back into their CFML variables */
        int nan;
        char **ran = strings(env, el(env, r, 5), &nan);
        jobjectArray rav = el(env, r, 6);
        for (int i = 0; i < na; i++) {
            for (int k = 0; k < nan; k++) {
                if (strcmp(ran[k], ap[i]->name)) continue;
                j_PushLocalFrame(env, 16);
                Struct *s = struct_new();
                struct_set(s, "name", v_str(ap[i]->variable));
                struct_set(s, "value", kfj_to_cf(env, el(env, rav, k)));
                array_push(back, v_struct(s));
                j_PopLocalFrame(env, NULL);
                break;
            }
        }
        jobject t = el(env, r, 7);
        if (t) {
            exc_text(env, t, &ecls, &emsg);
            int cnf = strstr(ecls, "ClassNotFound") || strstr(ecls, "NoClassDefFound");
            errmsg = strstr(ecls, "InterruptedIO") ? kprintf("The servlet %s timed out.", code)
                   : cnf ? kprintf("The servlet class %s could not be found.", code)
                   : kprintf("An exception occurred in the servlet %s.", code);
            errdetail = cnf ? kprintf("%s: %s. Put the servlet class into %s/java/classes or onto the Class Path set on the "
                                      "Java page of the KoldFusion Administrator.", ecls, emsg, G.root)
                            : kprintf("%s%s%s", ecls, *emsg ? ": " : "", emsg);
        }
    }
    j_ExceptionClear(env);
    j_PopLocalFrame(env, NULL);
    if (debug)
        kf_log("servlet.log", "Information", "CFSERVLET CODE=%s JRUNPROXY=%s: %s, %zu bytes in %.0f ms (run in-process)", code,
               *proxy ? proxy : "(local)", errmsg ? errmsg : "OK", bodylen, kf_time_ms() - t0);
    if (errmsg) kf_throw(c, "Application", kf_html_escape(errmsg), kf_html_escape(errdetail));
    for (int i = 0; i < back->n; i++) {
        Struct *s = back->v[i].u.st;
        assign_path(c, v_tostr(*struct_get(s, "name")), *struct_get(s, "value"));
    }
    assign_path(c, "CFSERVLET", v_struct(result));
    if (writeoutput && bodylen) out_put(c, body, bodylen);
}
