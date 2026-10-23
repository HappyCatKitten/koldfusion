/*
 * KoldFusion Application Server 4.5 - a minimal Java Servlet API (2.1/2.2 level), written for KoldFusion so
 * CFSERVLET can run servlets in the embedded Java VM. Only what 1999-era servlets need is here.
 */
package javax.servlet.http;

import java.util.Enumeration;

public interface HttpSession {
    public long getCreationTime();
    public String getId();
    public long getLastAccessedTime();
    public void setMaxInactiveInterval(int interval);
    public int getMaxInactiveInterval();
    public Object getAttribute(String name);
    public Enumeration getAttributeNames();
    public void setAttribute(String name, Object value);
    public void removeAttribute(String name);
    /** @deprecated */
    public Object getValue(String name);
    /** @deprecated */
    public String[] getValueNames();
    /** @deprecated */
    public void putValue(String name, Object value);
    /** @deprecated */
    public void removeValue(String name);
    public void invalidate();
    public boolean isNew();
}
