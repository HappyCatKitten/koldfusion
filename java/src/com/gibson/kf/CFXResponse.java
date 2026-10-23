/*
 * KoldFusion Application Server 4.5 - the Response handed to Java CFX tags.
 * It implements both com.gibson.cfx.Response and the ColdFusion-compatible com.allaire.cfx.Response.
 * Everything is buffered and handed back to the server when processRequest returns.
 */
package com.gibson.kf;

import java.util.Vector;

public class CFXResponse implements com.gibson.cfx.Response, com.allaire.cfx.Response {
    private final StringBuffer out = new StringBuffer();
    private final StringBuffer dbg = new StringBuffer();
    final Vector ops = new Vector();        /* String[]{"var",name,value} or Object[]{"query",CFXQuery} */
    private final boolean debugging;

    public CFXResponse(boolean debugging) { this.debugging = debugging; }

    /** a CFML variable name: letters, digits and underscores, optionally scope.name */
    static boolean validName(String s) {
        if (s == null || s.length() == 0) return false;
        boolean start = true;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '.') { if (start) return false; start = true; continue; }
            if (start) { if (!Character.isLetter(c) && c != '_') return false; start = false; }
            else if (!Character.isLetterOrDigit(c) && c != '_') return false;
        }
        return !start;
    }

    public CFXQuery addQuery(String name, String[] columns) throws IllegalArgumentException {
        if (!validName(name)) throw new IllegalArgumentException("Invalid query name: " + name);
        CFXQuery q = new CFXQuery(name, columns);
        ops.addElement(new Object[] { "query", q });
        return q;
    }

    public void setVariable(String name, String value) throws IllegalArgumentException {
        if (!validName(name)) throw new IllegalArgumentException("Invalid variable name: " + name);
        ops.addElement(new String[] { "var", name, value == null ? "" : value });
    }

    public synchronized void write(String output) { if (output != null) out.append(output); }

    public synchronized void writeDebug(String output) { if (debugging && output != null) dbg.append(output); }

    String output() { return out.toString(); }

    String debugOutput() { return dbg.toString(); }

    /** what DebugResponse.printResults() prints */
    protected String describe() {
        StringBuffer b = new StringBuffer();
        b.append("[ Output ]\n").append(out).append('\n');
        if (dbg.length() > 0) b.append("[ Debug Output ]\n").append(dbg).append('\n');
        for (int i = 0; i < ops.size(); i++) {
            Object o = ops.elementAt(i);
            if (o instanceof String[]) {
                String[] v = (String[]) o;
                b.append("[ Variable ] ").append(v[1]).append(" = \"").append(v[2]).append("\"\n");
            } else {
                CFXQuery q = (CFXQuery) ((Object[]) o)[1];
                b.append("[ Query ] ").append(q.getName()).append(" (").append(q.getRowCount()).append(" rows)\n").append(q);
            }
        }
        return b.toString();
    }
}
