/*
 * KoldFusion Application Server 4.5 - Java CFX API
 * Compatibility shim: the same interfaces under the package name ColdFusion 4.5 used, so
 * Java CFX tags written in 1999 compile and run unchanged. New tags may use com.gibson.cfx instead.
 */
package com.allaire.cfx;

/** A query for testing a CFX tag outside the server (see DebugRequest). */
public class DebugQuery extends com.gibson.kf.CFXQuery implements Query {
    public DebugQuery(String name, String[] columns) throws IllegalArgumentException {
        super(name, columns);
    }
    public DebugQuery(String name, String[] columns, String[][] data) throws IllegalArgumentException {
        super(name, columns);
        for (int r = 0; r < data.length; r++) {
            int row = addRow();
            for (int c = 0; c < columns.length && c < data[r].length; c++) setData(row, c + 1, data[r][c]);
        }
    }
}
