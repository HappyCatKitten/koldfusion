/*
 * KoldFusion Application Server 4.5 - a minimal Java Servlet API (2.1/2.2 level), written for KoldFusion so
 * CFSERVLET can run servlets in the embedded Java VM. Only what 1999-era servlets need is here.
 */
package javax.servlet;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.Locale;

public interface ServletResponse {
    public String getCharacterEncoding();
    public ServletOutputStream getOutputStream() throws IOException;
    public PrintWriter getWriter() throws IOException;
    public void setContentLength(int len);
    public void setContentType(String type);
    public void setBufferSize(int size);
    public int getBufferSize();
    public void flushBuffer() throws IOException;
    public boolean isCommitted();
    public void reset();
    public void setLocale(Locale loc);
    public Locale getLocale();
}
