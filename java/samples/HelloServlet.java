/*
 * HelloServlet - the classic first servlet, JSWDK 1.0 style.
 *
 *   <CFSERVLET CODE="HelloServlet">
 *     <CFSERVLETPARAM NAME="name" VALUE="Ben">
 *     <CFSERVLETPARAM NAME="visits" VARIABLE="Session.Visits" TYPE="INT">
 *   </CFSERVLET>
 *
 * Request parameters come from CFSERVLETPARAM NAME/VALUE (and the page's query string). An attribute passed
 * by reference ("visits") is incremented, and the CFML variable gets the new value after the tag.
 */
import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;

public class HelloServlet extends HttpServlet {
    private int served;

    public void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        served++;
        response.setContentType("text/html");
        response.setHeader("X-Servlet", "HelloServlet/1.0");
        PrintWriter out = response.getWriter();
        String name = request.getParameter("name");
        if (name == null) name = "World";
        out.println("<FONT FACE=\"Arial, Helvetica\" SIZE=\"2\">");
        out.println("<B>Hello, " + escape(name) + "!</B> This is HelloServlet, running inside "
                    + getServletContext().getServerInfo() + ".<BR>");
        Object visits = request.getAttribute("visits");
        if (visits instanceof Integer) {
            int v = ((Integer) visits).intValue() + 1;
            request.setAttribute("visits", new Integer(v));
            out.println("You have visited " + v + " time" + (v == 1 ? "" : "s") + ". ");
        }
        out.println("This servlet instance has served " + served + " request" + (served == 1 ? "" : "s") + ".</FONT>");
    }

    public void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        doGet(request, response);
    }

    public String getServletInfo() { return "HelloServlet - says hello"; }

    private static String escape(String s) {
        StringBuffer b = new StringBuffer();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '<') b.append("&lt;"); else if (c == '>') b.append("&gt;"); else if (c == '&') b.append("&amp;"); else b.append(c);
        }
        return b.toString();
    }
}
