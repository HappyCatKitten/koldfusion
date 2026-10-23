/*
 * KoldFusion Application Server 4.5 - Java CFX API
 * Compatibility shim: the same interfaces under the package name ColdFusion 4.5 used, so
 * Java CFX tags written in 1999 compile and run unchanged. New tags may use com.gibson.cfx instead.
 */
package com.allaire.cfx;

/**
 * A Java CFX tag. Register the class on the CFX Tags page of the KoldFusion
 * Administrator (type Java) and call it from CFML as &lt;CFX_NAME ...&gt;. A new
 * instance is created for every request.
 */
public interface CustomTag {
    /** Process one invocation of the tag. Throwing an exception reports a CFML error. */
    public void processRequest(Request request, Response response) throws Exception;
}
