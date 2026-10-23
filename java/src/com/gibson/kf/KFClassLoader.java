/*
 * KoldFusion Application Server 4.5 - a child-first class loader over <install>/java/classes, so Java CFX tags and
 * servlets placed there can be reloaded without restarting the server. The CFX, servlet and runtime interfaces always
 * come from the parent, so a reloaded class still implements the same CustomTag / Servlet.
 */
package com.gibson.kf;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.net.URL;

final class KFClassLoader extends ClassLoader {
    private final File dir;

    KFClassLoader(File dir, ClassLoader parent) {
        super(parent);
        this.dir = dir;
    }

    private static boolean shared(String name) {
        return name.startsWith("java.") || name.startsWith("javax.") || name.startsWith("sun.") || name.startsWith("jdk.")
            || name.startsWith("com.allaire.cfx.") || name.startsWith("com.gibson.cfx.") || name.startsWith("com.gibson.kf.");
    }

    protected synchronized Class loadClass(String name, boolean resolve) throws ClassNotFoundException {
        Class c = findLoadedClass(name);
        if (c == null && !shared(name)) {
            try { c = findClass(name); } catch (ClassNotFoundException e) { c = null; }
        }
        if (c == null) return super.loadClass(name, resolve);
        if (resolve) resolveClass(c);
        return c;
    }

    protected Class findClass(String name) throws ClassNotFoundException {
        File f = new File(dir, name.replace('.', File.separatorChar) + ".class");
        if (!f.isFile()) throw new ClassNotFoundException(name);
        try {
            InputStream in = new FileInputStream(f);
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buf = new byte[8192];
            int n;
            try { while ((n = in.read(buf)) > 0) out.write(buf, 0, n); } finally { in.close(); }
            byte[] b = out.toByteArray();
            return defineClass(name, b, 0, b.length);
        } catch (java.io.IOException e) {
            throw new ClassNotFoundException(name + ": " + e.getMessage());
        }
    }

    protected URL findResource(String name) {
        File f = new File(dir, name);
        try { return f.isFile() ? f.toURI().toURL() : null; } catch (java.net.MalformedURLException e) { return null; }
    }
}
