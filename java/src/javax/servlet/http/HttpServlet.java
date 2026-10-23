/*
 * KoldFusion Application Server 4.5 - a minimal Java Servlet API (2.1/2.2 level), written for KoldFusion so
 * CFSERVLET can run servlets in the embedded Java VM. Only what 1999-era servlets need is here.
 */
package javax.servlet.http;

import java.io.IOException;
import javax.servlet.GenericServlet;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;

public abstract class HttpServlet extends GenericServlet implements java.io.Serializable {
    public HttpServlet() { }

    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        resp.sendError(HttpServletResponse.SC_METHOD_NOT_ALLOWED, "HTTP method GET is not supported by this URL");
    }
    protected long getLastModified(HttpServletRequest req) { return -1; }
    protected void doHead(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException { doGet(req, resp); }
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        resp.sendError(HttpServletResponse.SC_METHOD_NOT_ALLOWED, "HTTP method POST is not supported by this URL");
    }
    protected void doPut(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        resp.sendError(HttpServletResponse.SC_METHOD_NOT_ALLOWED, "HTTP method PUT is not supported by this URL");
    }
    protected void doDelete(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        resp.sendError(HttpServletResponse.SC_METHOD_NOT_ALLOWED, "HTTP method DELETE is not supported by this URL");
    }
    protected void doOptions(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        resp.setHeader("Allow", "GET, HEAD, POST, PUT, DELETE, OPTIONS, TRACE");
    }
    protected void doTrace(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        resp.setContentType("message/http");
        resp.getWriter().print("TRACE " + req.getRequestURI() + " " + req.getProtocol() + "\r\n");
    }

    protected void service(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        String method = req.getMethod();
        if (method.equals("GET")) {
            long lm = getLastModified(req);
            if (lm != -1 && lm / 1000 * 1000 <= req.getDateHeader("If-Modified-Since")) { resp.setStatus(HttpServletResponse.SC_NOT_MODIFIED); return; }
            if (lm != -1) resp.setDateHeader("Last-Modified", lm);
            doGet(req, resp);
        } else if (method.equals("HEAD")) doHead(req, resp);
        else if (method.equals("POST")) doPost(req, resp);
        else if (method.equals("PUT")) doPut(req, resp);
        else if (method.equals("DELETE")) doDelete(req, resp);
        else if (method.equals("OPTIONS")) doOptions(req, resp);
        else if (method.equals("TRACE")) doTrace(req, resp);
        else resp.sendError(HttpServletResponse.SC_NOT_IMPLEMENTED, "Method " + method + " is not implemented by this servlet");
    }

    public void service(ServletRequest req, ServletResponse res) throws ServletException, IOException {
        if (!(req instanceof HttpServletRequest && res instanceof HttpServletResponse)) throw new ServletException("non-HTTP request or response");
        service((HttpServletRequest) req, (HttpServletResponse) res);
    }
}
