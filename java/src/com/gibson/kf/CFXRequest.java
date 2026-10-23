/*
 * KoldFusion Application Server 4.5 - the Request handed to Java CFX tags.
 * It implements both com.gibson.cfx.Request and the ColdFusion-compatible com.allaire.cfx.Request.
 */
package com.gibson.kf;

import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Vector;

public class CFXRequest implements com.gibson.cfx.Request, com.allaire.cfx.Request {
    private final Vector names = new Vector();          /* attribute names as passed */
    private final Hashtable attrs = new Hashtable();     /* UPPERCASE name -> value */
    private final Hashtable settings = new Hashtable();  /* UPPERCASE name -> value */
    private final CFXQuery query;

    public CFXRequest(Hashtable attributes, CFXQuery query, Hashtable settings) {
        if (attributes != null)
            for (Enumeration e = attributes.keys(); e.hasMoreElements(); ) {
                Object k = e.nextElement();
                put(String.valueOf(k), String.valueOf(attributes.get(k)));
            }
        if (settings != null)
            for (Enumeration e = settings.keys(); e.hasMoreElements(); ) {
                Object k = e.nextElement();
                this.settings.put(String.valueOf(k).toUpperCase(), String.valueOf(settings.get(k)));
            }
        this.query = query;
    }

    CFXRequest(String[] an, String[] av, CFXQuery query, String[] sn, String[] sv) {
        for (int i = 0; i < an.length; i++) put(an[i], av[i]);
        for (int i = 0; i < sn.length; i++) settings.put(sn[i].toUpperCase(), sv[i]);
        this.query = query;
    }

    private void put(String name, String value) {
        String k = name.toUpperCase();
        if (!attrs.containsKey(k)) names.addElement(k);
        attrs.put(k, value == null ? "" : value);
    }

    public boolean attributeExists(String name) { return name != null && attrs.containsKey(name.toUpperCase()); }

    public boolean debug() { return attributeExists("DEBUG"); }

    public String getAttribute(String name) {
        Object v = name == null ? null : attrs.get(name.toUpperCase());
        return v == null ? "" : (String) v;
    }

    public String[] getAttributeList() {
        String[] r = new String[names.size()];
        names.copyInto(r);
        return r;
    }

    public int getIntAttribute(String name) throws NumberFormatException {
        if (!attributeExists(name)) return -1;
        return Integer.parseInt(getAttribute(name).trim());
    }

    public int getIntAttribute(String name, int def) {
        if (!attributeExists(name)) return def;
        try { return Integer.parseInt(getAttribute(name).trim()); } catch (NumberFormatException e) { return def; }
    }

    public CFXQuery getQuery() { return query; }

    public String getSetting(String name) {
        Object v = name == null ? null : settings.get(name.toUpperCase());
        return v == null ? "" : (String) v;
    }
}
