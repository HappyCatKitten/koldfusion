/*
 * KoldFusion Application Server 4.5 - a minimal Java Servlet API (2.1/2.2 level), written for KoldFusion so
 * CFSERVLET can run servlets in the embedded Java VM. Only what 1999-era servlets need is here.
 */
package javax.servlet.http;

import java.util.Enumeration;
import javax.servlet.ServletRequest;

public interface HttpServletRequest extends ServletRequest {
    public static final String BASIC_AUTH = "BASIC";
    public String getAuthType();
    public Cookie[] getCookies();
    public long getDateHeader(String name);
    public String getHeader(String name);
    public Enumeration getHeaders(String name);
    public Enumeration getHeaderNames();
    public int getIntHeader(String name);
    public String getMethod();
    public String getPathInfo();
    public String getPathTranslated();
    public String getContextPath();
    public String getQueryString();
    public String getRemoteUser();
    public boolean isUserInRole(String role);
    public java.security.Principal getUserPrincipal();
    public String getRequestedSessionId();
    public String getRequestURI();
    public String getServletPath();
    public HttpSession getSession(boolean create);
    public HttpSession getSession();
    public boolean isRequestedSessionIdValid();
    public boolean isRequestedSessionIdFromCookie();
    public boolean isRequestedSessionIdFromURL();
    /** @deprecated */
    public boolean isRequestedSessionIdFromUrl();
}
