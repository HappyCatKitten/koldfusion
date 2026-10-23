/*
 * KoldFusion Application Server 4.5 - a minimal Java Servlet API (2.1/2.2 level), written for KoldFusion so
 * CFSERVLET can run servlets in the embedded Java VM. Only what 1999-era servlets need is here.
 */
package javax.servlet;

import java.io.BufferedReader;
import java.io.IOException;
import java.util.Enumeration;
import java.util.Locale;

public interface ServletRequest {
    public Object getAttribute(String name);
    public Enumeration getAttributeNames();
    public String getCharacterEncoding();
    public int getContentLength();
    public String getContentType();
    public ServletInputStream getInputStream() throws IOException;
    public String getParameter(String name);
    public Enumeration getParameterNames();
    public String[] getParameterValues(String name);
    public String getProtocol();
    public String getScheme();
    public String getServerName();
    public int getServerPort();
    public BufferedReader getReader() throws IOException;
    public String getRemoteAddr();
    public String getRemoteHost();
    public void setAttribute(String name, Object o);
    public void removeAttribute(String name);
    public Locale getLocale();
    public Enumeration getLocales();
    public boolean isSecure();
    public RequestDispatcher getRequestDispatcher(String path);
    /** @deprecated */
    public String getRealPath(String path);
}
