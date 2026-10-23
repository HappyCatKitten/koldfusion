/*
 * KoldFusion Application Server 4.5 - a minimal Java Servlet API (2.1/2.2 level), written for KoldFusion so
 * CFSERVLET can run servlets in the embedded Java VM. Only what 1999-era servlets need is here.
 */
package javax.servlet.http;

import java.util.Hashtable;
import java.util.StringTokenizer;

public class HttpUtils {
    public HttpUtils() { }

    public static Hashtable parseQueryString(String s) {
        if (s == null) throw new IllegalArgumentException();
        Hashtable ht = new Hashtable();
        StringTokenizer st = new StringTokenizer(s, "&");
        while (st.hasMoreTokens()) {
            String pair = st.nextToken();
            int pos = pair.indexOf('=');
            if (pos == -1) throw new IllegalArgumentException();
            String key = decode(pair.substring(0, pos)), val = decode(pair.substring(pos + 1));
            String[] old = (String[]) ht.get(key), nv;
            if (old != null) { nv = new String[old.length + 1]; System.arraycopy(old, 0, nv, 0, old.length); nv[old.length] = val; }
            else nv = new String[] { val };
            ht.put(key, nv);
        }
        return ht;
    }

    static String decode(String s) {
        StringBuffer sb = new StringBuffer();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '+') sb.append(' ');
            else if (c == '%' && i + 2 < s.length()) {
                try { sb.append((char) Integer.parseInt(s.substring(i + 1, i + 3), 16)); i += 2; }
                catch (NumberFormatException e) { sb.append(c); }
            } else sb.append(c);
        }
        return sb.toString();
    }

    public static StringBuffer getRequestURL(HttpServletRequest req) {
        StringBuffer url = new StringBuffer();
        String scheme = req.getScheme();
        int port = req.getServerPort();
        url.append(scheme).append("://").append(req.getServerName());
        if (("http".equals(scheme) && port != 80) || ("https".equals(scheme) && port != 443)) url.append(':').append(port);
        url.append(req.getRequestURI());
        return url;
    }
}
