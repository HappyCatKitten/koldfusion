/*
 * KoldFusion Application Server 4.5 - the Java half of Java CFX tags and CFSERVLET.
 *
 * The C engine (src/java_ext.c) calls the static methods below through JNI with plain strings and arrays, and
 * reads everything back from the Object[] they return: no Java code ever calls back into the server, so a CFX
 * tag or servlet can never unwind through C frames.
 *
 * Classes in <install>/java/classes are loaded by a ClassLoader of their own and reloaded when their .class
 * file changes (CFX tags: RELOAD="Auto|Always|Never"; servlets: always Auto), as ColdFusion and JRun did.
 */
package com.gibson.kf;

import java.io.File;
import java.util.Hashtable;
import java.util.Vector;

public final class Bridge {
    private Bridge() { }

    /* ================================================================ class loading */
    static File classesDir() {
        return new File(System.getProperty("koldfusion.root", "."), "java" + File.separator + "classes");
    }

    private static final class Loaded { Class cls; long mtime; }
    private static final Hashtable loaded = new Hashtable();     /* class name -> Loaded */

    /** the class, from java/classes (reloadable) or else from the class path */
    static synchronized Class load(String name, String reload) throws ClassNotFoundException {
        File f = new File(classesDir(), name.replace('.', File.separatorChar) + ".class");
        if (!f.isFile()) return Class.forName(name, true, ClassLoader.getSystemClassLoader());
        long mt = f.lastModified();
        Loaded l = (Loaded) loaded.get(name);
        boolean fresh = l == null || "always".equalsIgnoreCase(reload) || (!"never".equalsIgnoreCase(reload) && l.mtime != mt);
        if (!fresh) return l.cls;
        KFClassLoader cl = new KFClassLoader(classesDir(), Bridge.class.getClassLoader());
        Loaded n = new Loaded();
        n.cls = Class.forName(name, true, cl);
        n.mtime = mt;
        loaded.put(name, n);
        return n.cls;
    }

    /* ================================================================ Java CFX tags */
    /**
     * Runs one CFX tag. Returns { String output, String debugOutput, Object[] operations, String[] newInputQueryData,
     * Throwable error }; each operation is String[]{"var", name, value} or Object[]{"query", name, String[] columns,
     * String[] rowMajorData, Integer rows}.
     */
    public static Object[] runCFX(String className, String reload, String[] an, String[] av, String qname, String[] qcols,
                                  String[] qdata, int qrows, String[] sn, String[] sv, boolean debug) {
        Object[] r = new Object[5];
        CFXQuery q = qcols == null ? null : CFXQuery.fromData(qname, qcols, qdata, qrows);
        CFXRequest req = new CFXRequest(an, av, q, sn, sv);
        CFXResponse resp = new CFXResponse(debug);
        try {
            Class c = load(className, reload);
            Object tag = c.newInstance();
            if (tag instanceof com.gibson.cfx.CustomTag) ((com.gibson.cfx.CustomTag) tag).processRequest(req, resp);
            else if (tag instanceof com.allaire.cfx.CustomTag) ((com.allaire.cfx.CustomTag) tag).processRequest(req, resp);
            else throw new ClassCastException("The class " + className + " does not implement the CustomTag interface "
                                              + "(com.allaire.cfx.CustomTag or com.gibson.cfx.CustomTag)");
        } catch (Throwable t) {
            r[4] = t;
        }
        r[0] = resp.output();
        r[1] = resp.debugOutput();
        Object[] ops = new Object[resp.ops.size()];
        for (int i = 0; i < ops.length; i++) {
            Object o = resp.ops.elementAt(i);
            if (o instanceof String[]) ops[i] = o;
            else {
                CFXQuery cq = (CFXQuery) ((Object[]) o)[1];
                ops[i] = new Object[] { "query", cq.getName(), cq.getColumns(), cq.flatData(), Integer.valueOf(cq.getRowCount()) };
            }
        }
        r[2] = ops;
        r[3] = q != null && q.dirty ? q.flatData() : null;
        return r;
    }

    /* ================================================================ servlets */
    private static final Hashtable servlets = new Hashtable();   /* class name -> javax.servlet.Servlet */

    static synchronized javax.servlet.Servlet servlet(String className) throws Exception {
        Class c = load(className, "auto");
        javax.servlet.Servlet s = (javax.servlet.Servlet) servlets.get(className);
        if (s != null && s.getClass() == c) return s;
        if (s != null) { try { s.destroy(); } catch (Throwable t) { } }
        Object o = c.newInstance();
        if (!(o instanceof javax.servlet.Servlet))
            throw new javax.servlet.ServletException("The class " + className + " is not a servlet (it does not implement javax.servlet.Servlet)");
        s = (javax.servlet.Servlet) o;
        s.init(new ServletRunner.Config(className));
        servlets.put(className, s);
        return s;
    }

    /**
     * Runs a servlet in this VM. info = { method, requestURI, queryString, protocol, serverName, serverPort,
     * remoteAddr, remoteHost, scheme, contextPath, servletPath, pathInfo, remoteUser, contentType, authType }.
     * Returns { Integer status, String message, String[] headerNames, String[] headerValues, byte[] body,
     * String[] attributeNames, Object[] attributeValues, Throwable error }.
     */
    public static Object[] runServlet(final String className, String[] info, String[] pn, String[] pv, String[] hn,
                                      String[] hv, String[] an, Object[] av, byte[] body, String sessionId, int timeout) {
        final ServletRunner.Request req = new ServletRunner.Request(info, pn, pv, hn, hv, an, av, body, sessionId);
        final ServletRunner.Response resp = new ServletRunner.Response();
        final Throwable[] err = new Throwable[1];
        Runnable run = new Runnable() {
            public void run() {
                try {
                    javax.servlet.Servlet s = servlet(className);
                    if (s instanceof javax.servlet.SingleThreadModel) { synchronized (s) { s.service(req, resp); } }
                    else s.service(req, resp);
                    resp.finish();
                } catch (Throwable t) {
                    err[0] = t;
                }
            }
        };
        if (timeout > 0) {
            Thread t = new Thread(run, "CFSERVLET " + className);
            t.setDaemon(true);
            t.start();
            try { t.join(timeout * 1000L); } catch (InterruptedException e) { }
            if (t.isAlive()) {
                t.interrupt();
                err[0] = new java.io.InterruptedIOException("The servlet " + className + " did not respond within " + timeout + " seconds");
            }
        } else run.run();
        Object[] r = new Object[8];
        r[0] = Integer.valueOf(resp.status);
        r[1] = resp.message;
        Vector names = new Vector(), values = new Vector();
        resp.headers(names, values);
        String[] a = new String[names.size()], b = new String[values.size()];
        names.copyInto(a); values.copyInto(b);
        r[2] = a; r[3] = b;
        r[4] = resp.body();
        Vector anames = new Vector(), avals = new Vector();
        req.attributes(anames, avals);
        String[] c = new String[anames.size()];
        Object[] d = new Object[avals.size()];
        anames.copyInto(c); avals.copyInto(d);
        r[5] = c; r[6] = d;
        r[7] = err[0];
        return r;
    }
}
