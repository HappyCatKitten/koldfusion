/*
 * KoldFusion Application Server 4.5 - a minimal Java Servlet API (2.1/2.2 level), written for KoldFusion so
 * CFSERVLET can run servlets in the embedded Java VM. Only what 1999-era servlets need is here.
 */
package javax.servlet;

public class ServletException extends Exception {
    private Throwable rootCause;
    public ServletException() { super(); }
    public ServletException(String message) { super(message); }
    public ServletException(String message, Throwable rootCause) { super(message); this.rootCause = rootCause; }
    public ServletException(Throwable rootCause) { super(rootCause == null ? null : rootCause.toString()); this.rootCause = rootCause; }
    public Throwable getRootCause() { return rootCause; }
}
