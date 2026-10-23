/*
 * HelloColdFusion - the smallest possible Java CFX tag, written against the ColdFusion 4.5 API
 * (com.allaire.cfx) to show that 1999 tags run unchanged on KoldFusion.
 *
 *   <CFX_HelloColdFusion NAME="Les">
 */
import com.allaire.cfx.*;

public class HelloColdFusion implements CustomTag {
    public void processRequest(Request request, Response response) throws Exception {
        String strName = request.getAttribute("NAME");
        response.write("Hello, " + strName);
    }
}
