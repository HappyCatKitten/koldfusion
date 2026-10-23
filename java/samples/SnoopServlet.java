/*
 * SnoopServlet - shows everything the servlet engine knows about the request, like the snoop servlet every
 * 1999 servlet engine shipped. Handy for checking what CFSERVLET passes along.
 */
import java.io.*;
import java.util.*;
import javax.servlet.*;
import javax.servlet.http.*;

public class SnoopServlet extends HttpServlet {
    public void service(HttpServletRequest req, HttpServletResponse res) throws ServletException, IOException {
        res.setContentType("text/html");
        PrintWriter out = res.getWriter();
        out.println("<TABLE BORDER=1 CELLPADDING=2 CELLSPACING=0>");
        row(out, "<B>Request information</B>", "");
        row(out, "Servlet engine", getServletContext().getServerInfo());
        row(out, "Request method", req.getMethod());
        row(out, "Request URI", req.getRequestURI());
        row(out, "Request protocol", req.getProtocol());
        row(out, "Servlet path", req.getServletPath());
        row(out, "Query string", req.getQueryString());
        row(out, "Server name", req.getServerName());
        row(out, "Server port", String.valueOf(req.getServerPort()));
        row(out, "Remote address", req.getRemoteAddr());
        row(out, "Scheme", req.getScheme());
        Enumeration e = req.getParameterNames();
        if (e.hasMoreElements()) row(out, "<B>Parameters</B>", "");
        while (e.hasMoreElements()) {
            String n = (String) e.nextElement();
            String[] v = req.getParameterValues(n);
            StringBuffer b = new StringBuffer();
            for (int i = 0; i < v.length; i++) { if (i > 0) b.append(", "); b.append(v[i]); }
            row(out, n, b.toString());
        }
        e = req.getAttributeNames();
        if (e.hasMoreElements()) row(out, "<B>Attributes</B>", "");
        while (e.hasMoreElements()) {
            String n = (String) e.nextElement();
            Object v = req.getAttribute(n);
            row(out, n, v + " <I>(" + v.getClass().getName() + ")</I>");
        }
        e = req.getHeaderNames();
        if (e.hasMoreElements()) row(out, "<B>Headers</B>", "");
        while (e.hasMoreElements()) {
            String n = (String) e.nextElement();
            row(out, n, req.getHeader(n));
        }
        out.println("</TABLE>");
    }

    private static void row(PrintWriter out, String name, String value) {
        out.println("<TR><TD><FONT FACE=\"Arial\" SIZE=\"2\">" + name + "</FONT></TD><TD><FONT FACE=\"Arial\" SIZE=\"2\">"
                    + (value == null ? "<I>none</I>" : value) + "</FONT></TD></TR>");
    }
}
