/*
 * KoldFusion Application Server 4.5 - a minimal Java Servlet API (2.1/2.2 level), written for KoldFusion so
 * CFSERVLET can run servlets in the embedded Java VM. Only what 1999-era servlets need is here.
 */
package javax.servlet;

import java.io.IOException;
import java.io.InputStream;

public abstract class ServletInputStream extends InputStream {
    protected ServletInputStream() { }
    public int readLine(byte[] b, int off, int len) throws IOException {
        if (len <= 0) return 0;
        int count = 0, c;
        while ((c = read()) != -1) {
            b[off++] = (byte) c;
            count++;
            if (c == '\n' || count == len) break;
        }
        return count > 0 ? count : -1;
    }
}
