/*
 * KoldFusion Application Server 4.5 - a minimal Java Servlet API (2.1/2.2 level), written for KoldFusion so
 * CFSERVLET can run servlets in the embedded Java VM. Only what 1999-era servlets need is here.
 */
package javax.servlet;

public class UnavailableException extends ServletException {
    private final int seconds;
    public UnavailableException(String msg) { super(msg); seconds = -1; }
    public UnavailableException(String msg, int seconds) { super(msg); this.seconds = seconds <= 0 ? -1 : seconds; }
    /** @deprecated */
    public UnavailableException(Servlet servlet, String msg) { this(msg); }
    /** @deprecated */
    public UnavailableException(int seconds, Servlet servlet, String msg) { this(msg, seconds); }
    public boolean isPermanent() { return seconds == -1; }
    public int getUnavailableSeconds() { return seconds; }
}
