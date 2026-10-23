/*
 * CFX_JAVAQUERY - a Java CFX tag that reads and creates queries (com.gibson.cfx API).
 *
 *   <CFX_JAVAQUERY ACTION="properties" NAME="props">
 *       creates a query PROPS(Name, Value) of the Java system properties
 *   <CFX_JAVAQUERY ACTION="stats" QUERY="employees" COLUMN="Salary" [NAME="stats"]>
 *       sets stats.Count, stats.Sum, stats.Min, stats.Max and stats.Average for a numeric column,
 *       and adds a column RANK to nothing: queries handed to a CFX are read with getData()
 *   <CFX_JAVAQUERY ACTION="upper" QUERY="employees" COLUMN="LastName">
 *       changes a column of the query passed in to upper case (setData on the input query)
 *
 * It can also be tested without the server:  java -cp cfx.jar:. JavaQuery
 */
import com.gibson.cfx.*;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Properties;

public class JavaQuery implements CustomTag {
    public void processRequest(Request request, Response response) throws Exception {
        String action = request.attributeExists("ACTION") ? request.getAttribute("ACTION").toLowerCase() : "properties";
        if (action.equals("properties")) {
            String name = request.attributeExists("NAME") ? request.getAttribute("NAME") : "JavaProperties";
            Query q = response.addQuery(name, new String[] { "Name", "Value" });
            Properties p = System.getProperties();
            java.util.TreeSet keys = new java.util.TreeSet(p.keySet());
            for (java.util.Iterator i = keys.iterator(); i.hasNext(); ) {
                String k = (String) i.next();
                if (k.startsWith("java.") || k.startsWith("os.") || k.startsWith("user.") || k.startsWith("koldfusion.")) {
                    int row = q.addRow();
                    q.setData(row, 1, k);
                    q.setData(row, 2, p.getProperty(k));
                }
            }
            response.writeDebug("CFX_JAVAQUERY created " + q.getRowCount() + " rows in " + name);
            return;
        }
        Query q = request.getQuery();
        if (q == null) throw new Exception("ACTION=\"" + action + "\" needs a QUERY attribute");
        String colname = request.getAttribute("COLUMN");
        int col = q.getColumnIndex(colname);
        if (col < 1) throw new Exception("The query " + q.getName() + " has no column named " + colname);
        if (action.equals("stats")) {
            String var = request.attributeExists("NAME") ? request.getAttribute("NAME") : "stats";
            double sum = 0, min = Double.MAX_VALUE, max = -Double.MAX_VALUE;
            int n = q.getRowCount();
            for (int r = 1; r <= n; r++) {
                double d = Double.valueOf(q.getData(r, col).trim()).doubleValue();
                sum += d; if (d < min) min = d; if (d > max) max = d;
            }
            response.setVariable(var + ".Count", String.valueOf(n));
            response.setVariable(var + ".Sum", fmt(sum));
            response.setVariable(var + ".Min", n > 0 ? fmt(min) : "");
            response.setVariable(var + ".Max", n > 0 ? fmt(max) : "");
            response.setVariable(var + ".Average", n > 0 ? fmt(sum / n) : "");
        } else if (action.equals("upper")) {
            for (int r = 1; r <= q.getRowCount(); r++) q.setData(r, col, q.getData(r, col).toUpperCase());
        } else {
            throw new Exception("Unknown ACTION " + action + " (use properties, stats or upper)");
        }
    }

    private static String fmt(double d) {
        return d == Math.floor(d) && Math.abs(d) < 1e15 ? String.valueOf((long) d) : String.valueOf(d);
    }

    /* the DebugRequest/DebugResponse harness: run the tag from the command line */
    public static void main(String[] argv) {
        try {
            Hashtable attributes = new Hashtable();
            attributes.put("ACTION", "stats");
            attributes.put("COLUMN", "Salary");
            attributes.put("NAME", "pay");
            String[] columns = { "LastName", "Salary" };
            String[][] data = { { "Forta", "52000" }, { "Allaire", "61000" }, { "Gibson", "48000" } };
            DebugQuery query = new DebugQuery("Employees", columns, data);
            DebugRequest request = new DebugRequest(attributes, query);
            DebugResponse response = new DebugResponse();
            new JavaQuery().processRequest(request, response);
            response.printResults();
        } catch (Throwable e) {
            e.printStackTrace();
        }
    }
}
