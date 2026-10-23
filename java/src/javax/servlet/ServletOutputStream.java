/*
 * KoldFusion Application Server 4.5 - a minimal Java Servlet API (2.1/2.2 level), written for KoldFusion so
 * CFSERVLET can run servlets in the embedded Java VM. Only what 1999-era servlets need is here.
 */
package javax.servlet;

import java.io.IOException;
import java.io.OutputStream;

public abstract class ServletOutputStream extends OutputStream {
    protected ServletOutputStream() { }
    public void print(String s) throws IOException {
        if (s == null) s = "null";
        for (int i = 0; i < s.length(); i++) write(s.charAt(i));
    }
    public void print(boolean b) throws IOException { print(b ? "true" : "false"); }
    public void print(char c) throws IOException { print(String.valueOf(c)); }
    public void print(int i) throws IOException { print(String.valueOf(i)); }
    public void print(long l) throws IOException { print(String.valueOf(l)); }
    public void print(float f) throws IOException { print(String.valueOf(f)); }
    public void print(double d) throws IOException { print(String.valueOf(d)); }
    public void println() throws IOException { print("\r\n"); }
    public void println(String s) throws IOException { print(s); println(); }
    public void println(boolean b) throws IOException { print(b); println(); }
    public void println(char c) throws IOException { print(c); println(); }
    public void println(int i) throws IOException { print(i); println(); }
    public void println(long l) throws IOException { print(l); println(); }
    public void println(float f) throws IOException { print(f); println(); }
    public void println(double d) throws IOException { print(d); println(); }
}
