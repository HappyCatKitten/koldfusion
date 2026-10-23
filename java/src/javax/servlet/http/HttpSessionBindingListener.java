/*
 * KoldFusion Application Server 4.5 - a minimal Java Servlet API (2.1/2.2 level), written for KoldFusion so
 * CFSERVLET can run servlets in the embedded Java VM. Only what 1999-era servlets need is here.
 */
package javax.servlet.http;

public interface HttpSessionBindingListener extends java.util.EventListener {
    public void valueBound(HttpSessionBindingEvent event);
    public void valueUnbound(HttpSessionBindingEvent event);
}
