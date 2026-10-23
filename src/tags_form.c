/*
 * tags_form.c - CFFORM and friends, CFTABLE/CFCOL, CFAPPLET.
 *
 * In 1999 CFGRID, CFTREE, CFSLIDER and CFTEXTINPUT were Java applets
 * (the jars in /CFIDE/classes). Browsers no longer run applets, so KoldFusion
 * renders working HTML versions of them, styled like the applets were.
 */
#define _GNU_SOURCE
#include "engine.h"
#include "sql.h"
#include <stdlib.h>
#include <ctype.h>
#include <math.h>

#define TAG(nm) void tag_##nm(Ctx *c, Node *n, int *flow)

static __thread int form_counter;

static const char *H(const char *s) { return kf_html_escape(s); }
static int ListFindNoCase_k(const char *list, const char *v) {
    Array *a = list_to_array_k(list, ",");
    for (int i = 0; i < a->n; i++) if (!kf_stricmp(v_tostr(a->v[i]), v)) return 1;
    return 0;
}
static const char *js_q(const char *s) {
    Buf b; buf_init(&b);
    for (; *s; s++) { if (*s == '"' || *s == '\\') buf_putc(&b, '\\'); if (*s == '\n') { buf_puts(&b, "\\n"); continue; } buf_putc(&b, *s); }
    return buf_cstr(&b);
}

static const char *passthrough(Ctx *c, Node *n) {
    const char *p = attr_str(c, n, "passthrough", "");
    return *p ? kprintf(" %s", p) : "";
}

/* ================================================================ CFFORM */
TAG(form) {
    RState *rs = c->rs;
    const char *name = attr_str(c, n, "name", NULL);
    if (!name) name = kprintf("CFForm_%d", ++form_counter);
    const char *action = attr_str(c, n, "action", NULL);
    if (!action) action = struct_get(rs->cgi, "SCRIPT_NAME") ? v_tostr(*struct_get(rs->cgi, "SCRIPT_NAME")) : "";
    const char *method = attr_str(c, n, "method", "POST");
    const char *target = attr_str(c, n, "target", NULL);
    const char *enctype = attr_str(c, n, "enctype", NULL);
    const char *onsubmit = attr_str(c, n, "onsubmit", NULL);
    FormCtx *saved = c->form;
    FormCtx fc; memset(&fc, 0, sizeof fc);
    fc.name = name;
    buf_init(&fc.checks);
    c->form = &fc;
    struct_set(c->variables, "__kf_preservedata", v_bool(attr_bool(c, n, "preservedata", 0)));
    Buf body; buf_init(&body);
    Buf *sout = rs->out;
    rs->out = &body;
    exec_nodes(c, n->kids, n->nkids, flow);
    rs->out = sout;
    c->form = saved;
    struct_delete(c->variables, "__kf_preservedata");
    out_puts(c, "<SCRIPT LANGUAGE=\"JavaScript\" TYPE=\"text/javascript\" SRC=\"/CFIDE/scripts/cfform.js\"></SCRIPT>\n");
    out_puts(c, "<SCRIPT LANGUAGE=\"JavaScript\">\n<!--\n");
    out_puts(c, kprintf("function  _CF_check%s(_CF_this)\n{\n", name));
    out_puts(c, buf_cstr(&fc.checks));
    if (onsubmit) out_puts(c, kprintf("    %s\n", onsubmit));
    out_puts(c, "    return true;\n}\n//-->\n</SCRIPT>\n");
    out_puts(c, kprintf("<FORM NAME=\"%s\" ACTION=\"%s\" METHOD=%s", H(name), H(action), kf_upper(method)));
    if (target) out_puts(c, kprintf(" TARGET=\"%s\"", H(target)));
    if (enctype) out_puts(c, kprintf(" ENCTYPE=\"%s\"", H(enctype)));
    out_puts(c, kprintf(" onSubmit=\"return _CF_check%s(this)\"%s>\n", name, passthrough(c, n)));
    out_put(c, body.s ? body.s : "", body.len);
    out_puts(c, "</FORM>\n");
}

static const char *jsf(const char *field) {
    /* _CF_this.name, or _CF_this["a.b"] for names that are not JavaScript identifiers */
    for (const char *p = field; *p; p++)
        if (!isalnum((unsigned char)*p) && *p != '_') return kprintf("_CF_this[\"%s\"]", js_q(field));
    return kprintf("_CF_this.%s", field);
}
static void add_check(Ctx *c, const char *field, const char *cond, const char *msg) {
    if (!c->form) return;
    buf_printf(&c->form->checks,
        "    if  (%s)\n    {\n        if  (!_CF_onError(_CF_this, %s, %s.value, \"%s\"))\n        {\n"
        "            return false;\n        }\n    }\n", cond, jsf(field), jsf(field), js_q(msg));
}

static void require_form(Ctx *c, Node *n) {
    if (!c->form)
        kf_throw(c, "Template", kprintf("Context validation error for tag %s.", kf_upper(n->tag)),
                 "The tag must be nested inside a CFFORM tag.");
}

static const char *preserved(Ctx *c, const char *name, const char *def) {
    Val *p = struct_get(c->variables, "__kf_preservedata");
    if (p && p->t == VT_BOOL && p->u.b) {
        Val *f = struct_get(c->rs->form, name);
        if (f) return v_tostr(*f);
    }
    return def;
}

static void input_validation(Ctx *c, Node *n, const char *name, const char *type) {
    const char *msg = attr_str(c, n, "message", NULL);
    int required = attr_bool(c, n, "required", 0);
    const char *validate = attr_str(c, n, "validate", NULL);
    const char *range = attr_str(c, n, "range", NULL);
    const char *onvalidate = attr_str(c, n, "onvalidate", NULL);
    if (required) add_check(c, name, kprintf("!_CF_hasValue(%s, \"%s\" )", jsf(name), kf_upper(type)),
                            msg ? msg : kprintf("Error in %s text.", name));
    if (validate) {
        const char *fn = NULL;
        if (!kf_stricmp(validate, "date")) fn = "_CF_checkdate";
        else if (!kf_stricmp(validate, "eurodate")) fn = "_CF_checkeurodate";
        else if (!kf_stricmp(validate, "time")) fn = "_CF_checktime";
        else if (!kf_stricmp(validate, "float")) fn = "_CF_checknumber";
        else if (!kf_stricmp(validate, "integer")) fn = "_CF_checkinteger";
        else if (!kf_stricmp(validate, "telephone")) fn = "_CF_checkphone";
        else if (!kf_stricmp(validate, "zipcode")) fn = "_CF_checkzip";
        else if (!kf_stricmp(validate, "creditcard")) fn = "_CF_checkcreditcard";
        else if (!kf_stricmp(validate, "social_security_number")) fn = "_CF_checkssn";
        else kf_throw(c, "Application", kprintf("Attribute validation error for tag %s.", kf_upper(n->tag)),
                      kprintf("The value of the attribute VALIDATE, which is currently \"%s\", is invalid.", H(validate)));
        add_check(c, name, kprintf("!%s(%s.value)", fn, jsf(name)), msg ? msg : kprintf("Error in %s text.", name));
    }
    if (range) {
        Array *r = list_to_array_k(range, ",");
        const char *mn = r->n > 0 ? v_tostr(r->v[0]) : "", *mx = r->n > 1 ? v_tostr(r->v[1]) : "";
        add_check(c, name, kprintf("!_CF_checkrange(%s.value, %s, %s)", jsf(name), *mn ? mn : "null", *mx ? mx : "null"),
                  msg ? msg : kprintf("Error in %s text.", name));
    }
    if (onvalidate) add_check(c, name, kprintf("!%s(_CF_this, %s, %s.value)", onvalidate, jsf(name), jsf(name)),
                              msg ? msg : kprintf("Error in %s text.", name));
}

TAG(input) {
    (void)flow;
    require_form(c, n);
    const char *name = require_attr(c, n, "name");
    const char *type = attr_str(c, n, "type", "text");
    int choice = !kf_stricmp(type, "radio") || !kf_stricmp(type, "checkbox");
    const char *value = choice ? attr_str(c, n, "value", NULL) : preserved(c, name, attr_str(c, n, "value", NULL));
    int checked = attr_bool(c, n, "checked", 0);
    if (choice) {
        const char *sub = preserved(c, name, NULL);
        if (sub) checked = ListFindNoCase_k(sub, value ? value : "on");
    }
    Buf b; buf_init(&b);
    buf_printf(&b, "<INPUT TYPE=\"%s\" NAME=\"%s\"", kf_lower(type), H(name));
    if (value) buf_printf(&b, " VALUE=\"%s\"", H(value));
    const char *size = attr_str(c, n, "size", NULL), *maxlen = attr_str(c, n, "maxlength", NULL);
    if (size) buf_printf(&b, " SIZE=%s", H(size));
    if (maxlen) buf_printf(&b, " MAXLENGTH=%s", H(maxlen));
    if (checked) buf_puts(&b, " CHECKED");
    buf_printf(&b, "%s>", passthrough(c, n));
    out_puts(c, buf_cstr(&b));
    input_validation(c, n, name, kf_stricmp(type, "password") ? type : "TEXT");
}

TAG(textinput) {
    (void)flow;
    require_form(c, n);
    const char *name = require_attr(c, n, "name");
    const char *value = preserved(c, name, attr_str(c, n, "value", ""));
    Buf style; buf_init(&style);
    const char *font = attr_str(c, n, "font", NULL), *bg = attr_str(c, n, "bgcolor", NULL), *fg = attr_str(c, n, "textcolor", NULL);
    if (font) buf_printf(&style, "font-family:%s;", font);
    if (attr_str(c, n, "fontsize", NULL)) buf_printf(&style, "font-size:%spt;", attr_str(c, n, "fontsize", ""));
    if (bg) buf_printf(&style, "background:%s;", bg);
    if (fg) buf_printf(&style, "color:%s;", fg);
    if (attr_bool(c, n, "bold", 0)) buf_puts(&style, "font-weight:bold;");
    if (attr_bool(c, n, "italic", 0)) buf_puts(&style, "font-style:italic;");
    out_puts(c, kprintf("<INPUT TYPE=\"text\" NAME=\"%s\" VALUE=\"%s\" SIZE=%s%s STYLE=\"%s\">", H(name), H(value),
                        attr_str(c, n, "size", "20"), attr_str(c, n, "maxlength", NULL) ? kprintf(" MAXLENGTH=%s", attr_str(c, n, "maxlength", "")) : "",
                        buf_cstr(&style)));
    input_validation(c, n, name, "TEXT");
}

TAG(select) {
    require_form(c, n);
    const char *name = require_attr(c, n, "name");
    Buf b; buf_init(&b);
    buf_printf(&b, "<SELECT NAME=\"%s\"", H(name));
    if (attr_str(c, n, "size", NULL)) buf_printf(&b, " SIZE=%s", attr_str(c, n, "size", ""));
    if (attr_bool(c, n, "multiple", 0)) buf_puts(&b, " MULTIPLE");
    buf_printf(&b, "%s>\n", passthrough(c, n));
    const char *selected = preserved(c, name, attr_str(c, n, "selected", ""));
    int present;
    Val qv = attr_val(c, n, "query", &present);
    if (present) {
        Query *q = qv.t == VT_QUERY ? qv.u.q : NULL;
        if (!q) { Val t; if (resolve_path(c, v_tostr(qv), &t) && t.t == VT_QUERY) q = t.u.q; }
        if (!q) kf_throw(c, "Application", "Attribute validation error for tag CFSELECT.", "QUERY must name a query.");
        const char *vcol = require_attr(c, n, "value");
        const char *dcol = attr_str(c, n, "display", vcol);
        int vi = query_col_index(q, vcol), di = query_col_index(q, dcol);
        if (vi < 0) kf_throw(c, "Application", "Attribute validation error for tag CFSELECT.", kprintf("Column %s not found.", kf_upper(vcol)));
        if (di < 0) di = vi;
        Array *sel = list_to_array_k(selected, ",");
        for (int r = 0; r < q->nrows; r++) {
            const char *v = v_tostr(query_get(q, vi, r));
            int is = 0;
            for (int i = 0; i < sel->n; i++) if (!strcmp(v_tostr(sel->v[i]), v)) is = 1;
            buf_printf(&b, "<OPTION VALUE=\"%s\"%s>%s\n", H(v), is ? " SELECTED" : "", H(v_tostr(query_get(q, di, r))));
        }
    }
    out_puts(c, buf_cstr(&b));
    exec_nodes(c, n->kids, n->nkids, flow);
    out_puts(c, "</SELECT>");
    if (attr_bool(c, n, "required", 0))
        add_check(c, name, kprintf("!_CF_hasValue(%s, \"SELECT\" )", jsf(name)),
                  attr_str(c, n, "message", kprintf("Error in %s.", name)));
}

TAG(slider) {
    (void)flow;
    require_form(c, n);
    const char *name = require_attr(c, n, "name");
    const char *range = attr_str(c, n, "range", "0,100");
    Array *r = list_to_array_k(range, ",");
    double mn = r->n ? atof(v_tostr(r->v[0])) : 0, mx = r->n > 1 ? atof(v_tostr(r->v[1])) : 100;
    double scale = attr_num(c, n, "scale", 1);
    if (scale <= 0) scale = 1;
    double value = attr_num(c, n, "value", mn);
    const char *label = attr_str(c, n, "label", NULL);
    Buf b; buf_init(&b);
    buf_printf(&b, "<TABLE BORDER=1 CELLPADDING=2 CELLSPACING=0 BGCOLOR=\"%s\"><TR><TD><FONT FACE=\"Arial\" SIZE=1>",
               attr_str(c, n, "bgcolor", "#C0C0C0"));
    if (label) {
        const char *lb = label;
        const char *pv = kf_stristr(lb, "%value%");
        if (pv) lb = kprintf("%.*s%s%s", (int)(pv - lb), lb, fmt_number(value), pv + 7);
        buf_printf(&b, "%s ", H(lb));
    }
    if ((mx - mn) / scale <= 500) {
        buf_printf(&b, "<SELECT NAME=\"%s\">", H(name));
        for (double v = mn; v <= mx + 1e-9; v += scale)
            buf_printf(&b, "<OPTION%s>%s", fabs(v - value) < 1e-9 ? " SELECTED" : "", fmt_number(v));
        buf_puts(&b, "</SELECT>");
    } else buf_printf(&b, "<INPUT TYPE=\"text\" NAME=\"%s\" VALUE=\"%s\" SIZE=6>", H(name), fmt_number(value));
    buf_printf(&b, " <I>(%s-%s)</I></FONT></TD></TR></TABLE>", fmt_number(mn), fmt_number(mx));
    out_puts(c, buf_cstr(&b));
}

/* ================================================================ CFGRID */
typedef struct GridCol { const char *name, *header, *width, *align, *href, *hrefkey; int display, select; } GridCol;
typedef struct GridCtx { GridCol cols[64]; int ncols; Array *rows; } GridCtx;
static __thread GridCtx *t_grid;

TAG(gridcolumn) {
    (void)flow;
    if (!t_grid) kf_throw(c, "Template", "Context validation error for tag CFGRIDCOLUMN.", "The tag must be nested inside a CFGRID tag.");
    if (t_grid->ncols >= 64) return;
    GridCol *g = &t_grid->cols[t_grid->ncols++];
    g->name = require_attr(c, n, "name");
    g->header = attr_str(c, n, "header", g->name);
    g->width = attr_str(c, n, "width", NULL);
    g->align = attr_str(c, n, "dataalign", "left");
    g->href = attr_str(c, n, "href", NULL);
    g->hrefkey = attr_str(c, n, "hrefkey", NULL);
    g->display = attr_bool(c, n, "display", 1);
    g->select = attr_bool(c, n, "select", 1);
}

TAG(gridrow) {
    (void)flow;
    if (!t_grid) kf_throw(c, "Template", "Context validation error for tag CFGRIDROW.", "The tag must be nested inside a CFGRID tag.");
    array_push(t_grid->rows, v_str(require_attr(c, n, "data")));
}

TAG(grid) {
    require_form(c, n);
    const char *name = require_attr(c, n, "name");
    const char *mode = attr_str(c, n, "selectmode", "browse");
    int edit = !kf_stricmp(mode, "edit");
    int insert = attr_bool(c, n, "insert", 0), del = attr_bool(c, n, "delete", 0);
    const char *href = attr_str(c, n, "href", NULL), *hrefkey = attr_str(c, n, "hrefkey", NULL);
    int appendkey = attr_bool(c, n, "appendkey", 1);
    GridCtx g; memset(&g, 0, sizeof g);
    g.rows = array_new();
    GridCtx *saved = t_grid;
    t_grid = &g;
    exec_nodes(c, n->kids, n->nkids, flow);
    t_grid = saved;
    Query *q = NULL;
    int present;
    Val qv = attr_val(c, n, "query", &present);
    if (present) {
        q = qv.t == VT_QUERY ? qv.u.q : NULL;
        if (!q) { Val t; if (resolve_path(c, v_tostr(qv), &t) && t.t == VT_QUERY) q = t.u.q; }
        if (!q) kf_throw(c, "Application", "Attribute validation error for tag CFGRID.", "QUERY must name a query.");
    } else {
        /* build a query from CFGRIDROW data */
        q = query_new(0, NULL);
        for (int i = 0; i < g.ncols; i++) query_add_column(q, g.cols[i].name);
        for (int r = 0; r < g.rows->n; r++) {
            Array *f = list_to_array_k(v_tostr(g.rows->v[r]), ",");
            int row = query_add_row(q);
            for (int i = 0; i < q->ncols && i < f->n; i++) query_set(q, i, row, f->v[i]);
        }
    }
    if (!g.ncols) for (int i = 0; i < q->ncols && i < 64; i++) {
        g.cols[g.ncols++] = (GridCol){ q->cols[i], q->cols[i], NULL, "left", NULL, NULL, 1, 1 };
    }
    const char *font = attr_str(c, n, "font", "Arial");
    Buf b; buf_init(&b);
    buf_printf(&b, "<!-- CFGRID %s (HTML rendition of the Java grid applet) -->\n", H(name));
    int rowsel = !kf_stricmp(mode, "single") || !kf_stricmp(mode, "row");
    int colsel = !kf_stricmp(mode, "column");
    if (rowsel) for (int i = 0; i < g.ncols; i++) buf_printf(&b, "<INPUT TYPE=hidden NAME=\"%s.%s\" VALUE=\"\">", H(name), H(g.cols[i].name));
    buf_printf(&b, "<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 BGCOLOR=\"#808080\"><TR><TD>\n"
                   "<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=1 WIDTH=\"%s\">\n<TR BGCOLOR=\"#C0C0C0\">",
               attr_str(c, n, "width", "100%"));
    if (rowsel) buf_puts(&b, "<TH></TH>");
    if (edit && del) buf_puts(&b, "<TH><FONT FACE=\"Arial\" SIZE=1>Del</FONT></TH>");
    for (int i = 0; i < g.ncols; i++) if (g.cols[i].display)
        buf_printf(&b, "<TH ALIGN=LEFT%s><FONT FACE=\"%s\" SIZE=1>%s%s</FONT></TH>",
                   g.cols[i].width ? kprintf(" WIDTH=%s", g.cols[i].width) : "", H(font),
                   colsel ? kprintf("<INPUT TYPE=radio NAME=\"%s.column\" VALUE=\"%s\">", H(name), H(g.cols[i].name)) : "",
                   H(g.cols[i].header));
    buf_puts(&b, "</TR>\n");
    for (int r = 0; r < q->nrows; r++) {
        buf_printf(&b, "<TR BGCOLOR=\"%s\">", r % 2 ? "#F0F0F0" : "#FFFFFF");
        if (rowsel) {
            Buf js; buf_init(&js);
            for (int i = 0; i < g.ncols; i++) {
                int ci = query_col_index(q, g.cols[i].name);
                buf_printf(&js, "this.form['%s.%s'].value='%s';", js_q(name), js_q(g.cols[i].name), js_q(ci >= 0 ? v_tostr(query_get(q, ci, r)) : ""));
            }
            buf_printf(&b, "<TD><INPUT TYPE=radio NAME=\"%s.rowselected\" VALUE=\"%d\" onClick=\"%s\"></TD>", H(name), r + 1, H(buf_cstr(&js)));
        }
        if (edit && del) buf_printf(&b, "<TD ALIGN=CENTER><INPUT TYPE=checkbox NAME=\"__CFGRID__%s__%d__DELETE\" VALUE=1></TD>", name, r + 1);
        for (int i = 0; i < g.ncols; i++) {
            int ci = query_col_index(q, g.cols[i].name);
            const char *v = ci >= 0 ? v_tostr(query_get(q, ci, r)) : "";
            if (edit) buf_printf(&b, "<INPUT TYPE=hidden NAME=\"__CFGRID__%s__%d__ORIG__%s\" VALUE=\"%s\">", name, r + 1, g.cols[i].name, H(v));
            if (!g.cols[i].display) continue;
            buf_printf(&b, "<TD ALIGN=%s><FONT FACE=\"%s\" SIZE=1>", g.cols[i].align, H(font));
            if (edit && g.cols[i].select)
                buf_printf(&b, "<INPUT TYPE=text NAME=\"__CFGRID__%s__%d__%s\" VALUE=\"%s\" SIZE=%d STYLE=\"font-size:8pt\">",
                           name, r + 1, g.cols[i].name, H(v), (int)strlen(v) + 2 > 30 ? 30 : (int)strlen(v) + 2);
            else {
                const char *h = g.cols[i].href ? g.cols[i].href : href;
                const char *hk = g.cols[i].hrefkey ? g.cols[i].hrefkey : hrefkey;
                if (h) {
                    const char *kv = v;
                    if (hk) { int ki = query_col_index(q, hk); if (ki >= 0) kv = v_tostr(query_get(q, ki, r)); }
                    const char *url = appendkey ? kprintf("%s%cCFGRIDKEY=%s", h, strchr(h, '?') ? '&' : '?', kf_urlencode(kv)) : h;
                    buf_printf(&b, "<A HREF=\"%s\">%s</A>", H(url), H(v));
                } else buf_puts(&b, H(v));
            }
            buf_puts(&b, "</FONT></TD>");
        }
        buf_puts(&b, "</TR>\n");
    }
    if (edit && insert) {
        buf_printf(&b, "<TR BGCOLOR=\"#FFFFCC\">%s", del ? "<TD><FONT FACE=\"Arial\" SIZE=1>New</FONT></TD>" : "");
        for (int i = 0; i < g.ncols; i++) if (g.cols[i].display)
            buf_printf(&b, "<TD><INPUT TYPE=text NAME=\"__CFGRID__%s__NEW__%s\" SIZE=10 STYLE=\"font-size:8pt\"></TD>", name, g.cols[i].name);
        buf_puts(&b, "</TR>\n");
    }
    buf_printf(&b, "</TABLE></TD></TR></TABLE>\n<INPUT TYPE=hidden NAME=\"__CFGRID__%s__ROWS\" VALUE=\"%d\">\n", name, q->nrows);
    out_puts(c, buf_cstr(&b));
}

TAG(gridupdate) {
    (void)flow;
    RState *rs = c->rs;
    const char *grid = require_attr(c, n, "grid");
    const char *dsn = require_attr(c, n, "datasource");
    const char *table = require_attr(c, n, "tablename");
    int keyonly = attr_bool(c, n, "keyonly", 1);
    Dsn d;
    if (!dsn_lookup(dsn, &d)) kf_throw(c, "Database", kprintf("Data source %s could not be found.", kf_upper(dsn)), "");
    Query *cols; char err[1024];
    if (!sql_describe(d.path, table, &cols, err, sizeof err)) kf_throw(c, "Database", err, "");
    int pkcol = query_col_index(cols, "IS_PRIMARY_KEY");
    Val *rowsv = struct_get(rs->form, kprintf("__CFGRID__%s__ROWS", grid));
    int rows = rowsv ? atoi(v_tostr(*rowsv)) : 0;
    const char *prefix = kprintf("__CFGRID__%s__", grid);
    Buf sqls; buf_init(&sqls);
#define LIT(b, v) do { buf_putc(b, '\''); for (const char *_p = (v); *_p; _p++) { if (*_p == '\'') buf_putc(b, '\''); buf_putc(b, *_p); } buf_putc(b, '\''); } while (0)
    for (int r = 1; r <= rows; r++) {
        Buf where; buf_init(&where);
        int nkeys = 0;
        for (int k = 0; k < cols->nrows; k++) {
            const char *cn = v_tostr(query_get(cols, 0, k));
            int ispk = pkcol >= 0 ? atoi(v_tostr(query_get(cols, pkcol, k))) || !kf_stricmp(v_tostr(query_get(cols, pkcol, k)), "yes") : k == 0;
            Val *ov = struct_get(rs->form, kprintf("%s%d__ORIG__%s", prefix, r, cn));
            if (!ov || (!ispk && keyonly)) continue;
            if (nkeys++) buf_puts(&where, " AND ");
            buf_printf(&where, "%s = ", cn); LIT(&where, v_tostr(*ov));
        }
        if (!nkeys) continue;
        if (struct_get(rs->form, kprintf("%s%d__DELETE", prefix, r))) {
            buf_printf(&sqls, "DELETE FROM %s WHERE %s;\n", table, buf_cstr(&where));
            continue;
        }
        Buf set; buf_init(&set);
        int changed = 0;
        for (int k = 0; k < cols->nrows; k++) {
            const char *cn = v_tostr(query_get(cols, 0, k));
            Val *nv = struct_get(rs->form, kprintf("%s%d__%s", prefix, r, cn));
            Val *ov = struct_get(rs->form, kprintf("%s%d__ORIG__%s", prefix, r, cn));
            if (!nv || !ov || !strcmp(v_tostr(*nv), v_tostr(*ov))) continue;
            if (changed++) buf_puts(&set, ", ");
            buf_printf(&set, "%s = ", cn); LIT(&set, v_tostr(*nv));
        }
        if (changed) buf_printf(&sqls, "UPDATE %s SET %s WHERE %s;\n", table, buf_cstr(&set), buf_cstr(&where));
    }
    Buf names, vals; buf_init(&names); buf_init(&vals);
    int ni = 0;
    for (int k = 0; k < cols->nrows; k++) {
        const char *cn = v_tostr(query_get(cols, 0, k));
        Val *nv = struct_get(rs->form, kprintf("%sNEW__%s", prefix, cn));
        if (!nv || !*v_tostr(*nv)) continue;
        if (ni++) { buf_puts(&names, ", "); buf_puts(&vals, ", "); }
        buf_puts(&names, cn); LIT(&vals, v_tostr(*nv));
    }
    if (ni) buf_printf(&sqls, "INSERT INTO %s (%s) VALUES (%s);\n", table, buf_cstr(&names), buf_cstr(&vals));
#undef LIT
    if (sqls.len && !sql_exec_script(d.path, buf_cstr(&sqls), err, sizeof err))
        kf_throw(c, "Database", err, "");
}

/* ================================================================ CFTREE */
typedef struct TreeItem { const char *value, *display, *parent, *img, *href; int expand; } TreeItem;
typedef struct TreeCtx { TreeItem *items; int n, cap; } TreeCtx;
static __thread TreeCtx *t_tree;

static void tree_add(TreeItem it) {
    if (t_tree->n == t_tree->cap) {
        int nc = t_tree->cap ? t_tree->cap * 2 : 32;
        TreeItem *ni = kmalloc(sizeof(TreeItem) * nc);
        if (t_tree->n) memcpy(ni, t_tree->items, sizeof(TreeItem) * t_tree->n);
        t_tree->items = ni; t_tree->cap = nc;
    }
    t_tree->items[t_tree->n++] = it;
}

TAG(treeitem) {
    (void)flow;
    if (!t_tree) kf_throw(c, "Template", "Context validation error for tag CFTREEITEM.", "The tag must be nested inside a CFTREE tag.");
    const char *value = require_attr(c, n, "value");
    int present;
    Val qv = attr_val(c, n, "query", &present);
    if (present) {
        Query *q = qv.t == VT_QUERY ? qv.u.q : NULL;
        if (!q) { Val t; if (resolve_path(c, v_tostr(qv), &t) && t.t == VT_QUERY) q = t.u.q; }
        if (!q) kf_throw(c, "Application", "Attribute validation error for tag CFTREEITEM.", "QUERY must name a query.");
        /* VALUE/DISPLAY are comma lists of columns: one tree level per column */
        Array *vcols = list_to_array_k(value, ",");
        Array *dcols = list_to_array_k(attr_str(c, n, "display", value), ",");
        for (int r = 0; r < q->nrows; r++) {
            const char *parent = attr_str(c, n, "parent", "");
            for (int lv = 0; lv < vcols->n; lv++) {
                int vi = query_col_index(q, kf_trim(v_tostr(vcols->v[lv])));
                int di = lv < dcols->n ? query_col_index(q, kf_trim(v_tostr(dcols->v[lv]))) : vi;
                if (vi < 0) continue;
                const char *v = kprintf("%s/%s", parent, v_tostr(query_get(q, vi, r)));
                int exists = 0;
                for (int i = 0; i < t_tree->n; i++) if (!strcmp(t_tree->items[i].value, v)) exists = 1;
                Array *imgs = list_to_array_k(attr_str(c, n, "img", ""), ",");
                const char *img = lv < imgs->n ? v_tostr(imgs->v[lv]) : (lv == vcols->n - 1 ? "document" : "folder");
                if (!exists) tree_add((TreeItem){ v, v_tostr(query_get(q, di >= 0 ? di : vi, r)), parent,
                                                  img, attr_str(c, n, "href", NULL), attr_bool(c, n, "expand", 0) });
                parent = v;
            }
        }
        return;
    }
    tree_add((TreeItem){ value, attr_str(c, n, "display", value), attr_str(c, n, "parent", ""),
                         attr_str(c, n, "img", NULL), attr_str(c, n, "href", NULL), attr_bool(c, n, "expand", 1) });
}

static const char *tree_path(TreeCtx *t, TreeItem *it) {
    /* PATH: the item's value preceded by its ancestors' values, joined with \ */
    const char *path = it->value;
    const char *parent = it->parent ? it->parent : "";
    for (int guard = 0; *parent && guard < 64; guard++) {
        TreeItem *p = NULL;
        for (int i = 0; i < t->n; i++) if (!strcmp(t->items[i].value, parent)) p = &t->items[i];
        if (!p) break;
        path = kprintf("%s\\%s", p->value, path);
        parent = p->parent ? p->parent : "";
    }
    return path;
}

static void tree_render(Buf *b, TreeCtx *t, const char *parent, const char *name, int depth, int *uid) {
    int any = 0;
    for (int i = 0; i < t->n; i++) if (!strcmp(t->items[i].parent ? t->items[i].parent : "", parent)) any = 1;
    if (!any) return;
    for (int i = 0; i < t->n; i++) {
        TreeItem *it = &t->items[i];
        if (strcmp(it->parent ? it->parent : "", parent)) continue;
        int kids = 0;
        for (int j = 0; j < t->n; j++) if (!strcmp(t->items[j].parent ? t->items[j].parent : "", it->value)) kids = 1;
        int id = (*uid)++;
        const char *img = it->img ? it->img : (kids ? "folder" : "document");
        const char *gif = !kf_stricmp(img, "document") || !kf_stricmp(img, "computer") ? "/CFIDE/administrator/images/file.gif"
                        : !kf_stricmp(img, "folder") || !kf_stricmp(img, "cd") || !kf_stricmp(img, "floppy") || !kf_stricmp(img, "fixed")
                          || !kf_stricmp(img, "remote") ? "/CFIDE/administrator/images/folder.gif" : img;
        buf_printf(b, "<DIV STYLE=\"margin-left:%dpx\"><NOBR>", depth ? 16 : 0);
        if (kids) buf_printf(b, "<A HREF=\"javascript:_CF_treeToggle('%s_%d')\" STYLE=\"text-decoration:none\"><TT ID=\"%s_%d_m\">[%s]</TT></A>", name, id, name, id, it->expand ? "-" : "+");
        else buf_puts(b, "<TT>&nbsp;&nbsp;&nbsp;</TT>");
        buf_printf(b, "<IMG SRC=\"%s\" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE> ", gif);
        if (it->href) buf_printf(b, "<A HREF=\"%s%cCFTREEITEMKEY=%s\">%s</A>", H(it->href), strchr(it->href, '?') ? '&' : '?', kf_urlencode(it->value), H(it->display));
        else buf_printf(b, "<A HREF=\"javascript:_CF_treeSelect('%s','%s','%s')\" STYLE=\"color:black;text-decoration:none\">%s</A>", name, js_q(it->value), js_q(tree_path(t, it)), H(it->display));
        buf_puts(b, "</NOBR>");
        if (kids) {
            buf_printf(b, "<DIV ID=\"%s_%d\" STYLE=\"display:%s\">", name, id, it->expand ? "block" : "none");
            tree_render(b, t, it->value, name, depth + 1, uid);
            buf_puts(b, "</DIV>");
        }
        buf_puts(b, "</DIV>\n");
    }
}

TAG(tree) {
    require_form(c, n);
    const char *name = require_attr(c, n, "name");
    TreeCtx t; memset(&t, 0, sizeof t);
    TreeCtx *saved = t_tree;
    t_tree = &t;
    exec_nodes(c, n->kids, n->nkids, flow);
    t_tree = saved;
    Buf b; buf_init(&b);
    buf_printf(&b, "<!-- CFTREE %s (HTML rendition of the Java tree applet) -->\n", H(name));
    buf_printf(&b, "<TABLE BORDER=1 CELLPADDING=4 CELLSPACING=0 BGCOLOR=\"#FFFFFF\" WIDTH=\"%s\"><TR><TD>"
                   "<FONT FACE=\"%s\" SIZE=2>\n", attr_str(c, n, "width", "250"), attr_str(c, n, "font", "Arial"));
    int uid = 1;
    tree_render(&b, &t, "", name, 0, &uid);
    buf_printf(&b, "</FONT></TD></TR></TABLE>\n<INPUT TYPE=hidden NAME=\"%s.node\" VALUE=\"\"><INPUT TYPE=hidden NAME=\"%s.path\" VALUE=\"\">\n", H(name), H(name));
    out_puts(c, buf_cstr(&b));
    if (attr_bool(c, n, "required", 0))
        add_check(c, kprintf("%s.node", name), kprintf("_CF_this[\"%s.node\"].value == \"\"", name),
                  attr_str(c, n, "message", "Please select an item in the tree."));
}

/* ================================================================ CFAPPLET */
TAG(applet) {
    (void)flow;
    require_form(c, n);
    const char *src = require_attr(c, n, "appletsource");
    const char *name = require_attr(c, n, "name");
    char *k = cfg_key(kprintf("Applets\\%s", src));
    if (!reg_exists(k, NULL))
        kf_throw(c, "Application", kprintf("The applet %s is not registered.", H(src)),
                 "Applets must be registered on the Applets page of the KoldFusion Administrator before CFAPPLET can use them.");
    Buf b; buf_init(&b);
    buf_printf(&b, "<APPLET CODE=\"%s\" CODEBASE=\"%s\" NAME=\"%s\" WIDTH=%s HEIGHT=%s VSPACE=%s HSPACE=%s ALIGN=%s>\n",
               H(reg_get(k, "Code", "")), H(reg_get(k, "Codebase", "")), H(name),
               attr_str(c, n, "width", reg_get(k, "Width", "200")), attr_str(c, n, "height", reg_get(k, "Height", "100")),
               attr_str(c, n, "vspace", reg_get(k, "VSpace", "0")), attr_str(c, n, "hspace", reg_get(k, "HSpace", "0")),
               attr_str(c, n, "align", reg_get(k, "Align", "LEFT")));
    Query *params = reg_list(kprintf("%s\\Params", k), 0, 1);
    for (int r = 0; r < params->nrows; r++) {
        const char *pn = v_tostr(query_get(params, 0, r));
        buf_printf(&b, "<PARAM NAME=\"%s\" VALUE=\"%s\">\n", H(pn), H(attr_str(c, n, kf_lower(pn), v_tostr(query_get(params, 2, r)))));
    }
    buf_printf(&b, "%s\n</APPLET>", attr_str(c, n, "notsupported", reg_get(k, "NotSupported", "<B>Browser must support Java to view this applet.</B>")));
    out_puts(c, buf_cstr(&b));
}

/* ================================================================ CFTABLE */
typedef struct TCol { const char *header; int width; const char *align; Node *text; } TCol;
typedef struct TblCtx { TCol cols[64]; int n; } TblCtx;
static __thread TblCtx *t_table;

TAG(col) {
    (void)flow;
    if (!t_table) kf_throw(c, "Template", "Context validation error for tag CFCOL.", "The tag must be nested inside a CFTABLE tag.");
    if (t_table->n >= 64) return;
    TCol *tc = &t_table->cols[t_table->n++];
    tc->header = attr_str(c, n, "header", "");
    tc->width = (int)attr_num(c, n, "width", 20);
    tc->align = attr_str(c, n, "align", "left");
    tc->text = n;
}

static const char *col_text(Ctx *c, Node *n) {
    /* re-evaluate TEXT for the current row, honouring #...# */
    for (int i = 0; i < n->nattrs; i++)
        if (!strcmp(n->attrs[i].name, "text")) return val_simple_str(c, eval(c, n->attrs[i].val), NULL);
    return "";
}

TAG(table) {
    int present;
    Val qv = attr_val(c, n, "query", &present);
    Query *q = qv.t == VT_QUERY ? qv.u.q : NULL;
    if (!q) { Val t; if (present && resolve_path(c, v_tostr(qv), &t) && t.t == VT_QUERY) q = t.u.q; }
    if (!q) kf_throw(c, "Application", "Attribute validation error for tag CFTABLE.", "QUERY must name a query.");
    TblCtx tc; memset(&tc, 0, sizeof tc);
    TblCtx *saved = t_table;
    t_table = &tc;
    /* collect columns without producing output */
    Buf sink; buf_init(&sink);
    Buf *sout = c->rs->out;
    c->rs->out = &sink;
    exec_nodes(c, n->kids, n->nkids, flow);
    c->rs->out = sout;
    t_table = saved;
    int html = attr_bool(c, n, "htmltable", 0), border = has_attr(n, "border"), colheaders = attr_bool(c, n, "colheaders", 0);
    int spacing = (int)attr_num(c, n, "colspacing", 2);
    int start = (int)attr_num(c, n, "startrow", 1) - 1, maxrows = (int)attr_num(c, n, "maxrows", -1);
    int end = q->nrows;
    if (start < 0) start = 0;
    if (maxrows >= 0 && start + maxrows < end) end = start + maxrows;
    Buf b; buf_init(&b);
    QLoop ql = { q, c->qloop };
    c->qloop = &ql;
    int saved_row = q->currentrow, saved_out = c->in_output;
    c->in_output = 1;
    if (html) {
        buf_printf(&b, "<TABLE%s>\n", border ? " BORDER" : "");
        if (colheaders) {
            buf_puts(&b, "<TR>");
            for (int i = 0; i < tc.n; i++) buf_printf(&b, "<TH ALIGN=%s WIDTH=%d>%s</TH>", tc.cols[i].align, tc.cols[i].width * 8, tc.cols[i].header);
            buf_puts(&b, "</TR>\n");
        }
        for (int r = start; r < end; r++) {
            q->currentrow = r + 1;
            buf_puts(&b, "<TR>");
            for (int i = 0; i < tc.n; i++) buf_printf(&b, "<TD ALIGN=%s>%s</TD>", tc.cols[i].align, col_text(c, tc.cols[i].text));
            buf_puts(&b, "</TR>\n");
        }
        buf_puts(&b, "</TABLE>\n");
    } else {
        buf_puts(&b, "<PRE>");
        if (colheaders) {
            for (int i = 0; i < tc.n; i++) buf_printf(&b, "%-*.*s%*s", tc.cols[i].width, tc.cols[i].width, tc.cols[i].header, spacing, "");
            buf_puts(&b, "\n");
            for (int h = 1; h < (int)attr_num(c, n, "headerlines", 2); h++) buf_puts(&b, "\n");
        }
        for (int r = start; r < end; r++) {
            q->currentrow = r + 1;
            for (int i = 0; i < tc.n; i++) {
                const char *t = col_text(c, tc.cols[i].text);
                int w = tc.cols[i].width;
                if (!kf_stricmp(tc.cols[i].align, "right")) buf_printf(&b, "%*.*s%*s", w, w, t, spacing, "");
                else if (!kf_stricmp(tc.cols[i].align, "center")) {
                    int l = (int)strlen(t); if (l > w) l = w;
                    int pad = (w - l) / 2;
                    buf_printf(&b, "%*s%.*s%*s%*s", pad, "", l, t, w - l - pad, "", spacing, "");
                } else buf_printf(&b, "%-*.*s%*s", w, w, t, spacing, "");
            }
            buf_puts(&b, "\n");
        }
        buf_puts(&b, "</PRE>\n");
    }
    c->in_output = saved_out;
    q->currentrow = saved_row;
    c->qloop = ql.prev;
    out_puts(c, buf_cstr(&b));
}
