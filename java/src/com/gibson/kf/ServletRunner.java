/*
 * KoldFusion Application Server 4.5 - the servlet engine behind CFSERVLET: ServletConfig, ServletContext,
 * HttpServletRequest, HttpServletResponse and HttpSession for servlets running inside the embedded JVM
 * (ColdFusion 4.5 sent CFSERVLET requests to a JRun server instead).
 */
package com.gibson.kf;

import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Locale;
import java.util.TimeZone;
import java.util.Vector;
import javax.servlet.RequestDispatcher;
import javax.servlet.Servlet;
import javax.servlet.ServletConfig;
import javax.servlet.ServletContext;
import javax.servlet.ServletInputStream;
import javax.servlet.ServletOutputStream;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import javax.servlet.http.HttpSessionBindingEvent;
import javax.servlet.http.HttpSessionBindingListener;

final class ServletRunner {
    private ServletRunner() { }

    static final String SERVER_INFO = "KoldFusion Servlet Runner/4.5 (Servlet API 2.2; in-process, like JRun 3.0)";

    /* ================================================================ context */
    static final class Context implements ServletContext {
        static final Context INSTANCE = new Context();
        private final Hashtable attrs = new Hashtable();

        public ServletContext getContext(String uripath) { return this; }
        public int getMajorVersion() { return 2; }
        public int getMinorVersion() { return 2; }
        public String getMimeType(String file) {
            String f = file.toLowerCase();
            if (f.endsWith(".html") || f.endsWith(".htm")) return "text/html";
            if (f.endsWith(".txt")) return "text/plain";
            if (f.endsWith(".gif")) return "image/gif";
            if (f.endsWith(".jpg") || f.endsWith(".jpeg")) return "image/jpeg";
            if (f.endsWith(".xml")) return "text/xml";
            if (f.endsWith(".cfm")) return "text/html";
            return null;
        }
        public URL getResource(String path) throws java.net.MalformedURLException {
            File f = new File(getRealPath(path));
            return f.exists() ? f.toURI().toURL() : null;
        }
        public InputStream getResourceAsStream(String path) {
            try { return new java.io.FileInputStream(getRealPath(path)); } catch (IOException e) { return null; }
        }
        public RequestDispatcher getRequestDispatcher(String path) { return null; }
        public RequestDispatcher getNamedDispatcher(String name) { return null; }
        public Servlet getServlet(String name) { return null; }
        public Enumeration getServlets() { return new Vector().elements(); }
        public Enumeration getServletNames() { return new Vector().elements(); }
        public void log(String msg) { log(msg, null); }
        public void log(Exception e, String msg) { log(msg, e); }
        public synchronized void log(String msg, Throwable t) {
            try {
                File dir = new File(System.getProperty("koldfusion.root", "."), "log");
                PrintWriter w = new PrintWriter(new FileWriter(new File(dir, "servlet.log"), true));
                SimpleDateFormat d = new SimpleDateFormat("MM/dd/yy\",\"HH:mm:ss");
                w.println("\"Information\",\"" + Thread.currentThread().getName() + "\",\"" + d.format(new Date()) + "\",\""
                          + String.valueOf(msg).replace('"', '\'') + "\"");
                if (t != null) t.printStackTrace(w);
                w.close();
            } catch (IOException e) { }
        }
        public String getRealPath(String path) {
            String root = System.getProperty("koldfusion.webroot", ".");
            if (path == null) return root;
            return new File(root, path.replace('/', File.separatorChar)).getPath();
        }
        public String getServerInfo() { return SERVER_INFO; }
        public String getInitParameter(String name) { return null; }
        public Enumeration getInitParameterNames() { return new Vector().elements(); }
        public Object getAttribute(String name) { return attrs.get(name); }
        public Enumeration getAttributeNames() { return attrs.keys(); }
        public void setAttribute(String name, Object o) { if (o == null) attrs.remove(name); else attrs.put(name, o); }
        public void removeAttribute(String name) { attrs.remove(name); }
    }

    static final class Config implements ServletConfig {
        private final String name;
        Config(String name) { this.name = name; }
        public ServletContext getServletContext() { return Context.INSTANCE; }
        public String getInitParameter(String n) { return null; }
        public Enumeration getInitParameterNames() { return new Vector().elements(); }
        public String getServletName() { return name; }
    }

    /* ================================================================ sessions */
    static final Hashtable sessions = new Hashtable();
    private static long counter = System.currentTimeMillis();

    static final class Session implements HttpSession {
        final String id;
        final long created = System.currentTimeMillis();
        long accessed = created;
        int maxInactive = 1800;
        boolean isNew = true, valid = true;
        final Hashtable attrs = new Hashtable();

        Session(String id) { this.id = id; }
        private void check() { if (!valid) throw new IllegalStateException("The session has been invalidated"); }
        public long getCreationTime() { check(); return created; }
        public String getId() { return id; }
        public long getLastAccessedTime() { return accessed; }
        public void setMaxInactiveInterval(int i) { maxInactive = i; }
        public int getMaxInactiveInterval() { return maxInactive; }
        public Object getAttribute(String name) { check(); return attrs.get(name); }
        public Enumeration getAttributeNames() { check(); return attrs.keys(); }
        public void setAttribute(String name, Object value) {
            check();
            if (value == null) { removeAttribute(name); return; }
            Object old = attrs.put(name, value);
            if (old instanceof HttpSessionBindingListener) ((HttpSessionBindingListener) old).valueUnbound(new HttpSessionBindingEvent(this, name));
            if (value instanceof HttpSessionBindingListener) ((HttpSessionBindingListener) value).valueBound(new HttpSessionBindingEvent(this, name));
        }
        public void removeAttribute(String name) {
            check();
            Object old = attrs.remove(name);
            if (old instanceof HttpSessionBindingListener) ((HttpSessionBindingListener) old).valueUnbound(new HttpSessionBindingEvent(this, name));
        }
        public Object getValue(String name) { return getAttribute(name); }
        public String[] getValueNames() {
            check();
            String[] r = new String[attrs.size()];
            int i = 0;
            for (Enumeration e = attrs.keys(); e.hasMoreElements(); ) r[i++] = (String) e.nextElement();
            return r;
        }
        public void putValue(String name, Object value) { setAttribute(name, value); }
        public void removeValue(String name) { removeAttribute(name); }
        public void invalidate() {
            check();
            String[] names = getValueNames();
            for (int i = 0; i < names.length; i++) removeAttribute(names[i]);
            valid = false;
            sessions.remove(id);
        }
        public boolean isNew() { check(); return isNew; }
    }

    static synchronized Session session(String id, boolean create) {
        long now = System.currentTimeMillis();
        for (Enumeration e = sessions.elements(); e.hasMoreElements(); ) {
            Session s = (Session) e.nextElement();
            if (s.maxInactive > 0 && now - s.accessed > s.maxInactive * 1000L) { s.valid = false; sessions.remove(s.id); }
        }
        Session s = id == null ? null : (Session) sessions.get(id);
        if (s != null) { s.isNew = false; s.accessed = now; return s; }
        if (!create) return null;
        if (id == null) id = "KF" + Long.toString(counter++, 36).toUpperCase();
        s = new Session(id);
        sessions.put(id, s);
        return s;
    }

    /* ================================================================ request */
    static final class Request implements HttpServletRequest {
        private final String[] info;
        private final Hashtable params = new Hashtable();      /* name -> String[] */
        private final Vector paramNames = new Vector();
        private final Hashtable headers = new Hashtable();     /* lowercase name -> value */
        private final Vector headerNames = new Vector();
        private final Hashtable attrs = new Hashtable();
        private final byte[] body;
        private final String sessionId;
        private Session session;
        private boolean usedStream, usedReader;

        Request(String[] info, String[] pn, String[] pv, String[] hn, String[] hv, String[] an, Object[] av, byte[] body, String sessionId) {
            this.info = info;
            for (int i = 0; i < pn.length; i++) {
                String[] old = (String[]) params.get(pn[i]), nv;
                if (old == null) { nv = new String[] { pv[i] }; paramNames.addElement(pn[i]); }
                else { nv = new String[old.length + 1]; System.arraycopy(old, 0, nv, 0, old.length); nv[old.length] = pv[i]; }
                params.put(pn[i], nv);
            }
            for (int i = 0; i < hn.length; i++) { headers.put(hn[i].toLowerCase(), hv[i]); headerNames.addElement(hn[i]); }
            for (int i = 0; i < an.length; i++) if (av[i] != null) attrs.put(an[i], av[i]);
            this.body = body == null ? new byte[0] : body;
            this.sessionId = sessionId;
        }

        private String info(int i) { return i < info.length && info[i] != null && info[i].length() > 0 ? info[i] : null; }

        void attributes(Vector names, Vector values) {
            for (Enumeration e = attrs.keys(); e.hasMoreElements(); ) { Object k = e.nextElement(); names.addElement(k); values.addElement(attrs.get(k)); }
        }

        public Object getAttribute(String name) { return attrs.get(name); }
        public Enumeration getAttributeNames() { return attrs.keys(); }
        public String getCharacterEncoding() { return null; }
        public int getContentLength() { return body.length > 0 ? body.length : -1; }
        public String getContentType() { return info(13); }
        public ServletInputStream getInputStream() throws IOException {
            if (usedReader) throw new IllegalStateException("getReader() has already been called");
            usedStream = true;
            final ByteArrayInputStream in = new ByteArrayInputStream(body);
            return new ServletInputStream() { public int read() { return in.read(); } };
        }
        public String getParameter(String name) { String[] v = (String[]) params.get(name); return v == null ? null : v[0]; }
        public Enumeration getParameterNames() { return paramNames.elements(); }
        public String[] getParameterValues(String name) { String[] v = (String[]) params.get(name); return v == null ? null : (String[]) v.clone(); }
        public String getProtocol() { String p = info(3); return p == null ? "HTTP/1.0" : p; }
        public String getScheme() { String s = info(8); return s == null ? "http" : s; }
        public String getServerName() { String s = info(4); return s == null ? "localhost" : s; }
        public int getServerPort() { try { return Integer.parseInt(info(5)); } catch (Exception e) { return 80; } }
        public BufferedReader getReader() throws IOException {
            if (usedStream) throw new IllegalStateException("getInputStream() has already been called");
            usedReader = true;
            return new BufferedReader(new InputStreamReader(new ByteArrayInputStream(body), "ISO-8859-1"));
        }
        public String getRemoteAddr() { String s = info(6); return s == null ? "127.0.0.1" : s; }
        public String getRemoteHost() { String s = info(7); return s == null ? getRemoteAddr() : s; }
        public void setAttribute(String name, Object o) { if (o == null) attrs.remove(name); else attrs.put(name, o); }
        public void removeAttribute(String name) { attrs.remove(name); }
        public Locale getLocale() { return Locale.US; }
        public Enumeration getLocales() { Vector v = new Vector(); v.addElement(Locale.US); return v.elements(); }
        public boolean isSecure() { return "https".equals(getScheme()); }
        public RequestDispatcher getRequestDispatcher(String path) { return null; }
        public String getRealPath(String path) { return Context.INSTANCE.getRealPath(path); }

        public String getAuthType() { return info(14); }
        public Cookie[] getCookies() {
            String h = getHeader("Cookie");
            if (h == null) return null;
            Vector v = new Vector();
            java.util.StringTokenizer st = new java.util.StringTokenizer(h, ";");
            while (st.hasMoreTokens()) {
                String t = st.nextToken().trim();
                int eq = t.indexOf('=');
                if (eq <= 0) continue;
                try { v.addElement(new Cookie(t.substring(0, eq), t.substring(eq + 1))); } catch (IllegalArgumentException e) { }
            }
            Cookie[] r = new Cookie[v.size()];
            v.copyInto(r);
            return r;
        }
        public long getDateHeader(String name) {
            String h = getHeader(name);
            if (h == null) return -1;
            String[] fmts = { "EEE, dd MMM yyyy HH:mm:ss zzz", "EEEEEE, dd-MMM-yy HH:mm:ss zzz", "EEE MMMM d HH:mm:ss yyyy" };
            for (int i = 0; i < fmts.length; i++) {
                try { SimpleDateFormat f = new SimpleDateFormat(fmts[i], Locale.US); f.setTimeZone(TimeZone.getTimeZone("GMT")); return f.parse(h).getTime(); }
                catch (java.text.ParseException e) { }
            }
            throw new IllegalArgumentException(h);
        }
        public String getHeader(String name) { return name == null ? null : (String) headers.get(name.toLowerCase()); }
        public Enumeration getHeaders(String name) { Vector v = new Vector(); String h = getHeader(name); if (h != null) v.addElement(h); return v.elements(); }
        public Enumeration getHeaderNames() { return headerNames.elements(); }
        public int getIntHeader(String name) { String h = getHeader(name); return h == null ? -1 : Integer.parseInt(h.trim()); }
        public String getMethod() { String m = info(0); return m == null ? "GET" : m; }
        public String getPathInfo() { return info(11); }
        public String getPathTranslated() { String p = getPathInfo(); return p == null ? null : getRealPath(p); }
        public String getContextPath() { String s = info(9); return s == null ? "" : s; }
        public String getQueryString() { return info(2); }
        public String getRemoteUser() { return info(12); }
        public boolean isUserInRole(String role) { return false; }
        public java.security.Principal getUserPrincipal() { return null; }
        public String getRequestedSessionId() { return sessionId; }
        public String getRequestURI() { String s = info(1); return s == null ? "/" : s; }
        public String getServletPath() { String s = info(10); return s == null ? "" : s; }
        public HttpSession getSession(boolean create) {
            if (session != null && session.valid) return session;
            session = ServletRunner.session(sessionId, create);
            return session;
        }
        public HttpSession getSession() { return getSession(true); }
        public boolean isRequestedSessionIdValid() { return sessionId != null && sessions.get(sessionId) != null; }
        public boolean isRequestedSessionIdFromCookie() { return sessionId != null; }
        public boolean isRequestedSessionIdFromURL() { return false; }
        public boolean isRequestedSessionIdFromUrl() { return false; }
    }

    /* ================================================================ response */
    static final class Response implements HttpServletResponse {
        int status = 200;
        String message = "OK";
        private final Vector hnames = new Vector(), hvalues = new Vector();
        private final ByteArrayOutputStream buf = new ByteArrayOutputStream();
        private ServletOutputStream stream;
        private PrintWriter writer;
        private String encoding = "UTF-8";
        private int bufferSize = 8192;
        private boolean committed;
        private Locale locale = Locale.US;

        void headers(Vector n, Vector v) { for (int i = 0; i < hnames.size(); i++) { n.addElement(hnames.elementAt(i)); v.addElement(hvalues.elementAt(i)); } }
        byte[] body() { if (writer != null) writer.flush(); return buf.toByteArray(); }
        void finish() { if (writer != null) writer.flush(); committed = true; }

        private int find(String name) {
            for (int i = 0; i < hnames.size(); i++) if (((String) hnames.elementAt(i)).equalsIgnoreCase(name)) return i;
            return -1;
        }

        public String getCharacterEncoding() { return encoding; }
        public ServletOutputStream getOutputStream() {
            if (writer != null) throw new IllegalStateException("getWriter() has already been called");
            if (stream == null) stream = new ServletOutputStream() { public void write(int b) { buf.write(b); } };
            return stream;
        }
        public PrintWriter getWriter() throws UnsupportedEncodingException {
            if (stream != null) throw new IllegalStateException("getOutputStream() has already been called");
            if (writer == null) writer = new PrintWriter(new OutputStreamWriter(buf, encoding));
            return writer;
        }
        public void setContentLength(int len) { setIntHeader("Content-Length", len); }
        public void setContentType(String type) {
            setHeader("Content-Type", type);
            int cs = type == null ? -1 : type.toLowerCase().indexOf("charset=");
            if (cs >= 0 && writer == null) {
                String e = type.substring(cs + 8).trim();
                int semi = e.indexOf(';');
                if (semi >= 0) e = e.substring(0, semi);
                encoding = e.replace('"', ' ').trim();
            }
        }
        public void setBufferSize(int size) { bufferSize = size; }
        public int getBufferSize() { return bufferSize; }
        public void flushBuffer() { if (writer != null) writer.flush(); committed = true; }
        public boolean isCommitted() { return committed; }
        public void reset() {
            if (committed) throw new IllegalStateException("The response has already been committed");
            buf.reset(); hnames.removeAllElements(); hvalues.removeAllElements(); status = 200; message = "OK";
        }
        public void setLocale(Locale loc) { locale = loc; }
        public Locale getLocale() { return locale; }

        public void addCookie(Cookie c) {
            StringBuffer b = new StringBuffer(c.getName()).append('=').append(c.getValue() == null ? "" : c.getValue());
            if (c.getPath() != null) b.append("; path=").append(c.getPath());
            if (c.getDomain() != null) b.append("; domain=").append(c.getDomain());
            if (c.getMaxAge() >= 0) {
                SimpleDateFormat f = new SimpleDateFormat("EEE, dd-MMM-yyyy HH:mm:ss 'GMT'", Locale.US);
                f.setTimeZone(TimeZone.getTimeZone("GMT"));
                b.append("; expires=").append(f.format(new Date(System.currentTimeMillis() + c.getMaxAge() * 1000L)));
            }
            if (c.getSecure()) b.append("; secure");
            addHeader("Set-Cookie", b.toString());
        }
        public boolean containsHeader(String name) { return find(name) >= 0; }
        public String encodeURL(String url) { return url; }
        public String encodeRedirectURL(String url) { return url; }
        public String encodeUrl(String url) { return url; }
        public String encodeRedirectUrl(String url) { return url; }
        public void sendError(int sc, String msg) throws IOException {
            if (committed) throw new IllegalStateException("The response has already been committed");
            buf.reset();
            setStatus(sc, msg);
            setContentType("text/html");
            String m = msg == null ? "" : msg;
            byte[] page = ("<HTML><HEAD><TITLE>Error " + sc + "</TITLE></HEAD><BODY><H2>Error " + sc + "</H2>" + m + "</BODY></HTML>").getBytes("ISO-8859-1");
            buf.write(page, 0, page.length);
            committed = true;
        }
        public void sendError(int sc) throws IOException { sendError(sc, null); }
        public void sendRedirect(String location) throws IOException {
            if (committed) throw new IllegalStateException("The response has already been committed");
            setStatus(SC_MOVED_TEMPORARILY, "Moved Temporarily");
            setHeader("Location", location);
            committed = true;
        }
        private static String date(long d) {
            SimpleDateFormat f = new SimpleDateFormat("EEE, dd MMM yyyy HH:mm:ss 'GMT'", Locale.US);
            f.setTimeZone(TimeZone.getTimeZone("GMT"));
            return f.format(new Date(d));
        }
        public void setDateHeader(String name, long date) { setHeader(name, date(date)); }
        public void addDateHeader(String name, long date) { addHeader(name, date(date)); }
        public void setHeader(String name, String value) {
            int i = find(name);
            if (i >= 0) hvalues.setElementAt(value, i);
            else { hnames.addElement(name); hvalues.addElement(value); }
        }
        public void addHeader(String name, String value) { hnames.addElement(name); hvalues.addElement(value); }
        public void setIntHeader(String name, int value) { setHeader(name, String.valueOf(value)); }
        public void addIntHeader(String name, int value) { addHeader(name, String.valueOf(value)); }
        public void setStatus(int sc) { setStatus(sc, null); }
        public void setStatus(int sc, String sm) { status = sc; message = sm != null ? sm : reason(sc); }

        static String reason(int sc) {
            switch (sc) {
            case 200: return "OK"; case 201: return "Created"; case 202: return "Accepted"; case 204: return "No Content";
            case 301: return "Moved Permanently"; case 302: return "Moved Temporarily"; case 304: return "Not Modified";
            case 400: return "Bad Request"; case 401: return "Unauthorized"; case 403: return "Forbidden";
            case 404: return "Not Found"; case 405: return "Method Not Allowed"; case 500: return "Internal Server Error";
            case 501: return "Not Implemented"; case 503: return "Service Unavailable";
            default: return "";
            }
        }
    }
}
