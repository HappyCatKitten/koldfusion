/*
 * KoldFusion Application Server 4.5 - Java CFX API
 * Compatibility shim: the same interfaces under the package name ColdFusion 4.5 used, so
 * Java CFX tags written in 1999 compile and run unchanged. New tags may use com.gibson.cfx instead.
 */
package com.allaire.cfx;

/** A Response for testing a CFX tag from the command line; printResults() shows what the tag did. */
public class DebugResponse extends com.gibson.kf.CFXResponse implements Response {
    public DebugResponse() {
        super(true);
    }
    /** Prints the output, debug output, variables and queries the tag produced to System.out. */
    public void printResults() {
        System.out.print(describe());
        System.out.flush();
    }
}
