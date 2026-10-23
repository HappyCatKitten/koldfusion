/*
 * KoldFusion Application Server 4.5 - Java CFX API
 * The KoldFusion Java CFX API.
 */
package com.gibson.cfx;

/** The attributes, query and settings a CFX tag was called with. */
public interface Request {
    /** True if the attribute was passed (attribute names are not case sensitive). */
    public boolean attributeExists(String name);
    /** True if the tag was called with a DEBUG attribute. */
    public boolean debug();
    /** The value of an attribute, or "" if it was not passed. */
    public String getAttribute(String name);
    /** The names of all attributes passed to the tag. */
    public String[] getAttributeList();
    /** An attribute as an int, or -1 if it was not passed. */
    public int getIntAttribute(String name) throws NumberFormatException;
    /** An attribute as an int, or def if it was not passed or is not a number. */
    public int getIntAttribute(String name, int def);
    /** The query named by the QUERY attribute, or null. */
    public Query getQuery();
    /** A setting stored for this tag in the server registry, or "". */
    public String getSetting(String name);
}
