/*
 * KoldFusion Application Server 4.5 - Java CFX API
 * Compatibility shim: the same interfaces under the package name ColdFusion 4.5 used, so
 * Java CFX tags written in 1999 compile and run unchanged. New tags may use com.gibson.cfx instead.
 */
package com.allaire.cfx;

/** What a CFX tag sends back to the page. */
public interface Response {
    /** Creates a query (with no rows) in the calling page. */
    public Query addQuery(String name, String[] columns) throws IllegalArgumentException;
    /** Sets a variable in the calling page. */
    public void setVariable(String name, String value) throws IllegalArgumentException;
    /** Writes text to the page. */
    public void write(String output);
    /** Writes debugging text; shown only when the tag was called with a DEBUG attribute. */
    public void writeDebug(String output);
}
