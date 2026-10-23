/*
 * tags.c - core CFML tags: flow control, output, variables, includes,
 * custom tags, exceptions, application framework, HTTP response control.
 */
#define _GNU_SOURCE
#include "engine.h"
#include <stdlib.h>
#include <ctype.h>
#include <math.h>
#include <unistd.h>
#include <dirent.h>
#include <sys/stat.h>
#include <time.h>

#define TAG(nm) static void tag_##nm(Ctx *c, Node *n, int *flow)
#define UNUSED (void)c; (void)n; (void)flow

/* tags implemented in other files */
#define EXT(nm) void tag_##nm(Ctx *c, Node *n, int *flow);
EXT(query) EXT(queryparam) EXT(transaction) EXT(insert) EXT(update) EXT(storedproc)
EXT(mail) EXT(mailparam) EXT(file) EXT(directory) EXT(registry) EXT(http) EXT(httpparam)
EXT(schedule) EXT(execute) EXT(wddx) EXT(pop) EXT(ftp) EXT(ldap) EXT(object) EXT(servlet)
EXT(report) EXT(index) EXT(search) EXT(collection) EXT(authenticate) EXT(impersonate)
EXT(form) EXT(input) EXT(select) EXT(textinput) EXT(slider) EXT(grid) EXT(gridcolumn)
EXT(gridrow) EXT(gridupdate) EXT(tree) EXT(treeitem) EXT(applet) EXT(table) EXT(col)
EXT(adminsecurity) EXT(procparam) EXT(procresult) EXT(servletparam) EXT(objectcache)

/* ================================================================ helpers */
static void exec_body(Ctx *c, Node *n, int *flow) { exec_nodes(c, n->kids, n->nkids, flow); }

static void throw_abort(Ctx *c) {
    KfError *e = kf_error_new("__abort", "", "");
    kf_throw_err(c->rs, e);
}

/* ================================================================ CFSET */
TAG(set) {
    UNUSED;
    if (!n->expr) return;
    if (n->expr->k != E_ASSIGN) {
        /* <cfset foo()> evaluates for side effects */
        eval(c, n->expr);
        return;
    }
    eval(c, n->expr);
}

/* ================================================================ CFOUTPUT */
static int group_key_equal(Query *q, const char **cols, int ncols, int r1, int r2, int casesens) {
    for (int i = 0; i < ncols; i++) {
        int ci = query_col_index(q, cols[i]);
        if (ci < 0) continue;
        const char *a = v_tostr(query_get(q, ci, r1)), *b = v_tostr(query_get(q, ci, r2));
        if (casesens ? strcmp(a, b) : kf_stricmp(a, b)) return 0;
    }
    return 1;
}

static void loop_rows(Ctx *c, Node *n, Query *q, int start, int end, const char *group, int casesens, int *flow) {
    /* iterate rows [start,end) of q; with a GROUP attribute, iterate groups */
    QLoop ql = { q, c->qloop };
    c->qloop = &ql;
    int saved_row = q->currentrow;
    Query *sg_q = c->grp_q; int sg_s = c->grp_start, sg_e = c->grp_end, sg_a = c->grp_active;
    const char **gcols = NULL; int ngcols = 0;
    if (group && *group) {
        Array *a = list_to_array_k(group, ",");
        ngcols = a->n;
        gcols = kmalloc(sizeof(char *) * (ngcols ? ngcols : 1));
        for (int i = 0; i < a->n; i++) {
            gcols[i] = kf_trim(v_tostr(a->v[i]));
            if (query_col_index(q, gcols[i]) < 0)
                kf_throw(c, "Application", kprintf("Attribute validation error for tag %s.", kf_upper(n->tag)),
                         kprintf("The value of the attribute GROUP, which is currently \"%s\", is not a column of the query.",
                                 kf_html_escape(gcols[i])));
        }
    }
    int r = start;
    while (r < end) {
        check_timeout(c);
        int gend = r + 1;
        if (ngcols) while (gend < end && group_key_equal(q, gcols, ngcols, r, gend, casesens)) gend++;
        q->currentrow = r + 1;
        c->grp_q = q; c->grp_start = r; c->grp_end = gend; c->grp_active = ngcols > 0;
        exec_body(c, n, flow);
        if (*flow == FL_BREAK) { *flow = FL_OK; break; }
        if (*flow == FL_CONTINUE) *flow = FL_OK;
        if (*flow) break;
        r = gend;
    }
    q->currentrow = saved_row;
    c->qloop = ql.prev;
    c->grp_q = sg_q; c->grp_start = sg_s; c->grp_end = sg_e; c->grp_active = sg_a;
}

static Query *query_attr(Ctx *c, Node *n, const char *attr) {
    int present;
    Val v = attr_val(c, n, attr, &present);
    if (!present) return NULL;
    if (v.t == VT_QUERY) return v.u.q;
    const char *name = v_tostr(v);
    Val qv;
    if (!resolve_path(c, name, &qv) || qv.t != VT_QUERY)
        kf_throw(c, "Application", kprintf("Attribute validation error for tag %s.", kf_upper(n->tag)),
                 kprintf("The value of the attribute %s, which is currently \"%s\", is invalid. "
                         "The query %s is not defined or is not a query.", kf_upper(attr), kf_html_escape(name), kf_upper(name)));
    return qv.u.q;
}

TAG(output) {
    int saved = c->in_output;
    Query *q = query_attr(c, n, "query");
    if (q) {
        if (c->in_output && c->qloop)
            kf_throw(c, "Template", "Invalid tag nesting configuration.",
                "A query driven CFOUTPUT tag is nested inside a CFOUTPUT tag that also has a QUERY= attribute. This is not allowed. "
                "Nesting these tags implies that you want to use grouped processing. However, only the top-level tag can specify "
                "the query that drives the processing.");
        int start = (int)attr_num(c, n, "startrow", 1) - 1;
        int maxrows = (int)attr_num(c, n, "maxrows", -1);
        if (start < 0) start = 0;
        int end = q->nrows;
        if (maxrows >= 0 && start + maxrows < end) end = start + maxrows;
        c->in_output = 1;
        loop_rows(c, n, q, start, end, attr_str(c, n, "group", NULL), attr_bool(c, n, "groupcasesensitive", 1), flow);
        c->in_output = saved;
        return;
    }
    if (c->grp_active && c->grp_q) {
        /* inner CFOUTPUT of a grouped output: iterate rows of the current group */
        Query *gq = c->grp_q;
        int s = c->grp_start, e = c->grp_end;
        c->in_output = 1;
        c->grp_active = 0;
        loop_rows(c, n, gq, s, e, attr_str(c, n, "group", NULL), attr_bool(c, n, "groupcasesensitive", 1), flow);
        c->grp_active = 1;
        c->in_output = saved;
        return;
    }
    c->in_output = 1;
    exec_body(c, n, flow);
    c->in_output = saved;
}

/* ================================================================ CFIF */
TAG(if) {
    UNUSED;
    /* split children at CFELSEIF / CFELSE */
    int take = val_truth(c, eval(c, n->expr), n->expr);
    int start = 0;
    for (int i = 0; i <= n->nkids; i++) {
        Node *k = i < n->nkids ? n->kids[i] : NULL;
        int is_branch = k && k->k == N_TAG && (!strcmp(k->tag, "cfelseif") || !strcmp(k->tag, "cfelse"));
        if (k && !is_branch) continue;
        if (take) {
            exec_nodes(c, n->kids + start, i - start, flow);
            return;
        }
        if (!k) return;
        c->rs->cur_node = k;
        if (!strcmp(k->tag, "cfelse")) take = 1;
        else take = val_truth(c, eval(c, k->expr), k->expr);
        c->rs->cur_node = n;
        start = i + 1;
    }
}

/* ================================================================ CFLOOP */
TAG(loop) {
    RState *rs = c->rs;
    (void)rs;
    if (has_attr(n, "query")) {
        Query *q = query_attr(c, n, "query");
        int start = (int)attr_num(c, n, "startrow", 1) - 1;
        int end = (int)attr_num(c, n, "endrow", q->nrows);
        if (start < 0) start = 0;
        if (end > q->nrows) end = q->nrows;
        Query *sg = c->grp_q; int sa = c->grp_active;
        c->grp_active = 0;
        loop_rows(c, n, q, start, end, NULL, 1, flow);
        c->grp_q = sg; c->grp_active = sa;
        if (*flow == FL_EXIT_LOOP) *flow = FL_OK;
        return;
    }
    if (has_attr(n, "condition")) {
        /* condition is re-evaluated each pass from the raw attribute text */
        const char *cond = NULL;
        for (int i = 0; i < n->nattrs; i++) if (!strcmp(n->attrs[i].name, "condition")) cond = n->attrs[i].raw;
        const char *err;
        Expr *e = expr_parse_string(cond, &err);
        if (!e) kf_throw(c, "Expression", "Invalid CONDITION expression in CFLOOP.", err);
        while (val_truth(c, eval(c, e), e)) {
            check_timeout(c);
            exec_body(c, n, flow);
            if (*flow == FL_BREAK) { *flow = FL_OK; break; }
            if (*flow == FL_CONTINUE) { *flow = FL_OK; continue; }
            if (*flow) return;
        }
        return;
    }
    if (has_attr(n, "collection")) {
        Val coll = attr_val(c, n, "collection", NULL);
        const char *item = require_attr(c, n, "item");
        if (coll.t != VT_STRUCT)
            kf_throw(c, "Application", "Attribute validation error for tag CFLOOP.",
                     "The value of the attribute COLLECTION must be a structure.");
        Struct *s = coll.u.st;
        int cnt = s->n;
        const char **keys = kmalloc(sizeof(char *) * (cnt ? cnt : 1));
        for (int i = 0; i < cnt; i++) keys[i] = s->e[i].key;
        for (int i = 0; i < cnt; i++) {
            check_timeout(c);
            assign_path(c, item, v_str(keys[i]));
            exec_body(c, n, flow);
            if (*flow == FL_BREAK) { *flow = FL_OK; break; }
            if (*flow == FL_CONTINUE) { *flow = FL_OK; continue; }
            if (*flow) return;
        }
        return;
    }
    if (has_attr(n, "list")) {
        const char *list = attr_str(c, n, "list", "");
        const char *delims = attr_str(c, n, "delimiters", ",");
        const char *idx = require_attr(c, n, "index");
        Array *a = list_to_array_k(list, delims);
        for (int i = 0; i < a->n; i++) {
            check_timeout(c);
            assign_path(c, idx, a->v[i]);
            exec_body(c, n, flow);
            if (*flow == FL_BREAK) { *flow = FL_OK; break; }
            if (*flow == FL_CONTINUE) { *flow = FL_OK; continue; }
            if (*flow) return;
        }
        return;
    }
    if (has_attr(n, "index")) {
        const char *idx = require_attr(c, n, "index");
        if (!has_attr(n, "from") || !has_attr(n, "to"))
            kf_throw(c, "Application", "Attribute validation error for tag CFLOOP.",
                     "An index loop requires the attributes FROM and TO.");
        double from = attr_num(c, n, "from", 1), to = attr_num(c, n, "to", 1), step = attr_num(c, n, "step", 1);
        if (step == 0) kf_throw(c, "Application", "Attribute validation error for tag CFLOOP.", "STEP may not be 0.");
        for (double i = from; step > 0 ? i <= to : i >= to; i += step) {
            check_timeout(c);
            assign_path(c, idx, v_num(i));
            exec_body(c, n, flow);
            if (*flow == FL_BREAK) { *flow = FL_OK; break; }
            if (*flow == FL_CONTINUE) { *flow = FL_OK; }
            if (*flow) return;
            /* the body may change the index; CF re-reads it */
            Val cur;
            if (resolve_path(c, idx, &cur)) { double d; if (v_tonum(cur, &d)) i = d; }
        }
        return;
    }
    kf_throw(c, "Application", "Attribute validation error for tag CFLOOP.",
             "The tag requires one of the attribute sets: INDEX/FROM/TO, CONDITION, QUERY, LIST/INDEX, COLLECTION/ITEM.");
}

TAG(break) { UNUSED; *flow = FL_BREAK; }

TAG(abort) {
    (void)flow;
    const char *msg = attr_str(c, n, "showerror", NULL);
    if (msg) {
        KfError *e = kf_error_new("Application", msg, "");
        e->errorcode = "abort";
        kf_throw_err(c->rs, e);
    }
    throw_abort(c);
}

TAG(exit) {
    const char *m = attr_str(c, n, "method", "exittag");
    if (!c->thistag) { throw_abort(c); }
    if (!kf_stricmp(m, "exittemplate")) *flow = FL_EXIT_TEMPLATE;
    else if (!kf_stricmp(m, "loop")) *flow = FL_EXIT_LOOP;
    else *flow = FL_EXIT_TAG;
}

/* ================================================================ CFPARAM */
static int is_valid_varname(const char *s) {
    if (!kf_is_ident_start((unsigned char)*s)) return 0;
    for (; *s; s++) if (!kf_is_ident_char((unsigned char)*s) && *s != '.') return 0;
    return 1;
}

static int check_type(Val v, const char *type) {
    double d; int b;
    if (!kf_stricmp(type, "any")) return 1;
    if (!kf_stricmp(type, "array")) return v.t == VT_ARRAY;
    if (!kf_stricmp(type, "struct")) return v.t == VT_STRUCT;
    if (!kf_stricmp(type, "query")) return v.t == VT_QUERY;
    if (!kf_stricmp(type, "binary")) return v.t == VT_BINARY;
    if (!v_is_simple(v)) return 0;
    if (!kf_stricmp(type, "string")) return 1;
    if (!kf_stricmp(type, "numeric")) return v_tonum(v, &d) && (v.t != VT_STR || v_isnumeric_str(v.u.str.s, NULL));
    if (!kf_stricmp(type, "boolean")) return v_tobool(v, &b);
    if (!kf_stricmp(type, "date")) return v_todate(v, &d);
    if (!kf_stricmp(type, "variablename")) return is_valid_varname(v_tostr(v));
    if (!kf_stricmp(type, "uuid")) {
        const char *s = v_tostr(v);
        if (strlen(s) != 35) return 0;
        for (int i = 0; i < 35; i++) {
            if (i == 8 || i == 13 || i == 18) { if (s[i] != '-') return 0; }
            else if (!isxdigit((unsigned char)s[i])) return 0;
        }
        return 1;
    }
    return 1;
}

TAG(param) {
    (void)flow;
    const char *name = require_attr(c, n, "name");
    int has_def;
    Val def = attr_val(c, n, "default", &has_def);
    Val cur;
    if (!resolve_path(c, name, &cur)) {
        if (!has_def)
            kf_throw(c, "Application", kprintf("Parameter validation error for tag CFPARAM."),
                     kprintf("The required parameter '%s' was not provided. This page uses the CFPARAM tag to declare the "
                             "parameter '%s' as required for this template. The parameter is not available.",
                             kf_upper(name), kf_upper(name)));
        assign_path(c, name, def);
        cur = def;
    }
    const char *type = attr_str(c, n, "type", NULL);
    if (type && !check_type(cur, type))
        kf_throw(c, "Application", "Invalid parameter type.",
                 kprintf("The value specified, \"%s\", must be a valid %s.",
                         v_is_simple(cur) ? kf_html_escape(v_tostr(cur)) : v_typename(cur), type));
}

/* ================================================================ CFINCLUDE */
TAG(include) {
    (void)flow;
    const char *tpl = require_attr(c, n, "template");
    const char *path = resolve_template_path(c, tpl, 0);
    KfError *err;
    Template *t = template_get(c->rs, path, &err);
    if (!t) {
        if (err) kf_throw_err(c->rs, err);
        KfError *e = kf_error_new("MissingInclude", "Error processing CFINCLUDE",
            kprintf("Could not find the included template %s. Note: If you wish to use an absolute template path "
                    "(e.g. TEMPLATE=\"/mypath/index.cfm\") with CFINCLUDE then you must create a mapping for the path "
                    "using the KoldFusion Administrator.", kf_html_escape(tpl)));
        e->extended = kstrdup(tpl);
        kf_throw_err(c->rs, e);
    }
    exec_template(c, t);
}

/* ================================================================ custom tags */
static const char *find_in_dir_recursive(const char *dir, const char *file, int depth) {
    if (depth > 8) return NULL;
    char *p = kf_path_join(dir, file);
    if (access(p, R_OK) == 0) return p;
    DIR *d = opendir(dir);
    if (!d) return NULL;
    struct dirent *de;
    const char *found = NULL;
    /* case-insensitive match in this directory first */
    while ((de = readdir(d))) {
        if (!kf_stricmp(de->d_name, file)) { found = kf_path_join(dir, de->d_name); break; }
    }
    if (!found) {
        rewinddir(d);
        while ((de = readdir(d)) && !found) {
            if (de->d_name[0] == '.') continue;
            char *sub = kf_path_join(dir, de->d_name);
            struct stat st;
            if (stat(sub, &st) == 0 && S_ISDIR(st.st_mode)) found = find_in_dir_recursive(sub, file, depth + 1);
        }
    }
    closedir(d);
    return found;
}

static const char *find_custom_tag(Ctx *c, const char *tagname) {
    const char *file = kprintf("%s.cfm", tagname);
    char *p = kf_resolve_ci(kf_path_join(c->tagdir, file));
    if (p) return p;
    return find_in_dir_recursive(kf_path_join(G.root, "customtags"), file, 0);
}

static void run_custom_mode(Ctx *tc, Template *t, const char *mode, int *flow) {
    struct_set(tc->thistag, "ExecutionMode", v_str(mode));
    RState *rs = tc->rs;
    Template *saved_tpl = rs->cur_tpl;
    rs->cur_tpl = t;
    tc->tpl = t;
    tc->tagdir = kf_template_dir(t->path);
    if (++rs->depth > 64) kf_throw(tc, "Template", "Maximum custom tag nesting depth exceeded.", "Check for runaway recursion.");
    exec_nodes(tc, t->root->kids, t->root->nkids, flow);
    rs->depth--;
    rs->cur_tpl = saved_tpl;
}

void call_custom_tag(Ctx *c, Node *n, const char *path, Struct *attrs, int *flow) {
    RState *rs = c->rs;
    *flow = FL_OK;
    const char *tagname = NULL;
    if (!path) {
        tagname = n->tag + 3;
        path = find_custom_tag(c, tagname);
        if (!path)
            kf_throw(c, "Template", kprintf("Cannot find CFML template for custom tag %s.", kf_upper(n->tag)),
                     kprintf("KoldFusion attempted looking in the tree of installed custom tags but did not find a custom "
                             "tag with this name. Custom tags may be placed in the directory of the calling template or "
                             "in %s/customtags.", G.root));
    }
    tag_security_check(c, "cfmodule") ;
    KfError *err;
    Template *t = template_get(rs, path, &err);
    if (!t) {
        if (err) kf_throw_err(rs, err);
        kf_throw(c, "MissingInclude", "Error processing custom tag", kprintf("Could not open the custom tag template %s.", path));
    }
    if (!attrs) {
        attrs = struct_new();
        for (int i = 0; i < n->nattrs; i++) {
            if (!strcmp(n->attrs[i].name, "attributecollection")) {
                Val v = eval(c, n->attrs[i].val);
                if (v.t == VT_STRUCT) for (int j = 0; j < v.u.st->n; j++) struct_set(attrs, v.u.st->e[j].key, v.u.st->e[j].v);
                continue;
            }
            struct_set(attrs, n->attrs[i].name, eval(c, n->attrs[i].val));
        }
    }
    Ctx *tc = ctx_new(rs, t);
    tc->attributes = attrs;
    tc->caller = c->variables;
    tc->thistag = struct_new();
    tc->parent = c;
    int has_end = n->has_end || n->selfclose;
    struct_set(tc->thistag, "HasEndTag", v_bool(has_end));
    struct_set(tc->thistag, "GeneratedContent", v_str(""));
    struct_set(tc->thistag, "AssocAttribs", v_arr(array_new()));

    if (!rs->tagstack) { rs->tagstack = array_new(); rs->tagdata = array_new(); }
    array_push(rs->tagstack, v_str(kf_upper(tagname ? kprintf("CF_%s", tagname) : "CFMODULE")));
    Struct *td = struct_new();
    struct_set(td, "ThisTag", v_struct(tc->thistag));
    struct_set(td, "Attributes", v_struct(attrs));
    struct_set(td, "__variables", v_struct(tc->variables));
    array_push(rs->tagdata, v_struct(td));

    run_custom_mode(tc, t, "start", flow);
    int f = *flow;
    if (f == FL_EXIT_TAG) goto done;
    if (has_end && f != FL_EXIT_TAG) {
        for (;;) {
            /* run the body in the caller's context, capturing output */
            Buf cap; buf_init(&cap);
            Buf *saved_out = rs->out;
            rs->out = &cap;
            int bf = FL_OK;
            if (n->nkids) exec_nodes(c, n->kids, n->nkids, &bf);
            rs->out = saved_out;
            struct_set(tc->thistag, "GeneratedContent", v_strn(buf_cstr(&cap), cap.len));
            /* end-mode output follows the (possibly rewritten) body content */
            Buf endout; buf_init(&endout);
            rs->out = &endout;
            run_custom_mode(tc, t, "end", flow);
            rs->out = saved_out;
            Val *gc = struct_get(tc->thistag, "GeneratedContent");
            if (gc && v_is_simple(*gc)) out_puts(c, v_tostr(*gc));
            out_put(c, endout.s ? endout.s : "", endout.len);
            if (*flow == FL_EXIT_LOOP) {
                *flow = FL_OK;
                continue;
            }
            break;
        }
    }
done:
    rs->tagstack->n--; rs->tagdata->n--;
    *flow = FL_OK;
}

TAG(module) {
    Struct *attrs = struct_new();
    for (int i = 0; i < n->nattrs; i++) {
        const char *an = n->attrs[i].name;
        if (!strcmp(an, "template") || !strcmp(an, "name")) continue;
        if (!strcmp(an, "attributecollection")) {
            Val v = eval(c, n->attrs[i].val);
            if (v.t == VT_STRUCT) for (int j = 0; j < v.u.st->n; j++) struct_set(attrs, v.u.st->e[j].key, v.u.st->e[j].v);
            continue;
        }
        struct_set(attrs, an, eval(c, n->attrs[i].val));
    }
    const char *path;
    const char *tpl = attr_str(c, n, "template", NULL);
    if (tpl) path = resolve_template_path(c, tpl, 1);
    else {
        const char *name = attr_str(c, n, "name", NULL);
        if (!name) kf_throw(c, "Application", "Attribute validation error for tag CFMODULE.",
                            "The tag requires either the TEMPLATE or the NAME attribute.");
        char *rel = kstrdup(name);
        for (char *p = rel; *p; p++) if (*p == '.') *p = '/';
        path = kf_path_join(kf_path_join(G.root, "customtags"), kprintf("%s.cfm", rel));
    }
    call_custom_tag(c, n, path, attrs, flow);
}

TAG(associate) {
    (void)flow;
    const char *base = require_attr(c, n, "basetag");
    const char *datacol = attr_str(c, n, "datacollection", "AssocAttribs");
    RState *rs = c->rs;
    if (!rs->tagstack) return;
    for (int i = rs->tagstack->n - 2; i >= 0; i--) {
        if (!kf_stricmp(v_tostr(rs->tagstack->v[i]), base)) {
            Struct *td = rs->tagdata->v[i].u.st;
            Struct *tt = struct_get(td, "ThisTag")->u.st;
            Val *arr = struct_get(tt, datacol);
            if (!arr || arr->t != VT_ARRAY) { struct_set(tt, datacol, v_arr(array_new())); arr = struct_get(tt, datacol); }
            array_push(arr->u.a, v_struct(c->attributes ? c->attributes : struct_new()));
            return;
        }
    }
    kf_throw(c, "Application", "CFASSOCIATE error.", kprintf("The base tag %s was not found in the ancestor tags.", kf_upper(base)));
}

/* ================================================================ CFSWITCH */
TAG(switch) {
    Val v = attr_val(c, n, "expression", NULL);
    const char *sv = val_simple_str(c, v, NULL);
    Node *def = NULL;
    for (int i = 0; i < n->nkids; i++) {
        Node *k = n->kids[i];
        if (k->k != N_TAG) continue;
        if (!strcmp(k->tag, "cfdefaultcase")) { def = k; continue; }
        if (strcmp(k->tag, "cfcase")) continue;
        c->rs->cur_node = k;
        const char *vals = attr_str(c, k, "value", "");
        const char *delim = attr_str(c, k, "delimiters", ",");
        Array *a = list_to_array_k(vals, delim);
        for (int j = 0; j < a->n; j++) {
            if (!kf_stricmp(v_tostr(a->v[j]), sv) || v_compare(a->v[j], v) == 0) {
                exec_body(c, k, flow);
                if (*flow == FL_BREAK) *flow = FL_OK;
                return;
            }
        }
    }
    if (def) { exec_body(c, def, flow); if (*flow == FL_BREAK) *flow = FL_OK; }
}
TAG(case) { UNUSED; }

/* ================================================================ CFTRY */
static int catch_matches(const char *ctype, KfError *e) {
    if (!kf_stricmp(ctype, "any")) return 1;
    if (!kf_stricmp(ctype, e->type)) return 1;
    /* custom types match by prefix: "MyApp" catches "MyApp.Error" */
    size_t n = strlen(ctype);
    if (!kf_strnicmp(e->type, ctype, n) && e->type[n] == '.') return 1;
    return 0;
}

TAG(try) {
    RState *rs = c->rs;
    /* body excludes the cfcatch children */
    int nb = 0;
    Node **body = kmalloc(sizeof(Node *) * (n->nkids ? n->nkids : 1));
    for (int i = 0; i < n->nkids; i++) {
        Node *k = n->kids[i];
        if (k->k == N_TAG && !strcmp(k->tag, "cfcatch")) continue;
        body[nb++] = k;
    }
    JmpFrame jf; jf.prev = rs->jf; rs->jf = &jf;
    Buf *saved_out = rs->out;
    size_t saved_len = rs->out->len;
    int saved_inout = c->in_output, saved_sql = c->sql_mode;
    QLoop *saved_ql = c->qloop;
    Node *saved_node = rs->cur_node;
    int saved_depth = rs->depth;
    Template *saved_tpl = rs->cur_tpl;
    const char *saved_dir = c->tagdir;
    int saved_locks = rs->locks_held;
    if (setjmp(jf.jb) == 0) {
        exec_nodes(c, body, nb, flow);
        rs->jf = jf.prev;
        return;
    }
    rs->jf = jf.prev;
    KfError *e = rs->err;
    rs->err = NULL;
    if (!strcmp(e->type, "__abort")) kf_throw_err(rs, e);
    /* release locks acquired inside the try */
    while (rs->locks_held > saved_locks) {
        rs->locks_held--;
        named_unlock((int)(intptr_t)rs->held_locks[rs->locks_held]);
    }
    rs->out = saved_out;
    (void)saved_len;
    c->in_output = saved_inout; c->sql_mode = saved_sql; c->qloop = saved_ql;
    rs->cur_node = saved_node; rs->depth = saved_depth; rs->cur_tpl = saved_tpl; c->tagdir = saved_dir;
    for (int i = 0; i < n->nkids; i++) {
        Node *k = n->kids[i];
        if (k->k != N_TAG || strcmp(k->tag, "cfcatch")) continue;
        const char *ctype = attr_str(c, k, "type", "any");
        if (!catch_matches(ctype, e)) continue;
        Val *old = struct_get(c->variables, "cfcatch");
        Val oldv = old ? *old : v_null();
        struct_set(c->variables, "cfcatch", error_to_cfcatch(e));
        struct_set(c->variables, "__kf_rethrow", v_null());
        /* stash the error for CFRETHROW */
        Val holder = v_binary((const char *)e, 0);
        struct_set(c->variables, "__kf_err", holder);
        rs->cur_node = k;
        exec_body(c, k, flow);
        struct_delete(c->variables, "__kf_err");
        if (old) struct_set(c->variables, "cfcatch", oldv);
        return;
    }
    kf_throw_err(rs, e);
}
TAG(catch) { UNUSED; }

TAG(throw) {
    (void)flow;
    const char *type = attr_str(c, n, "type", "Application");
    const char *msg = attr_str(c, n, "message", "");
    const char *detail = attr_str(c, n, "detail", "");
    KfError *e = kf_error_new(type, msg, detail);
    e->errorcode = attr_str(c, n, "errorcode", "");
    e->extended = attr_str(c, n, "extendedinfo", "");
    e->custom = v_bool(1);
    if (!*msg) e->message = kprintf("Unhandled exception of type %s.", kf_html_escape(type));
    kf_throw_err(c->rs, e);
}

TAG(rethrow) {
    (void)flow; (void)n;
    Val *h = struct_get(c->variables, "__kf_err");
    if (!h || h->t != VT_BINARY)
        kf_throw(c, "Template", "Context validation error for tag CFRETHROW.", "CFRETHROW may only be used inside a CFCATCH block.");
    kf_throw_err(c->rs, (KfError *)h->u.str.s);
}

/* ================================================================ CFSCRIPT */
TAG(script) {
    if (!n->script) return;
    int saved = c->in_output;
    script_exec(c, n->script, flow);
    c->in_output = saved;
    if (*flow == FL_BREAK || *flow == FL_CONTINUE) *flow = FL_OK;
}

/* ================================================================ CFSETTING / CFSILENT */
TAG(setting) {
    UNUSED;
    RState *rs = c->rs;
    int present;
    Val v = attr_val(c, n, "enablecfoutputonly", &present);
    if (present) {
        int b;
        if (!v_tobool(v, &b)) kf_throw(c, "Application", "Attribute validation error for tag CFSETTING.",
                                       "ENABLECFOUTPUTONLY must be YES or NO.");
        if (b) rs->enablecfoutputonly++;
        else if (rs->enablecfoutputonly > 0) rs->enablecfoutputonly--;
    }
    v = attr_val(c, n, "showdebugoutput", &present);
    if (present) { int b; if (v_tobool(v, &b)) rs->debug_override = b; }
}

TAG(silent) {
    Buf sink; buf_init(&sink);
    RState *rs = c->rs;
    Buf *saved = rs->out;
    rs->out = &sink;
    JmpFrame jf; jf.prev = rs->jf; rs->jf = &jf;
    if (setjmp(jf.jb) == 0) {
        exec_body(c, n, flow);
        rs->jf = jf.prev;
        rs->out = saved;
        return;
    }
    rs->jf = jf.prev;
    rs->out = saved;
    kf_throw_err(rs, rs->err);
}

TAG(processingdirective) {
    int ws = attr_bool(c, n, "suppresswhitespace", -1);
    RState *rs = c->rs;
    if (!n->has_end) { if (ws >= 0) rs->suppress_ws = ws; return; }
    if (ws != 1) { exec_body(c, n, flow); return; }
    Buf cap; buf_init(&cap);
    Buf *saved = rs->out;
    rs->out = &cap;
    exec_body(c, n, flow);
    rs->out = saved;
    /* compress runs of whitespace */
    char *s = buf_cstr(&cap);
    Buf o; buf_init(&o);
    for (size_t i = 0; i < cap.len; ) {
        if (isspace((unsigned char)s[i])) {
            int nl = 0; size_t j = i;
            while (j < cap.len && isspace((unsigned char)s[j])) { if (s[j] == '\n') nl = 1; j++; }
            buf_putc(&o, nl ? '\n' : ' ');
            i = j;
        } else buf_putc(&o, s[i++]);
    }
    out_put(c, o.s ? o.s : "", o.len);
}

/* ================================================================ HTTP response */
static const char *url_token(RState *rs) {
    if (!rs->cfid) return "";
    return kprintf("CFID=%s&CFTOKEN=%s", rs->cfid, rs->cftoken);
}

TAG(location) {
    (void)flow;
    const char *url = require_attr(c, n, "url");
    int addtoken = attr_bool(c, n, "addtoken", 1);
    RState *rs = c->rs;
    if (addtoken && rs->cfid && (rs->session || rs->client_enabled))
        url = kprintf("%s%c%s", url, strchr(url, '?') ? '&' : '?', url_token(rs));
    rs->location = url;
    rs->status = 302; rs->status_text = "Object Moved";
    throw_abort(c);
}

static char *cookie_date(double dt) {
    dt = date_local_to_utc(dt);
    int y, mo, d, h, mi, s;
    date_to_parts(dt, &y, &mo, &d, &h, &mi, &s);
    static const char *DN[] = {"Sun","Mon","Tue","Wed","Thu","Fri","Sat"};
    static const char *MN[] = {"Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"};
    return kprintf("%s, %02d-%s-%04d %02d:%02d:%02d GMT", DN[date_dow(dt) - 1], d, MN[mo - 1], y, h, mi, s);
}

void add_set_cookie(RState *rs, const char *name, const char *value, const char *expires, const char *path,
                    const char *domain, int secure) {
    Buf b; buf_init(&b);
    buf_printf(&b, "%s=%s", kf_upper(name), kf_urlencode(value));
    if (expires && *expires) buf_printf(&b, "; expires=%s", expires);
    buf_printf(&b, "; path=%s", path && *path ? path : "/");
    if (domain && *domain) buf_printf(&b, "; domain=%s", domain);
    if (secure) buf_puts(&b, "; secure");
    if (!rs->setcookies) rs->setcookies = array_new();
    array_push(rs->setcookies, v_str(buf_cstr(&b)));
}

TAG(cookie) {
    (void)flow;
    RState *rs = c->rs;
    const char *name = require_attr(c, n, "name");
    const char *value = attr_str(c, n, "value", "");
    const char *exp = attr_str(c, n, "expires", NULL);
    const char *expires = NULL;
    if (exp) {
        double d;
        if (!kf_stricmp(exp, "now")) { expires = cookie_date(date_now() - 365 * 10); value = ""; }
        else if (!kf_stricmp(exp, "never")) expires = cookie_date(date_now() + 365.25 * 30);
        else if (v_isnumeric_str(exp, &d)) expires = cookie_date(date_now() + d);
        else if (date_parse(exp, &d)) expires = cookie_date(d);
    }
    add_set_cookie(rs, name, value, expires, attr_str(c, n, "path", "/"), attr_str(c, n, "domain", NULL),
                   attr_bool(c, n, "secure", 0));
    if (exp && !kf_stricmp(exp, "now")) struct_delete(rs->cookie, name);
    else struct_set(rs->cookie, name, v_strdup(value));
}

TAG(header) {
    (void)flow;
    RState *rs = c->rs;
    const char *sc = attr_str(c, n, "statuscode", NULL);
    if (sc) {
        rs->status = atoi(sc);
        rs->status_text = attr_str(c, n, "statustext", "");
        return;
    }
    const char *name = require_attr(c, n, "name");
    const char *value = attr_str(c, n, "value", "");
    if (!kf_stricmp(name, "content-type")) { rs->content_type = value; return; }
    if (!rs->headers) rs->headers = struct_new();
    struct_set(rs->headers, name, v_strdup(value));
}

TAG(content) {
    (void)flow;
    tag_security_check(c, "cfcontent");
    RState *rs = c->rs;
    const char *type = attr_str(c, n, "type", NULL);
    if (type) rs->content_type = type;
    int reset = attr_bool(c, n, "reset", 1);
    const char *file = attr_str(c, n, "file", NULL);
    if (reset) rs->page.len = 0;
    if (file) {
        rs->content_file = file;
        rs->content_delete = attr_bool(c, n, "deletefile", 0);
        throw_abort(c);
    }
    if (n->nkids) exec_body(c, n, flow);
}

TAG(htmlhead) {
    (void)flow;
    buf_puts(&c->rs->htmlhead, require_attr(c, n, "text"));
}

/* ================================================================ CFAPPLICATION */
static double timespan_attr(Ctx *c, Node *n, const char *name, double def) {
    int present;
    Val v = attr_val(c, n, name, &present);
    if (!present) return def;
    double d;
    if (!v_tonum(v, &d)) kf_throw(c, "Application", "Attribute validation error for tag CFAPPLICATION.",
                                  kprintf("The value of the attribute %s must be a timespan created with CreateTimeSpan().", kf_upper(name)));
    return d;
}

static double cfg_days(const char *entry, double def) {
    char *v = cfg("Variables", entry, NULL);
    double d;
    if (v && v_isnumeric_str(v, &d)) return d;
    return def;
}

TAG(application) {
    (void)flow;
    RState *rs = c->rs;
    const char *name = require_attr(c, n, "name");
    int sessmgmt = attr_bool(c, n, "sessionmanagement", 0);
    int clientmgmt = attr_bool(c, n, "clientmanagement", 0);
    int setcookies = attr_bool(c, n, "setclientcookies", 1);
    const char *storage = attr_str(c, n, "clientstorage", NULL);
    if (!storage) storage = cfg("Variables", "DefaultClientStorage", "Registry");

    double app_def = cfg_days("ApplicationTimeoutDefault", 2.0), app_max = cfg_days("ApplicationTimeoutMax", 2.0);
    double ses_def = cfg_days("SessionTimeoutDefault", 20.0 / 1440), ses_max = cfg_days("SessionTimeoutMax", 20.0 / 1440);
    double app_to = timespan_attr(c, n, "applicationtimeout", app_def);
    double ses_to = timespan_attr(c, n, "sessiontimeout", ses_def);
    if (app_to > app_max) app_to = app_max;
    if (ses_to > ses_max) ses_to = ses_max;

    rs->appname = name;
    if (cfg_int("Variables", "EnableApplicationVariables", 1)) {
        int created;
        AppState *a = app_get(name, app_to, &created);
        rs->app = a;
        rs->application = a->scope;
        if (!struct_get(a->scope, "ApplicationName")) struct_set(a->scope, "ApplicationName", v_strdup(name));
    }

    if (sessmgmt || clientmgmt) {
        Val *v;
        const char *cfid = NULL, *cftoken = NULL;
        if ((v = struct_get(rs->url, "CFID")) && struct_get(rs->url, "CFTOKEN")) {
            cfid = v_tostr(*v); cftoken = v_tostr(*struct_get(rs->url, "CFTOKEN"));
        } else if ((v = struct_get(rs->cookie, "CFID")) && struct_get(rs->cookie, "CFTOKEN")) {
            cfid = v_tostr(*v); cftoken = v_tostr(*struct_get(rs->cookie, "CFTOKEN"));
        }
        if (!cfid || !*cfid || !v_isnumeric_str(cfid, NULL) || !cftoken || !v_isnumeric_str(cftoken, NULL)) {
            cfid = kprintf("%ld", next_cfid());
            cftoken = kprintf("%08d", (int)(random() % 100000000));
            if (setcookies) {
                const char *exp = cookie_date(date_now() + 365.25 * 30);
                add_set_cookie(rs, "CFID", cfid, exp, "/", NULL, 0);
                add_set_cookie(rs, "CFTOKEN", cftoken, exp, "/", NULL, 0);
            }
            struct_set(rs->cookie, "CFID", v_strdup(cfid));
            struct_set(rs->cookie, "CFTOKEN", v_strdup(cftoken));
        }
        rs->cfid = cfid; rs->cftoken = cftoken;
    }
    if (sessmgmt && cfg_int("Variables", "EnableSessionVariables", 1)) {
        if (!rs->sess) {
            int created;
            SessState *s = sess_get(name, rs->cfid, rs->cftoken, ses_to, &created);
            rs->sess = s;
            rs->session = s->scope;
            if (cfg_int("Locking", "SingleThreadedSessions", 0)) pthread_mutex_lock(&s->mu);
            if (created || !struct_get(s->scope, "CFID")) {
                struct_set(s->scope, "CFID", v_strdup(rs->cfid));
                struct_set(s->scope, "CFTOKEN", v_strdup(rs->cftoken));
                struct_set(s->scope, "URLToken", v_strdup(url_token(rs)));
                struct_set(s->scope, "SessionID", v_strdup(kprintf("%s_%s_%s", kf_upper(name), rs->cfid, rs->cftoken)));
            }
        }
    }
    if (clientmgmt) {
        rs->client_enabled = 1;
        rs->client_storage = storage;
        client_load(rs, name);
    }
}

/* ================================================================ CFLOCK */
TAG(lock) {
    RState *rs = c->rs;
    const char *name = attr_str(c, n, "name", NULL);
    const char *scope = attr_str(c, n, "scope", NULL);
    double timeout = attr_num(c, n, "timeout", 30);
    const char *type = attr_str(c, n, "type", "exclusive");
    int throwon = attr_bool(c, n, "throwontimeout", 1);
    const char *lname;
    if (scope) {
        if (!kf_stricmp(scope, "session")) lname = kprintf("SESSION:%s", rs->sess ? rs->sess->key : "none");
        else if (!kf_stricmp(scope, "application")) lname = kprintf("APPLICATION:%s", rs->appname ? kf_upper(rs->appname) : "none");
        else if (!kf_stricmp(scope, "server")) lname = "SERVER";
        else kf_throw(c, "Application", "Attribute validation error for tag CFLOCK.",
                      "The value of SCOPE must be one of Session, Application or Server.");
    } else if (name) lname = kprintf("NAME:%s", kf_upper(name));
    else kf_throw(c, "Application", "Attribute validation error for tag CFLOCK.", "The tag requires either the NAME or the SCOPE attribute.");
    int h = named_lock(lname, kf_stricmp(type, "readonly") != 0, timeout);
    if (h < 0) {
        if (!throwon) return;
        KfError *e = kf_error_new("Lock", kprintf("A timeout occurred while attempting to lock %s.", kf_html_escape(name ? name : scope)),
                                  kprintf("The lock could not be obtained within %s seconds.", fmt_number(timeout)));
        kf_throw_err(rs, e);
    }
    if (rs->locks_held < 32) { rs->held_lock_names[rs->locks_held] = lname; rs->held_locks[rs->locks_held++] = (void *)(intptr_t)h; }
    JmpFrame jf; jf.prev = rs->jf; rs->jf = &jf;
    if (setjmp(jf.jb) == 0) {
        exec_body(c, n, flow);
        rs->jf = jf.prev;
        if (rs->locks_held) rs->locks_held--;
        named_unlock(h);
        return;
    }
    rs->jf = jf.prev;
    if (rs->locks_held) rs->locks_held--;
    named_unlock(h);
    kf_throw_err(rs, rs->err);
}

/* ================================================================ CFERROR */
TAG(error) {
    (void)flow;
    RState *rs = c->rs;
    const char *type = attr_str(c, n, "type", "request");
    const char *tpl = require_attr(c, n, "template");
    if (!rs->cferror) rs->cferror = struct_new();
    Struct *h = struct_new();
    struct_set(h, "template", v_strdup(resolve_template_path(c, tpl, 0)));
    struct_set(h, "mailto", v_strdup(attr_str(c, n, "mailto", "")));
    struct_set(rs->cferror, kf_lower(type), v_struct(h));
}

/* ================================================================ misc */
/* CFCACHE: ColdFusion 4.5 saved the rendered page to a static file and served
 * that copy until it expired. Cache files live in <root>/cache (or DIRECTORY=). */
TAG(cache) {
    (void)flow;
    RState *rs = c->rs;
    const char *action = attr_str(c, n, "action", "cache");
    const char *dir = attr_str(c, n, kf_stricmp(action, "flush") ? "cachedirectory" : "directory", NULL);
    if (!dir) dir = attr_str(c, n, "directory", NULL);
    if (!dir) dir = kf_path_join(G.root, "cache");
    if (kf_stricmp(action, "cache") && kf_stricmp(action, "flush") && kf_stricmp(action, "clientcache") && kf_stricmp(action, "optimal"))
        kf_throw(c, "Application", "Attribute validation error for tag CFCACHE.",
                 kprintf("The value of the attribute ACTION, which is currently \"%s\", must be one of the values: CACHE, FLUSH, CLIENTCACHE, OPTIMAL.",
                         kf_html_escape(action)));
    if (!kf_stricmp(action, "clientcache") || !kf_stricmp(action, "optimal")) {
        /* browser caching: Last-Modified is the template's date (or TIMEOUT, if later); a browser
         * that already holds that version gets 304 Not Modified */
        struct stat ts;
        time_t lm = rs->cur_tpl && stat(rs->cur_tpl->path, &ts) == 0 ? ts.st_mtime : time(NULL);
        int tp; double td;
        Val tov = attr_val(c, n, "timeout", &tp);
        if (tp && v_todate(tov, &td)) { time_t tt = (time_t)((date_local_to_utc(td) - 25569.0) * 86400.0); if (tt > lm && tt <= time(NULL)) lm = tt; }
        char *lms = http_date(lm);
        if (!rs->headers) rs->headers = struct_new();
        struct_set(rs->headers, "Last-Modified", v_str(lms));
        struct_set(rs->headers, "Cache-Control", v_str("private"));
        Val *ims = rs->http && rs->http->headers ? struct_get(rs->http->headers, "if-modified-since") : NULL;
        if (ims && !strcmp(v_tostr(*ims), lms)) {
            rs->status = 304; rs->status_text = "Not Modified";
            rs->page.len = 0;
            rs->debug_override = 0;
            throw_abort(c);
        }
        if (!kf_stricmp(action, "clientcache")) return;
    }
    kf_mkdirs(dir);
    if (!kf_stricmp(action, "flush")) {
        const char *expire = attr_str(c, n, "expireurl", NULL);
        DIR *d = opendir(dir);
        struct dirent *de;
        while (d && (de = readdir(d))) {
            if (strncmp(de->d_name, "kfcache_", 8)) continue;
            char *p = kf_path_join(dir, de->d_name);
            if (expire && *expire) {
                size_t len; char *data = kf_read_file(p, &len);
                int match = data && kf_stristr(data, kprintf("<!-- KFCACHE %s", expire)) == data;
                free(data);
                if (!match) continue;
            }
            unlink(p);
        }
        if (d) closedir(d);
        return;
    }
    Val *sn = struct_get(rs->cgi, "SCRIPT_NAME"), *qs = struct_get(rs->cgi, "QUERY_STRING");
    const char *key = kprintf("%s?%s", sn ? v_tostr(*sn) : "", qs ? v_tostr(*qs) : "");
    char *file = kf_path_join(dir, kprintf("kfcache_%s.tmp", md5_hex_upper(key, strlen(key))));
    double timeout = 0;
    int present;
    Val tv = attr_val(c, n, "timeout", &present);
    if (present) v_todate(tv, &timeout);          /* cached copies older than this date are stale */
    struct stat st;
    if (stat(file, &st) == 0) {
        struct tm tm; localtime_r(&st.st_mtime, &tm);
        double made = date_from_parts(tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec);
        if (!timeout || made >= timeout) {
            size_t len;
            char *data = kf_read_file(file, &len);
            if (data) {
                char *body = strstr(data, "-->\n");
                rs->page.len = 0;
                buf_puts(&rs->page, body ? body + 4 : data);
                free(data);
                rs->debug_override = 0;
                throw_abort(c);
            }
        }
    }
    rs->cache_file = file;
    rs->cache_key = kstrdup(key);
}


TAG(defaultcase) { UNUSED; }

/* ================================================================ registry */
typedef struct TagDef { const char *name; TagFn fn; int paired; } TagDef;

static TagDef TAGS[] = {
    {"cfset", tag_set, 0}, {"cfoutput", tag_output, 2}, {"cfif", tag_if, 2}, {"cfloop", tag_loop, 2},
    {"cfbreak", tag_break, 0}, {"cfabort", tag_abort, 0}, {"cfexit", tag_exit, 0}, {"cfparam", tag_param, 0},
    {"cfinclude", tag_include, 0}, {"cfmodule", tag_module, 1}, {"cfassociate", tag_associate, 0},
    {"cfswitch", tag_switch, 2}, {"cfcase", tag_case, 2}, {"cfdefaultcase", tag_defaultcase, 2},
    {"cftry", tag_try, 2}, {"cfcatch", tag_catch, 2}, {"cfthrow", tag_throw, 0}, {"cfrethrow", tag_rethrow, 0},
    {"cfscript", tag_script, 2}, {"cfsetting", tag_setting, 0}, {"cfsilent", tag_silent, 2},
    {"cfprocessingdirective", tag_processingdirective, 1},
    {"cflocation", tag_location, 0}, {"cfcookie", tag_cookie, 0}, {"cfheader", tag_header, 0},
    {"cfcontent", tag_content, 1}, {"cfhtmlhead", tag_htmlhead, 0}, {"cfapplication", tag_application, 0},
    {"cflock", tag_lock, 2}, {"cferror", tag_error, 0}, {"cfcache", tag_cache, 0},
    {"cfelse", NULL, 0}, {"cfelseif", NULL, 0},
    /* database */
    {"cfquery", tag_query, 2}, {"cfqueryparam", tag_queryparam, 0}, {"cftransaction", tag_transaction, 2},
    {"cfinsert", tag_insert, 0}, {"cfupdate", tag_update, 0}, {"cfstoredproc", tag_storedproc, 2},
    {"cfprocparam", tag_procparam, 0}, {"cfprocresult", tag_procresult, 0}, {"cfobjectcache", tag_objectcache, 0},
    /* io */
    {"cfmail", tag_mail, 2}, {"cfmailparam", tag_mailparam, 0}, {"cffile", tag_file, 0},
    {"cfdirectory", tag_directory, 0}, {"cfregistry", tag_registry, 0}, {"cfhttp", tag_http, 1},
    {"cfhttpparam", tag_httpparam, 0}, {"cfschedule", tag_schedule, 0}, {"cfexecute", tag_execute, 1},
    {"cfwddx", tag_wddx, 0}, {"cfpop", tag_pop, 0}, {"cfftp", tag_ftp, 0}, {"cfldap", tag_ldap, 0},
    {"cfobject", tag_object, 0}, {"cfservlet", tag_servlet, 1}, {"cfservletparam", tag_servletparam, 0},
    {"cfreport", tag_report, 1}, {"cfindex", tag_index, 0}, {"cfsearch", tag_search, 0},
    {"cfcollection", tag_collection, 0}, {"cfauthenticate", tag_authenticate, 0},
    {"cfimpersonate", tag_impersonate, 2}, {"cfadminsecurity", tag_adminsecurity, 0},
    /* forms & display */
    {"cfform", tag_form, 2}, {"cfinput", tag_input, 0}, {"cfselect", tag_select, 1},
    {"cftextinput", tag_textinput, 0}, {"cfslider", tag_slider, 0}, {"cfgrid", tag_grid, 1},
    {"cfgridcolumn", tag_gridcolumn, 0}, {"cfgridrow", tag_gridrow, 0}, {"cfgridupdate", tag_gridupdate, 0},
    {"cftree", tag_tree, 1}, {"cftreeitem", tag_treeitem, 0}, {"cfapplet", tag_applet, 0},
    {"cftable", tag_table, 2}, {"cfcol", tag_col, 0},
    {NULL, NULL, 0}
};

TagFn tag_lookup(const char *name) {
    for (int i = 0; TAGS[i].name; i++) if (!strcmp(TAGS[i].name, name)) return TAGS[i].fn;
    return NULL;
}

int tag_is_paired(const char *name) {
    if (!strncmp(name, "cf_", 3)) return 1;
    for (int i = 0; TAGS[i].name; i++) if (!strcmp(TAGS[i].name, name)) return TAGS[i].paired;
    return 0;
}

Query *tag_list_all(void) {
    const char *cols[] = {"Name"};
    Query *q = query_new(1, cols);
    for (int i = 0; TAGS[i].name; i++) {
        int r = query_add_row(q);
        query_set(q, 0, r, v_str(kf_upper(TAGS[i].name)));
    }
    return q;
}
