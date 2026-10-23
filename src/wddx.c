/*
 * wddx.c - Web Distributed Data eXchange (WDDX 1.0), Allaire's 1998 XML
 * format for shipping CFML data between servers and JavaScript.
 */
#define _GNU_SOURCE
#include "engine.h"
#include <stdlib.h>
#include <ctype.h>

#define TAG(nm) void tag_##nm(Ctx *c, Node *n, int *flow)

static void wddx_string(Buf *b, const char *s, size_t len) {
    buf_puts(b, "<string>");
    for (size_t i = 0; i < len; i++) {
        unsigned char ch = (unsigned char)s[i];
        if (ch == '<') buf_puts(b, "&lt;");
        else if (ch == '>') buf_puts(b, "&gt;");
        else if (ch == '&') buf_puts(b, "&amp;");
        else if (ch < 32) buf_printf(b, "<char code='%02X'/>", ch);
        else buf_putc(b, (char)ch);
    }
    buf_puts(b, "</string>");
}

static void wddx_dt(Buf *b, double d, int tz) {
    int y, mo, dd, h, mi, s;
    date_to_parts(d, &y, &mo, &dd, &h, &mi, &s);
    buf_printf(b, "<dateTime>%04d-%d-%dT%d:%d:%d", y, mo, dd, h, mi, s);
    if (tz) {
        time_t t = time(NULL); struct tm lt; localtime_r(&t, &lt);
        long off = lt.tm_gmtoff;
        buf_printf(b, "%c%d:%d", off < 0 ? '-' : '+', (int)(labs(off) / 3600), (int)(labs(off) % 3600 / 60));
    }
    buf_puts(b, "</dateTime>");
}

static void wddx_val(Buf *b, Val v, int tz) {
    switch (v.t) {
    case VT_NULL: buf_puts(b, "<null/>"); break;
    case VT_BOOL: buf_printf(b, "<boolean value='%s'/>", v.u.b ? "true" : "false"); break;
    case VT_NUM: buf_printf(b, "<number>%s</number>", fmt_number(v.u.n)); break;
    case VT_DATE: wddx_dt(b, v.u.n, tz); break;
    case VT_STR: wddx_string(b, v.u.str.s, v.u.str.len); break;
    case VT_BINARY:
        buf_printf(b, "<binary length='%zu'>%s</binary>", v.u.str.len, base64_encode((const unsigned char *)v.u.str.s, v.u.str.len));
        break;
    case VT_ARRAY:
        buf_printf(b, "<array length='%d'>", v.u.a->n);
        for (int i = 0; i < v.u.a->n; i++) wddx_val(b, v.u.a->v[i], tz);
        buf_puts(b, "</array>");
        break;
    case VT_STRUCT:
        buf_puts(b, "<struct>");
        for (int i = 0; i < v.u.st->n; i++) {
            buf_printf(b, "<var name='%s'>", kf_upper(v.u.st->e[i].key));
            wddx_val(b, v.u.st->e[i].v, tz);
            buf_puts(b, "</var>");
        }
        buf_puts(b, "</struct>");
        break;
    case VT_QUERY: {
        Query *q = v.u.q;
        buf_printf(b, "<recordset rowCount='%d' fieldNames='%s'>", q->nrows, query_column_list(q));
        for (int col = 0; col < q->ncols; col++) {
            buf_printf(b, "<field name='%s'>", kf_upper(q->cols[col]));
            for (int r = 0; r < q->nrows; r++) wddx_val(b, query_get(q, col, r), tz);
            buf_puts(b, "</field>");
        }
        buf_puts(b, "</recordset>");
        break;
    }
    }
}

char *wddx_serialize(Val v, int tz) {
    Buf b; buf_init(&b);
    buf_puts(&b, "<wddxPacket version='1.0'><header/><data>");
    wddx_val(&b, v, tz);
    buf_puts(&b, "</data></wddxPacket>");
    return buf_cstr(&b);
}

/* ---------------------------------------------------------------- parse */
typedef struct XP { const char *s; const char *err; } XP;

static void xws(XP *x) { while (isspace((unsigned char)*x->s)) x->s++; }

/* read "<name attr='v' ...>" ; returns name, sets selfclose; attrs into struct */
static char *xtag(XP *x, Struct *attrs, int *selfclose, int *closing) {
    xws(x);
    if (*x->s != '<') { x->err = "Expected an element."; return NULL; }
    x->s++;
    *closing = 0;
    if (*x->s == '/') { *closing = 1; x->s++; }
    const char *ns = x->s;
    while (*x->s && !isspace((unsigned char)*x->s) && *x->s != '>' && *x->s != '/') x->s++;
    char *name = kstrndup(ns, x->s - ns);
    *selfclose = 0;
    for (;;) {
        xws(x);
        if (*x->s == '/' && x->s[1] == '>') { *selfclose = 1; x->s += 2; break; }
        if (*x->s == '>') { x->s++; break; }
        if (!*x->s) { x->err = "Unexpected end of packet."; return NULL; }
        const char *an = x->s;
        while (*x->s && *x->s != '=' && !isspace((unsigned char)*x->s)) x->s++;
        char *aname = kstrndup(an, x->s - an);
        xws(x);
        if (*x->s == '=') {
            x->s++; xws(x);
            char q = *x->s;
            if (q == '\'' || q == '"') {
                x->s++;
                const char *vs = x->s;
                while (*x->s && *x->s != q) x->s++;
                if (attrs) struct_set(attrs, aname, v_str(kstrndup(vs, x->s - vs)));
                if (*x->s) x->s++;
            }
        }
    }
    return name;
}

static char *xtext(XP *x) {
    Buf b; buf_init(&b);
    while (*x->s && *x->s != '<') {
        if (*x->s == '&') {
            if (!strncmp(x->s, "&lt;", 4)) { buf_putc(&b, '<'); x->s += 4; continue; }
            if (!strncmp(x->s, "&gt;", 4)) { buf_putc(&b, '>'); x->s += 4; continue; }
            if (!strncmp(x->s, "&amp;", 5)) { buf_putc(&b, '&'); x->s += 5; continue; }
            if (!strncmp(x->s, "&quot;", 6)) { buf_putc(&b, '"'); x->s += 6; continue; }
            if (!strncmp(x->s, "&apos;", 6)) { buf_putc(&b, '\''); x->s += 6; continue; }
        }
        buf_putc(&b, *x->s++);
    }
    return buf_cstr(&b);
}

static void xend(XP *x, const char *name) {
    int sc, cl;
    char *t = xtag(x, NULL, &sc, &cl);
    if (!t || !cl || kf_stricmp(t, name)) if (!x->err) x->err = kprintf("Expected </%s>.", name);
}

static Val xval(XP *x) {
    Struct *attrs = struct_new();
    int sc, cl;
    char *t = xtag(x, attrs, &sc, &cl);
    if (!t || x->err) return v_null();
    if (!kf_stricmp(t, "null")) { if (!sc) xend(x, t); return v_str(""); }
    if (!kf_stricmp(t, "boolean")) {
        Val *v = struct_get(attrs, "value");
        if (!sc) xend(x, t);
        return v_bool(v && !kf_stricmp(v_tostr(*v), "true"));
    }
    if (!kf_stricmp(t, "number")) { char *s = xtext(x); xend(x, t); double d = atof(s); return v_num(d); }
    if (!kf_stricmp(t, "string")) {
        if (sc) return v_str("");
        Buf b; buf_init(&b);
        for (;;) {
            buf_puts(&b, xtext(x));
            if (!strncmp(x->s, "<char", 5)) {
                Struct *ca = struct_new(); int s2, c2;
                xtag(x, ca, &s2, &c2);
                Val *code = struct_get(ca, "code");
                buf_putc(&b, (char)strtol(code ? v_tostr(*code) : "20", NULL, 16));
                if (!s2) xend(x, "char");
                continue;
            }
            break;
        }
        xend(x, t);
        return v_str(buf_cstr(&b));
    }
    if (!kf_stricmp(t, "dateTime")) {
        char *s = xtext(x); xend(x, t);
        int y = 0, mo = 0, d = 0, h = 0, mi = 0, se = 0;
        sscanf(s, "%d-%d-%dT%d:%d:%d", &y, &mo, &d, &h, &mi, &se);
        return v_date(date_from_parts(y, mo, d, h, mi, se));
    }
    if (!kf_stricmp(t, "binary")) { char *s = xtext(x); xend(x, t); size_t len; unsigned char *p = base64_decode(s, &len); return v_binary((char *)p, len); }
    if (!kf_stricmp(t, "array")) {
        Array *a = array_new();
        if (sc) return v_arr(a);
        for (;;) {
            xws(x);
            if (!strncmp(x->s, "</", 2)) break;
            array_push(a, xval(x));
            if (x->err) return v_null();
        }
        xend(x, t);
        return v_arr(a);
    }
    if (!kf_stricmp(t, "struct")) {
        Struct *s = struct_new();
        if (sc) return v_struct(s);
        for (;;) {
            xws(x);
            if (!strncmp(x->s, "</", 2)) break;
            Struct *va = struct_new();
            int s2, c2;
            char *vt = xtag(x, va, &s2, &c2);
            if (!vt || kf_stricmp(vt, "var")) { x->err = "Expected <var> in <struct>."; return v_null(); }
            Val *nm = struct_get(va, "name");
            Val v = xval(x);
            xend(x, "var");
            struct_set(s, nm ? v_tostr(*nm) : "", v);
            if (x->err) return v_null();
        }
        xend(x, t);
        return v_struct(s);
    }
    if (!kf_stricmp(t, "recordset")) {
        Val *fn = struct_get(attrs, "fieldNames");
        Val *rc = struct_get(attrs, "rowCount");
        Query *q = query_new(0, NULL);
        Array *names = list_to_array_k(fn ? v_tostr(*fn) : "", ",");
        for (int i = 0; i < names->n; i++) query_add_column(q, v_tostr(names->v[i]));
        int rows = rc ? atoi(v_tostr(*rc)) : 0;
        for (int i = 0; i < rows; i++) query_add_row(q);
        if (sc) return v_query(q);
        for (;;) {
            xws(x);
            if (!strncmp(x->s, "</", 2)) break;
            Struct *fa = struct_new();
            int s2, c2;
            char *ft = xtag(x, fa, &s2, &c2);
            if (!ft || kf_stricmp(ft, "field")) { x->err = "Expected <field> in <recordset>."; return v_null(); }
            Val *nm = struct_get(fa, "name");
            int col = query_add_column(q, nm ? v_tostr(*nm) : "COLUMN");
            for (int r = 0; !s2; r++) {
                xws(x);
                if (!strncmp(x->s, "</", 2)) break;
                Val v = xval(x);
                if (x->err) return v_null();
                if (r < q->nrows) query_set(q, col, r, v);
            }
            if (!s2) xend(x, "field");
        }
        xend(x, t);
        return v_query(q);
    }
    x->err = kprintf("Unknown WDDX element <%s>.", t);
    return v_null();
}

int wddx_deserialize(const char *packet, Val *out, const char **err) {
    XP x = { packet, NULL };
    const char *p = kf_stristr(packet, "<data>");
    if (!kf_stristr(packet, "<wddxPacket") || !p) { *err = "The input is not a WDDX packet."; return 0; }
    x.s = p + 6;
    xws(&x);
    if (!strncmp(x.s, "</data>", 7)) { *out = v_str(""); return 1; }
    *out = xval(&x);
    if (x.err) { *err = x.err; return 0; }
    return 1;
}

/* ---------------------------------------------------------------- JavaScript */
static int js_tmp;
static void js_val(Buf *b, const char *target, Val v) {
    switch (v.t) {
    case VT_NULL: buf_printf(b, "%s=null;", target); break;
    case VT_BOOL: buf_printf(b, "%s=%s;", target, v.u.b ? "true" : "false"); break;
    case VT_NUM: buf_printf(b, "%s=%s;", target, fmt_number(v.u.n)); break;
    case VT_DATE: {
        int y, mo, d, h, mi, s; date_to_parts(v.u.n, &y, &mo, &d, &h, &mi, &s);
        buf_printf(b, "%s=new Date(%d,%d,%d,%d,%d,%d);", target, y, mo - 1, d, h, mi, s);
        break;
    }
    case VT_ARRAY:
        buf_printf(b, "%s=new Array();", target);
        for (int i = 0; i < v.u.a->n; i++) js_val(b, kprintf("%s[%d]", target, i), v.u.a->v[i]);
        break;
    case VT_STRUCT:
        buf_printf(b, "%s=new Object();", target);
        for (int i = 0; i < v.u.st->n; i++) js_val(b, kprintf("%s[\"%s\"]", target, kf_lower(v.u.st->e[i].key)), v.u.st->e[i].v);
        break;
    case VT_QUERY: {
        Query *q = v.u.q;
        buf_printf(b, "%s=new WddxRecordset();", target);
        for (int col = 0; col < q->ncols; col++) {
            char *tmp = kprintf("_t%d", js_tmp++);
            buf_printf(b, "%s=new Array();", tmp);
            for (int r = 0; r < q->nrows; r++) js_val(b, kprintf("%s[%d]", tmp, r), query_get(q, col, r));
            buf_printf(b, "%s[\"%s\"]=%s;", target, kf_lower(q->cols[col]), tmp);
        }
        break;
    }
    default: {
        const char *s = v_tostr(v);
        buf_printf(b, "%s=\"", target);
        for (; *s; s++) {
            if (*s == '"' || *s == '\\') { buf_putc(b, '\\'); buf_putc(b, *s); }
            else if (*s == '\n') buf_puts(b, "\\n");
            else if (*s == '\r') buf_puts(b, "\\r");
            else if (*s == '<') buf_puts(b, "\\x3C");
            else buf_putc(b, *s);
        }
        buf_puts(b, "\";");
    }
    }
}

TAG(wddx) {
    (void)flow;
    const char *action = require_attr(c, n, "action");
    int present;
    Val in = attr_val(c, n, "input", &present);
    if (!present) kf_throw(c, "Application", "Attribute validation error for tag CFWDDX.", "The tag requires the attribute(s): INPUT.");
    const char *output = attr_str(c, n, "output", NULL);
    const char *toplevel = attr_str(c, n, "toplevelvariable", NULL);
    int tz = attr_bool(c, n, "usetimezoneinfo", 1);
    Val result;
    if (!kf_stricmp(action, "cfml2wddx")) result = v_str(wddx_serialize(in, tz));
    else if (!kf_stricmp(action, "wddx2cfml") || !kf_stricmp(action, "wddx2js")) {
        const char *err;
        Val v;
        if (!wddx_deserialize(val_simple_str(c, in, NULL), &v, &err))
            kf_throw(c, "Application", "Error processing CFWDDX", kprintf("WDDX packet parse error: %s", err));
        if (!kf_stricmp(action, "wddx2cfml")) result = v;
        else {
            if (!toplevel) kf_throw(c, "Application", "Attribute validation error for tag CFWDDX.", "TOPLEVELVARIABLE is required for WDDX2JS.");
            Buf b; buf_init(&b); js_tmp = 0; js_val(&b, toplevel, v); result = v_str(buf_cstr(&b));
        }
    } else if (!kf_stricmp(action, "cfml2js")) {
        if (!toplevel) kf_throw(c, "Application", "Attribute validation error for tag CFWDDX.", "TOPLEVELVARIABLE is required for CFML2JS.");
        Buf b; buf_init(&b); js_tmp = 0; js_val(&b, toplevel, in); result = v_str(buf_cstr(&b));
    } else
        kf_throw(c, "Application", "Attribute validation error for tag CFWDDX.",
                 "ACTION must be one of CFML2WDDX, WDDX2CFML, CFML2JS, WDDX2JS.");
    if (output) assign_path(c, output, result);
    else out_puts(c, val_simple_str(c, result, NULL));
}
