/*
 * KoldFusion Application Server 4.5 - a minimal Java Servlet API (2.1/2.2 level), written for KoldFusion so
 * CFSERVLET can run servlets in the embedded Java VM. Only what 1999-era servlets need is here.
 */
package javax.servlet;

import java.io.InputStream;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Enumeration;

public interface ServletContext {
    public ServletContext getContext(String uripath);
    public int getMajorVersion();
    public int getMinorVersion();
    public String getMimeType(String file);
    public URL getResource(String path) throws MalformedURLException;
    public InputStream getResourceAsStream(String path);
    public RequestDispatcher getRequestDispatcher(String path);
    public RequestDispatcher getNamedDispatcher(String name);
    /** @deprecated */
    public Servlet getServlet(String name) throws ServletException;
    /** @deprecated */
    public Enumeration getServlets();
    /** @deprecated */
    public Enumeration getServletNames();
    public void log(String msg);
    /** @deprecated */
    public void log(Exception exception, String msg);
    public void log(String message, Throwable throwable);
    public String getRealPath(String path);
    public String getServerInfo();
    public String getInitParameter(String name);
    public Enumeration getInitParameterNames();
    public Object getAttribute(String name);
    public Enumeration getAttributeNames();
    public void setAttribute(String name, Object object);
    public void removeAttribute(String name);
}
