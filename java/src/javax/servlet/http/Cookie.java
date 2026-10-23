/*
 * KoldFusion Application Server 4.5 - a minimal Java Servlet API (2.1/2.2 level), written for KoldFusion so
 * CFSERVLET can run servlets in the embedded Java VM. Only what 1999-era servlets need is here.
 */
package javax.servlet.http;

public class Cookie implements Cloneable {
    private String name, value, comment, domain, path;
    private int maxAge = -1, version = 0;
    private boolean secure;

    public Cookie(String name, String value) {
        if (name == null || name.length() == 0 || name.startsWith("$") || name.indexOf(';') >= 0 || name.indexOf(',') >= 0 || name.indexOf(' ') >= 0)
            throw new IllegalArgumentException("Cookie name \"" + name + "\" is a reserved token");
        this.name = name; this.value = value;
    }
    public void setComment(String purpose) { comment = purpose; }
    public String getComment() { return comment; }
    public void setDomain(String pattern) { domain = pattern == null ? null : pattern.toLowerCase(); }
    public String getDomain() { return domain; }
    public void setMaxAge(int expiry) { maxAge = expiry; }
    public int getMaxAge() { return maxAge; }
    public void setPath(String uri) { path = uri; }
    public String getPath() { return path; }
    public void setSecure(boolean flag) { secure = flag; }
    public boolean getSecure() { return secure; }
    public String getName() { return name; }
    public void setValue(String newValue) { value = newValue; }
    public String getValue() { return value; }
    public int getVersion() { return version; }
    public void setVersion(int v) { version = v; }
    public Object clone() { try { return super.clone(); } catch (CloneNotSupportedException e) { throw new RuntimeException(e.getMessage()); } }
}
