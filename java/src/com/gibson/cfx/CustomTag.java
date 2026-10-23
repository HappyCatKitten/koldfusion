/*
 * KoldFusion Application Server 4.5 - Java CFX API
 * The KoldFusion Java CFX API.
 */
package com.gibson.cfx;

/**
 * A Java CFX tag. Register the class on the CFX Tags page of the KoldFusion
 * Administrator (type Java) and call it from CFML as &lt;CFX_NAME ...&gt;. A new
 * instance is created for every request.
 */
public interface CustomTag {
    /** Process one invocation of the tag. Throwing an exception reports a CFML error. */
    public void processRequest(Request request, Response response) throws Exception;
}
