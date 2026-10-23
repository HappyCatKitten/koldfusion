/*
 * KoldFusion Application Server 4.5 - a minimal Java Servlet API (2.1/2.2 level), written for KoldFusion so
 * CFSERVLET can run servlets in the embedded Java VM. Only what 1999-era servlets need is here.
 */
package javax.servlet.http;

public class HttpSessionBindingEvent extends java.util.EventObject {
    private final String name;
    public HttpSessionBindingEvent(HttpSession session, String name) { super(session); this.name = name; }
    public String getName() { return name; }
    public HttpSession getSession() { return (HttpSession) getSource(); }
}
