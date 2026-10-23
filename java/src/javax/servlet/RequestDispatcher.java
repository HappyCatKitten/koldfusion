/*
 * KoldFusion Application Server 4.5 - a minimal Java Servlet API (2.1/2.2 level), written for KoldFusion so
 * CFSERVLET can run servlets in the embedded Java VM. Only what 1999-era servlets need is here.
 */
package javax.servlet;

import java.io.IOException;

public interface RequestDispatcher {
    public void forward(ServletRequest request, ServletResponse response) throws ServletException, IOException;
    public void include(ServletRequest request, ServletResponse response) throws ServletException, IOException;
}
