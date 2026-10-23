/*
 * KoldFusion Application Server 4.5 - a minimal Java Servlet API (2.1/2.2 level), written for KoldFusion so
 * CFSERVLET can run servlets in the embedded Java VM. Only what 1999-era servlets need is here.
 */
package javax.servlet;

/** Marker: the servlet engine never runs two requests through one instance at the same time. */
public interface SingleThreadModel {
}
