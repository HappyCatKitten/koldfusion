/*
 * KoldFusion Application Server 4.5 - the Query handed to Java CFX tags.
 * It implements both com.gibson.cfx.Query and the ColdFusion-compatible com.allaire.cfx.Query.
 */
package com.gibson.kf;

import java.util.Vector;

public class CFXQuery implements com.gibson.cfx.Query, com.allaire.cfx.Query {
    private final String name;
    private final String[] columns;
    private final Vector rows = new Vector();     /* of String[] */
    boolean dirty;

    public CFXQuery(String name, String[] columns) throws IllegalArgumentException {
        if (columns == null) throw new IllegalArgumentException("The column list of a query cannot be null");
        this.name = name == null ? "" : name;
        this.columns = (String[]) columns.clone();
    }

    /** a copy of any Query implementation (used by DebugRequest) */
    public static CFXQuery from(Object q) {
        if (q == null) return null;
        if (q instanceof CFXQuery) return (CFXQuery) q;
        String name; String[] cols; int n;
        if (q instanceof com.allaire.cfx.Query) {
            com.allaire.cfx.Query a = (com.allaire.cfx.Query) q;
            name = a.getName(); cols = a.getColumns(); n = a.getRowCount();
            CFXQuery r = new CFXQuery(name, cols);
            for (int i = 1; i <= n; i++) { r.addRow(); for (int c = 1; c <= cols.length; c++) r.setData(i, c, a.getData(i, c)); }
            return r;
        }
        com.gibson.cfx.Query g = (com.gibson.cfx.Query) q;
        name = g.getName(); cols = g.getColumns(); n = g.getRowCount();
        CFXQuery r = new CFXQuery(name, cols);
        for (int i = 1; i <= n; i++) { r.addRow(); for (int c = 1; c <= cols.length; c++) r.setData(i, c, g.getData(i, c)); }
        return r;
    }

    /** a query passed in from CFML: data is row-major */
    static CFXQuery fromData(String name, String[] columns, String[] data, int nrows) {
        CFXQuery q = new CFXQuery(name, columns);
        int nc = columns.length;
        for (int r = 0; r < nrows; r++) {
            String[] row = new String[nc];
            for (int c = 0; c < nc; c++) row[c] = data[r * nc + c];
            q.rows.addElement(row);
        }
        return q;
    }

    String[] flatData() {
        int nc = columns.length;
        String[] out = new String[rows.size() * nc];
        for (int r = 0; r < rows.size(); r++) {
            String[] row = (String[]) rows.elementAt(r);
            for (int c = 0; c < nc; c++) out[r * nc + c] = row[c] == null ? "" : row[c];
        }
        return out;
    }

    public synchronized int addRow() {
        String[] row = new String[columns.length];
        for (int i = 0; i < row.length; i++) row[i] = "";
        rows.addElement(row);
        dirty = true;
        return rows.size();
    }

    public int getColumnIndex(String name) {
        for (int i = 0; i < columns.length; i++) if (columns[i].equalsIgnoreCase(name)) return i + 1;
        return -1;
    }

    public String[] getColumns() { return (String[]) columns.clone(); }

    private void check(int iRow, int iCol) {
        if (iRow < 1 || iRow > rows.size())
            throw new IndexOutOfBoundsException("Row " + iRow + " is out of range (the query " + name + " has " + rows.size() + " rows)");
        if (iCol < 1 || iCol > columns.length)
            throw new IndexOutOfBoundsException("Column " + iCol + " is out of range (the query " + name + " has " + columns.length + " columns)");
    }

    public synchronized String getData(int iRow, int iCol) throws IndexOutOfBoundsException {
        check(iRow, iCol);
        return ((String[]) rows.elementAt(iRow - 1))[iCol - 1];
    }

    public String getName() { return name; }

    public synchronized int getRowCount() { return rows.size(); }

    public synchronized void setData(int iRow, int iCol, String data) throws IndexOutOfBoundsException {
        check(iRow, iCol);
        ((String[]) rows.elementAt(iRow - 1))[iCol - 1] = data == null ? "" : data;
        dirty = true;
    }

    public String toString() {
        StringBuffer b = new StringBuffer();
        for (int c = 0; c < columns.length; c++) { if (c > 0) b.append('\t'); b.append(columns[c]); }
        b.append('\n');
        for (int r = 0; r < rows.size(); r++) {
            String[] row = (String[]) rows.elementAt(r);
            for (int c = 0; c < row.length; c++) { if (c > 0) b.append('\t'); b.append(row[c]); }
            b.append('\n');
        }
        return b.toString();
    }
}
