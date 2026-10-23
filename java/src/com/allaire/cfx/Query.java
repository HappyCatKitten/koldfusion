/*
 * KoldFusion Application Server 4.5 - Java CFX API
 * Compatibility shim: the same interfaces under the package name ColdFusion 4.5 used, so
 * Java CFX tags written in 1999 compile and run unchanged. New tags may use com.gibson.cfx instead.
 */
package com.allaire.cfx;

/** A CFML query. Rows and columns are numbered from 1. */
public interface Query {
    /** Adds an empty row and returns its index. */
    public int addRow();
    /** The 1-based index of a column (not case sensitive), or -1. */
    public int getColumnIndex(String name);
    /** The column names. */
    public String[] getColumns();
    /** The value of a cell. */
    public String getData(int iRow, int iCol) throws IndexOutOfBoundsException;
    /** The name of the query. */
    public String getName();
    /** The number of rows. */
    public int getRowCount();
    /** Sets the value of a cell. */
    public void setData(int iRow, int iCol, String data) throws IndexOutOfBoundsException;
}
