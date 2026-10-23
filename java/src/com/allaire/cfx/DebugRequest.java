/*
 * KoldFusion Application Server 4.5 - Java CFX API
 * Compatibility shim: the same interfaces under the package name ColdFusion 4.5 used, so
 * Java CFX tags written in 1999 compile and run unchanged. New tags may use com.gibson.cfx instead.
 */
package com.allaire.cfx;

import java.util.Hashtable;

/**
 * A Request for testing a CFX tag from the command line, without the server:
 * <pre>
 *   public static void main(String[] argv) {
 *       try {
 *           Hashtable attributes = new Hashtable();
 *           attributes.put("NAME", "Ben");
 *           DebugRequest request = new DebugRequest(attributes);
 *           DebugResponse response = new DebugResponse();
 *           new MyTag().processRequest(request, response);
 *           response.printResults();
 *       } catch (Throwable e) { e.printStackTrace(); }
 *   }
 * </pre>
 */
public class DebugRequest extends com.gibson.kf.CFXRequest implements Request {
    public DebugRequest(Hashtable attributes) {
        this(attributes, null, null);
    }
    public DebugRequest(Hashtable attributes, Query query) {
        this(attributes, query, null);
    }
    public DebugRequest(Hashtable attributes, Query query, Hashtable settings) {
        super(attributes, com.gibson.kf.CFXQuery.from(query), settings);
    }
}
