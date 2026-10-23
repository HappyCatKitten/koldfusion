/*
 * CFX_JAVAHELLO - a friendly Java CFX tag in the 1999 style (com.allaire.cfx API).
 *
 *   <CFX_JAVAHELLO NAME="Ben" [TIMES="3"] [VARIABLE="greeting"] [DEBUG]>
 *
 * Writes a greeting TIMES times, and optionally stores it in a variable of the calling page.
 */
import com.allaire.cfx.*;

public class JavaHello implements CustomTag {
    public void processRequest(Request request, Response response) throws Exception {
        if (!request.attributeExists("NAME"))
            throw new Exception("Missing attribute (NAME is a required attribute for this tag)");
        String name = request.getAttribute("NAME");
        int times = request.getIntAttribute("TIMES", 1);
        if (times < 1 || times > 100) throw new Exception("TIMES must be between 1 and 100");
        String greeting = "Hello, " + name + "! Greetings from Java " + System.getProperty("java.version")
                        + " inside KoldFusion.";
        for (int i = 0; i < times; i++) response.write("<B>" + greeting + "</B><BR>\n");
        if (request.attributeExists("VARIABLE")) response.setVariable(request.getAttribute("VARIABLE"), greeting);
        if (request.debug()) {
            String[] attrs = request.getAttributeList();
            response.writeDebug("CFX_JAVAHELLO called with " + attrs.length + " attributes");
            for (int i = 0; i < attrs.length; i++) response.writeDebug("\n  " + attrs[i] + "=" + request.getAttribute(attrs[i]));
        }
    }
}
