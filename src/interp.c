/*
 * interp.c - the template interpreter: template cache, node execution,
 * Application.cfm handling, error pages and debug output.
 */
#define _GNU_SOURCE
#include "engine.h"
#include <stdlib.h>
#include <ctype.h>
#include <time.h>
#include <sys/stat.h>
#include <pthread.h>
#include <unistd.h>

__thread RState *t_rs;

/* ================================================================ errors */
KfError *kf_error_new(const char *type, const char *msg, const char *detail) {
    KfError *e = kmalloc(sizeof(KfError));
    e->type = kstrdup(type ? type : "Application");
    e->message = kstrdup(msg ? msg : "");
    e->detail = kstrdup(detail ? detail : "");
    e->custom = v_null();
    return e;
}

void kf_out_of_memory(void) {
    RState *rs = t_rs;
    if (rs && rs->jf) {
        KfError *e = kf_error_new("Application", "Out of memory.",
            "The request exceeded the maximum amount of memory a single KoldFusion request may use.");
        kf_throw_err(rs, e);
    }
    fprintf(stderr, "KoldFusion: out of memory\n");
    abort();
}

void kf_throw_err(RState *rs, KfError *e) {
    if (!e->tplpath && rs->cur_tpl) e->tplpath = rs->cur_tpl->path;
    if (!e->tagname && rs->cur_node) {
        Node *n = rs->cur_node;
        e->tagname = n->k == N_TAG ? kf_upper(n->tag) : (n->rawsrc ? kstrndup(n->rawsrc, n->rawlen) : "");
        if (!e->line) { e->line = n->line; e->col = n->col; }
    }
    rs->err = e;
    if (!rs->jf) { fprintf(stderr, "KoldFusion: uncaught error: %s\n", e->message); abort(); }
    longjmp(rs->jf->jb, 1);
}

void kf_throw(Ctx *c, const char *type, const char *msg, const char *detail) {
    KfError *e = kf_error_new(type, msg, detail);
    kf_throw_err(c->rs, e);
}

void kf_throw_at(Ctx *c, Expr *where, const char *type, const char *msg, const char *detail) {
    KfError *e = kf_error_new(type, msg, detail);
    RState *rs = c->rs;
    if (where && where->line) { e->line = where->line; e->col = where->col; }
    Node *n = rs->cur_node;
    if (n && n->k == N_EXPR && n->rawsrc) {
        e->heading = "An error occurred while evaluating the expression:";
        e->snippet = kstrndup(n->rawsrc, n->rawlen);
    } else if (n && n->k == N_TAG && (!strcmp(n->tag, "cfset") || !strcmp(n->tag, "cfif") || !strcmp(n->tag, "cfelseif"))) {
        e->heading = "An error occurred while evaluating the expression:";
        if (n->expr && n->expr->src) e->snippet = kstrndup(n->expr->src, n->expr->srclen);
    } else if (where && where->src && where->srclen > 0) {
        e->heading = "An error occurred while evaluating the expression:";
        e->snippet = kstrndup(where->src, where->srclen);
    }
    kf_throw_err(rs, e);
}

Val error_to_cfcatch(KfError *e) {
    Struct *s = struct_new();
    struct_set(s, "Type", v_strdup(e->type));
    struct_set(s, "Message", v_strdup(e->message));
    struct_set(s, "Detail", v_strdup(e->detail));
    struct_set(s, "ErrorCode", v_strdup(e->errorcode ? e->errorcode : ""));
    struct_set(s, "ExtendedInfo", v_strdup(e->extended ? e->extended : ""));
    if (!kf_stricmp(e->type, "Database")) {
        struct_set(s, "NativeErrorCode", v_strdup(e->nativecode ? e->nativecode : "0"));
        struct_set(s, "SQLState", v_str(e->sqlstate ? kstrndup(e->sqlstate, strcspn(e->sqlstate, " ")) : ""));
    }
    if (!kf_stricmp(e->type, "Lock")) {
        struct_set(s, "LockName", v_str(""));
        struct_set(s, "LockOperation", v_str("Timeout"));
    }
    if (!kf_stricmp(e->type, "MissingInclude")) struct_set(s, "MissingFileName", v_strdup(e->extended ? e->extended : ""));
    Array *tc = array_new();
    Struct *t = struct_new();
    struct_set(t, "ID", v_strdup(e->tagname ? e->tagname : "??"));
    struct_set(t, "Line", v_num(e->line));
    struct_set(t, "Column", v_num(e->col));
    struct_set(t, "Template", v_strdup(e->tplpath ? e->tplpath : ""));
    array_push(tc, v_struct(t));
    struct_set(s, "TagContext", v_arr(tc));
    return v_struct(s);
}

/* ================================================================ output */
void out_put(Ctx *c, const char *s, size_t n) { buf_put(c->rs->out, s, n); }
void out_puts(Ctx *c, const char *s) { if (s) buf_put(c->rs->out, s, strlen(s)); }

const char *kf_html_escape(const char *s) {
    if (!s) return "";
    if (!strpbrk(s, "<>&\"")) return s;
    Buf b; buf_init(&b);
    for (; *s; s++) {
        switch (*s) {
        case '<': buf_puts(&b, "&lt;"); break;
        case '>': buf_puts(&b, "&gt;"); break;
        case '&': buf_puts(&b, "&amp;"); break;
        case '"': buf_puts(&b, "&quot;"); break;
        default: buf_putc(&b, *s);
        }
    }
    return buf_cstr(&b);
}

const char *kf_template_dir(const char *path) {
    const char *sl = strrchr(path, '/');
    if (!sl) return kstrdup(".");
    return kstrndup(path, sl - path + 1);
}

/* ================================================================ attributes */
int has_attr(Node *n, const char *name) {
    for (int i = 0; i < n->nattrs; i++) if (!strcmp(n->attrs[i].name, name)) return 1;
    return 0;
}
Val attr_val(Ctx *c, Node *n, const char *name, int *present) {
    for (int i = 0; i < n->nattrs; i++) {
        if (!strcmp(n->attrs[i].name, name)) {
            if (present) *present = 1;
            return eval(c, n->attrs[i].val);
        }
    }
    if (present) *present = 0;
    return v_null();
}
const char *attr_str(Ctx *c, Node *n, const char *name, const char *def) {
    for (int i = 0; i < n->nattrs; i++) {
        if (!strcmp(n->attrs[i].name, name)) {
            Val v = eval(c, n->attrs[i].val);
            if (!v_is_simple(v))
                kf_throw(c, "Application", kprintf("Attribute validation error for tag %s.", kf_upper(n->tag)),
                         kprintf("The value of the attribute %s is a complex object and cannot be converted to a string.", kf_upper(name)));
            return v_tostr(v);
        }
    }
    return def;
}
const char *require_attr(Ctx *c, Node *n, const char *name) {
    const char *v = attr_str(c, n, name, NULL);
    if (!v)
        kf_throw(c, "Application", kprintf("Attribute validation error for tag %s.", kf_upper(n->tag)),
                 kprintf("The tag requires the attribute(s): %s.", kf_upper(name)));
    return v;
}
int attr_bool(Ctx *c, Node *n, const char *name, int def) {
    int present;
    Val v = attr_val(c, n, name, &present);
    if (!present) return def;
    if (v.t == VT_STR && !v.u.str.len) return 1;      /* bare attribute */
    int b;
    if (v_tobool(v, &b)) return b;
    kf_throw(c, "Application", kprintf("Attribute validation error for tag %s.", kf_upper(n->tag)),
             kprintf("The value of the attribute %s, which is currently \"%s\", must be a boolean value (YES/NO).",
                     kf_upper(name), kf_html_escape(v_tostr(v))));
}
double attr_num(Ctx *c, Node *n, const char *name, double def) {
    int present;
    Val v = attr_val(c, n, name, &present);
    if (!present) return def;
    double d;
    if (v_tonum(v, &d)) return d;
    kf_throw(c, "Application", kprintf("Attribute validation error for tag %s.", kf_upper(n->tag)),
             kprintf("The value of the attribute %s, which is currently \"%s\", must be numeric.",
                     kf_upper(name), kf_html_escape(v_tostr(v))));
}

/* ================================================================ context */
Ctx *ctx_new(RState *rs, Template *t) {
    Ctx *c = kmalloc(sizeof(Ctx));
    c->rs = rs;
    c->tpl = t;
    c->variables = struct_new();
    c->tagdir = t ? kf_template_dir(t->path) : G.webroot;
    return c;
}

void check_timeout(Ctx *c) {
    RState *rs = c->rs;
    if (rs->deadline_ms > 0 && kf_time_ms() > rs->deadline_ms) {
        rs->deadline_ms = 0;  /* let the error page render */
        kf_throw(c, "Application", "Request timed out.",
                 kprintf("The request has exceeded the allowable time limit of %s seconds. "
                         "The KoldFusion Administrator sets the default; a single request may ask for more with "
                         "the RequestTimeout URL parameter (e.g. ?RequestTimeout=120).", fmt_number(rs->timeout_s)));
    }
}

/* ================================================================ template cache */
static pthread_mutex_t tc_mu = PTHREAD_MUTEX_INITIALIZER;
static Template *tc_head;
static size_t tc_bytes;

static long file_mtime(const char *path, size_t *size) {
    struct stat st;
    if (stat(path, &st) != 0 || S_ISDIR(st.st_mode)) return -1;
    if (size) *size = st.st_size;
    return (long)st.st_mtime;
}

static void tc_unlink(Template *t) {
    Template **pp = &tc_head;
    while (*pp) { if (*pp == t) { *pp = t->next; tc_bytes -= t->srclen; return; } pp = &(*pp)->next; }
}

static void tc_free(Template *t) {
    free(t->src);
    arena_free(t->arena);
}

static void tc_evict(size_t limit) {
    while (tc_bytes > limit) {
        Template *victim = NULL;
        for (Template *t = tc_head; t; t = t->next)
            if (t->refs == 0 && (!victim || t->last_used < victim->last_used)) victim = t;
        if (!victim) return;
        tc_unlink(victim);
        tc_free(victim);
    }
}

static void tpl_used_add(RState *rs, Template *t) {
    if (rs->ntpl_used == rs->captpl_used) {
        int nc = rs->captpl_used ? rs->captpl_used * 2 : 16;
        Template **n = kmalloc(sizeof(Template *) * nc);
        if (rs->ntpl_used) memcpy(n, rs->tpl_used, sizeof(Template *) * rs->ntpl_used);
        rs->tpl_used = n; rs->captpl_used = nc;
    }
    rs->tpl_used[rs->ntpl_used++] = t;
}

void templates_release(RState *rs) {
    pthread_mutex_lock(&tc_mu);
    for (int i = 0; i < rs->ntpl_used; i++) {
        Template *t = rs->tpl_used[i];
        t->refs--;
        if (t->stale && t->refs == 0) tc_free(t);
    }
    rs->ntpl_used = 0;
    pthread_mutex_unlock(&tc_mu);
}

Query *template_cache_list(void) {
    const char *cols[] = {"Path", "Size", "Refs", "LastUsed"};
    Query *q = query_new(4, cols);
    pthread_mutex_lock(&tc_mu);
    for (Template *t = tc_head; t; t = t->next) {
        int r = query_add_row(q);
        query_set(q, 0, r, v_strdup(t->path));
        query_set(q, 1, r, v_num((double)t->srclen));
        query_set(q, 2, r, v_num(t->refs));
        query_set(q, 3, r, v_date(t->last_used));
    }
    pthread_mutex_unlock(&tc_mu);
    return q;
}

void template_cache_flush(void) {
    pthread_mutex_lock(&tc_mu);
    Template *t = tc_head;
    tc_head = NULL; tc_bytes = 0;
    while (t) {
        Template *n = t->next;
        if (t->refs == 0) tc_free(t); else t->stale = 1;
        t = n;
    }
    pthread_mutex_unlock(&tc_mu);
}

Template *template_get(RState *rs, const char *path, KfError **perr) {
    *perr = NULL;
    int trusted = cfg_int(REG_SERVER, "TrustedCache", 0);
    size_t fsize = 0;
    long mt = -2;
    pthread_mutex_lock(&tc_mu);
    for (Template *t = tc_head; t; t = t->next) {
        if (strcmp(t->path, path)) continue;
        if (!trusted) {
            pthread_mutex_unlock(&tc_mu);
            mt = file_mtime(path, &fsize);
            pthread_mutex_lock(&tc_mu);
            /* re-find: list may have changed */
            Template *again = NULL;
            for (Template *u = tc_head; u; u = u->next) if (u == t) again = u;
            if (!again) break;
            if (mt != t->mtime) {
                tc_unlink(t);
                t->stale = 1;
                if (t->refs == 0) tc_free(t);
                break;
            }
        }
        t->refs++;
        t->last_used = date_now();
        pthread_mutex_unlock(&tc_mu);
        tpl_used_add(rs, t);
        return t;
    }
    pthread_mutex_unlock(&tc_mu);

    if (mt == -2) mt = file_mtime(path, &fsize);
    if (mt < 0) {
        char *ci = kf_resolve_ci(path);
        if (!ci || !strcmp(ci, path)) return NULL;
        return template_get(rs, ci, perr);
    }
    size_t len;
    char *src = kf_read_file(path, &len);
    if (!src) return NULL;
    Arena *a = arena_new();
    Template *t = template_parse(path, src, len, a, perr);
    if (!t) { free(src); arena_free(a); return NULL; }
    t->mtime = mt;
    t->refs = 1;
    if (getenv("KF_DUMP")) { extern void template_dump(Node *, int); template_dump(t->root, 0); }
    t->last_used = t->loaded_at = date_now();
    pthread_mutex_lock(&tc_mu);
    t->next = tc_head; tc_head = t; tc_bytes += len;
    size_t limit = (size_t)cfg_int(REG_SERVER, "TemplateCacheSize", 1024) * 1024;
    tc_evict(limit);
    pthread_mutex_unlock(&tc_mu);
    tpl_used_add(rs, t);
    return t;
}

/* ================================================================ paths */
static char *apply_mapping(const char *logical) {
    /* longest matching logical path in the Mappings key; "/" -> webroot */
    Query *q = reg_list(cfg_key("Mappings"), 0, 1);
    const char *best_l = "/", *best_d = G.webroot;
    size_t best_len = 1;
    for (int r = 0; r < q->nrows; r++) {
        const char *l = v_tostr(query_get(q, 0, r));
        const char *d = v_tostr(query_get(q, 2, r));
        size_t ll = strlen(l);
        while (ll > 1 && l[ll - 1] == '/') ll--;
        if (ll > best_len && !kf_strnicmp(logical, l, ll) && (logical[ll] == '/' || logical[ll] == 0)) {
            best_l = kstrndup(l, ll); best_d = d; best_len = ll;
        }
    }
    const char *rest = logical + (best_len == 1 ? 1 : best_len);
    (void)best_l;
    return kf_path_join(best_d, rest);
}

const char *resolve_template_path(Ctx *c, const char *tpl, int for_module) {
    (void)for_module;
    if (isalpha((unsigned char)tpl[0]) && tpl[1] == ':') return kf_native_path(tpl);
    char *t = kstrdup(tpl);
    for (char *p = t; *p; p++) if (*p == '\\') *p = '/';
    if (t[0] == '/') {
        /* absolute filesystem path that exists? (CF allowed C:\... paths) */
        struct stat st;
        if (!strncmp(t, G.root, strlen(G.root)) && stat(t, &st) == 0) return t;
        return apply_mapping(t);
    }
    return kf_path_join(c->tagdir, t);
}

/* ================================================================ security */
void tag_security_check(Ctx *c, const char *tagname) {
    /* Basic Security: a tag is restricted when its registry flag is 0 */
    char *v = cfg("Server\\TagRestrictions", tagname, NULL);
    if (!v || atoi(v) != 0) return;
    char *dir = cfg(REG_SERVER, "UnsecuredTagsDirectory", NULL);
    if (!dir || !*dir) dir = kf_path_join(G.webroot, "CFIDE/administrator/");
    const char *path = c->tpl ? c->tpl->path : "";
    if (*dir && !kf_strnicmp(path, dir, strlen(dir))) return;
    kf_throw(c, "Security", kprintf("Security: The requested template has been denied access to %s.", kf_upper(tagname)),
             kprintf("The tag %s has been disabled by the KoldFusion Administrator (Basic Security, Tag Restrictions). "
                     "It may only be used by templates in the unsecured tags directory.", kf_upper(tagname)));
}

/* ================================================================ execution */
static void exec_tag(Ctx *c, Node *n, int *flow) {
    RState *rs = c->rs;
    Node *saved = rs->cur_node;
    rs->cur_node = n;
    TagFn fn = (TagFn)n->fn;
    if (!fn) {
        if (!strncmp(n->tag, "cf_", 3)) {
            call_custom_tag(c, n, NULL, NULL, flow);
            rs->cur_node = saved;
            return;
        }
        if (!strncmp(n->tag, "cfx_", 4)) {
            cfx_call(c, n, n->tag);
            rs->cur_node = saved;
            return;
        }
        fn = tag_lookup(n->tag);
        if (!fn) {
            if (!strcmp(n->tag, "cfelse") || !strcmp(n->tag, "cfelseif"))
                kf_throw(c, "Template", kprintf("Context validation error for tag %s.", kf_upper(n->tag)),
                         "The tag must be nested inside a CFIF tag.");
            kf_throw(c, "Template", kprintf("Unknown tag &lt;%s&gt;.", kf_upper(n->tag)),
                     kprintf("KoldFusion cannot determine how to process the tag &lt;%s&gt;. The tag name may be misspelled.",
                             kf_upper(n->tag)));
        }
        n->fn = (void *)fn;
    }
    check_timeout(c);
    if (rs->strict_attrs) strict_check(c, n);
    fn(c, n, flow);
    rs->cur_node = saved;
}

static void out_expr_value(Ctx *c, Node *n) {
    Val v = eval(c, n->expr);
    const char *s;
    size_t len;
    if (v.t == VT_STR) { s = v.u.str.s; len = v.u.str.len; }
    else { s = val_simple_str(c, v, n->expr); len = strlen(s); }
    /* Inside CFQUERY single quotes are doubled, except in the results of the
     * functions whose job is to build SQL (PreserveSingleQuotes, QuotedValueList,
     * ListQualify, CreateODBC*) and in ODBC date/time values held in variables */
    static const char *SQLFN[] = {"PreserveSingleQuotes", "QuotedValueList", "ListQualify", "CreateODBCDate",
                                  "CreateODBCTime", "CreateODBCDateTime", NULL};
    int sqlfn = 0;
    if (n->expr->k == E_CALL)
        for (int i = 0; SQLFN[i]; i++) if (!kf_stricmp(n->expr->name, SQLFN[i])) sqlfn = 1;
    int is_odbc_dt = len > 4 && s[0] == '{' && (s[1] == 'd' || s[1] == 't' || s[1] == 'D' || s[1] == 'T') && s[len - 1] == '}';
    if (c->sql_mode && !sqlfn && !is_odbc_dt && v.t != VT_DATE) {
        /* ColdFusion escapes single quotes in variables inside CFQUERY */
        if (memchr(s, '\'', len)) {
            Buf b; buf_init(&b);
            for (size_t i = 0; i < len; i++) { if (s[i] == '\'') buf_putc(&b, '\''); buf_putc(&b, s[i]); }
            out_put(c, b.s, b.len);
            return;
        }
    }
    out_put(c, s, len);
}

void exec_nodes(Ctx *c, Node **kids, int n, int *flow) {
    RState *rs = c->rs;
    *flow = FL_OK;
    for (int i = 0; i < n; i++) {
        Node *k = kids[i];
        switch (k->k) {
        case N_TEXT:
            if (rs->enablecfoutputonly > 0 && !c->in_output && !c->sql_mode) break;
            out_put(c, k->text, k->len);
            break;
        case N_EXPR: {
            if (!c->in_output && !c->sql_mode) {
                /* # outside of CFOUTPUT is literal; only happens for mail/query bodies */
                out_put(c, k->rawsrc, k->rawlen);
                break;
            }
            Node *saved = rs->cur_node;
            rs->cur_node = k;
            out_expr_value(c, k);
            rs->cur_node = saved;
            break;
        }
        case N_TAG:
            exec_tag(c, k, flow);
            if (*flow) return;
            break;
        default: break;
        }
    }
}

void exec_template(Ctx *c, Template *t) {
    RState *rs = c->rs;
    Template *saved_tpl = rs->cur_tpl;
    Template *saved_ctpl = c->tpl;
    const char *saved_dir = c->tagdir;
    rs->cur_tpl = t;
    c->tpl = t;
    c->tagdir = kf_template_dir(t->path);
    if (++rs->depth > 64)
        kf_throw(c, "Template", "Maximum include depth exceeded.",
                 "Templates may be nested (CFINCLUDE, CFMODULE, custom tags) at most 64 levels deep. Check for recursion.");
    double t0 = kf_time_ms();
    int flow;
    exec_nodes(c, t->root->kids, t->root->nkids, &flow);
    rs->depth--;
    if (rs->detail_view) {
        DebugTpl *d = kmalloc(sizeof(DebugTpl));
        d->path = t->path; d->ms = kf_time_ms() - t0; d->next = rs->dt; rs->dt = d;
    }
    rs->cur_tpl = saved_tpl;
    c->tpl = saved_ctpl;
    c->tagdir = saved_dir;
}

/* ================================================================ error page */
static const char *asctime_now(void) {
    time_t t = time(NULL);
    struct tm tm; localtime_r(&t, &tm);
    char buf[64];
    strftime(buf, sizeof buf, "%a %b %d %H:%M:%S %Y", &tm);
    return kstrdup(buf);
}

static const char *cgi(RState *rs, const char *name) {
    Val *v = struct_get(rs->cgi, name);
    return v ? v_tostr(*v) : "";
}

static void error_body(RState *rs, KfError *e, Buf *b) {
    int show_path = rs->show_tpl_path;
    const char *tpl = e->tplpath ? e->tplpath : "";
    if (e->heading) {
        buf_printf(b, "<P>%s\n", e->heading);
        if (e->snippet) buf_printf(b, "<P><PRE>%s</PRE>\n", kf_html_escape(e->snippet));
    }
    if (e->line && kf_stricmp(e->type, "Database")) buf_printf(b, "<P>Error near line %d, column %d.\n", e->line, e->col);
    buf_puts(b, "<HR>\n");
    if (!kf_stricmp(e->type, "Database")) {
        buf_printf(b, "<P>ODBC Error Code = %s<P>%s\n", e->sqlstate ? e->sqlstate : "S1000 (General error)", e->message);
        if (*e->detail) buf_printf(b, "<P>%s\n", e->detail);
        if (rs->show_sql) {
            if (e->sql) buf_printf(b, "<P><P>SQL = \"%s\"\n", kf_html_escape(e->sql));
            if (e->datasource) buf_printf(b, "<P>Data Source = \"%s\"\n", kf_html_escape(kf_upper(e->datasource)));
        }
    } else if (e->custom.t != VT_NULL || (!kf_stricmp(e->type, "Application") && e->errorcode)) {
        buf_printf(b, "<P>%s\n", e->message);
        if (*e->detail) buf_printf(b, "<P>%s\n", e->detail);
    } else {
        buf_printf(b, "<P>%s\n", e->message);
        if (*e->detail) buf_printf(b, "<P>%s\n", e->detail);
    }
    if (e->tagname && e->line) {
        buf_printf(b, "<P>The error occurred while processing an element with a general identifier of (%s), "
                      "occupying document position (%d:%d) to (%d:%d)",
                   kf_html_escape(e->tagname), e->line, e->col,
                   rs->cur_node && rs->cur_node->eline ? rs->cur_node->eline : e->line,
                   rs->cur_node && rs->cur_node->eline ? rs->cur_node->ecol : e->col + 1);
        if (show_path) buf_printf(b, " in the template file %s", kf_html_escape(tpl));
        buf_puts(b, ".\n");
    } else if (show_path && *tpl) {
        buf_printf(b, "<P>The error occurred in the template file %s.\n", kf_html_escape(tpl));
    }
    buf_printf(b, "<P>Date/Time: %s<BR>\nBrowser: %s<BR>\nRemote Address: %s<BR>\nHTTP Referer: %s<BR>\n",
               asctime_now(), kf_html_escape(cgi(rs, "HTTP_USER_AGENT")), kf_html_escape(cgi(rs, "REMOTE_ADDR")),
               kf_html_escape(cgi(rs, "HTTP_REFERER")));
    if (show_path) buf_printf(b, "Template: %s<BR>\n", kf_html_escape(cgi(rs, "CF_TEMPLATE_PATH")));
    buf_printf(b, "Query String: %s<BR>\n", kf_html_escape(cgi(rs, "QUERY_STRING")));
    char *admin = cfg(REG_SERVER, "AdminEmail", "");
    if (admin && *admin)
        buf_printf(b, "<P>Please inform the site administrator that this error has occurred (be sure to include the contents "
                      "of this page in your message to the administrator). <A HREF=\"mailto:%s\">%s</A>\n", admin, admin);
}

void render_error_page(RState *rs, KfError *e) {
    Buf b; buf_init(&b);
    if (rs->status == 200) rs->status = 500, rs->status_text = "Internal Server Error";
    buf_puts(&b, "\n<!-- \" ---></TD></TD></TD></TH></TH></TH></TR></TR></TR></TABLE></TABLE></TABLE></A></ABBREV></ACRONYM></ADDRESS></APPLET></AU></B></BANNER></BIG></BLINK></BLOCKQUOTE></BQ></CAPTION></CENTER></CITE></CODE></COMMENT></DEL></DFN></DIR></DIV></DL></EM></FIG></FN></FONT></FORM></FRAME></FRAMESET></H1></H2></H3></H4></H5></H6></HEAD></I></INS></KBD></LISTING></MAP></MARQUEE></MENU></MULTICOL></NOBR></NOFRAMES></NOSCRIPT></NOTE></OL></P></PARAM></PERSON></PLAINTEXT></PRE></Q></S></SAMP></SCRIPT></SELECT></SMALL></STRIKE></STRONG></SUB></SUP></TABLE></TD></TEXTAREA></TH></TITLE></TR></TT></U></UL></VAR></WBR></XMP>\n");
    buf_puts(&b, "<FONT FACE=\"Arial, Helvetica\" SIZE=\"2\" COLOR=\"#000000\">\n");
    buf_puts(&b, "<P><FONT SIZE=\"+1\"><B>Error Diagnostic Information</B></FONT>\n");
    error_body(rs, e, &b);
    buf_puts(&b, "</FONT>\n");
    buf_put(&rs->page, b.s, b.len);
}

static char *error_log_line(RState *rs, KfError *e) {
    Buf b; buf_init(&b);
    buf_printf(&b, "%s", e->message);
    if (*e->detail) buf_printf(&b, " %s", e->detail);
    if (e->tagname && e->line)
        buf_printf(&b, " The error occurred while processing an element with a general identifier of (%s), "
                       "occupying document position (%d:%d) to (%d:%d) in the template file %s.",
                   e->tagname, e->line, e->col, e->line, e->col + 1, e->tplpath ? e->tplpath : "");
    buf_printf(&b, " Date/Time: %s Browser: %s Remote Address: %s HTTP Referer: %s",
               asctime_now(), cgi(rs, "HTTP_USER_AGENT"), cgi(rs, "REMOTE_ADDR"), cgi(rs, "HTTP_REFERER"));
    /* strip tags for the log */
    char *s = buf_cstr(&b), *o = s;
    int intag = 0;
    for (char *p = s; *p; p++) {
        if (*p == '<') { intag = 1; continue; }
        if (*p == '>' && intag) { intag = 0; continue; }
        if (!intag) *o++ = *p;
    }
    *o = 0;
    return s;
}

/* ================================================================ debug */
static int ip_allowed_for_debug(RState *rs) {
    char *ips = cfg("Debug", "DebugIPs", "");
    if (!ips || !*ips) return 1;
    const char *ra = cgi(rs, "REMOTE_ADDR");
    char *list = kstrdup(ips);
    for (char *t = strtok(list, ","); t; t = strtok(NULL, ",")) {
        t = kf_trim(t);
        if (!strcmp(t, ra)) return 1;
    }
    return 0;
}

static void debug_scope(Buf *b, const char *title, Struct *s) {
    buf_printf(b, "<P><I>%s</I><BR>\n", title);
    if (!s) return;
    for (int i = 0; i < s->n; i++) {
        Val v = s->e[i].v;
        buf_printf(b, "%s=%s<BR>\n", kf_html_escape(kf_upper(s->e[i].key)),
                   v_is_simple(v) ? kf_html_escape(v_tostr(v)) : kprintf("[%s]", v_typename(v)));
    }
}

void render_debug(RState *rs, Ctx *c) {
    (void)c;
    if (!rs->show_debug || rs->debug_override == 0 || !ip_allowed_for_debug(rs)) return;
    if (!rs->show_query_info && !rs->show_proc_time && !rs->show_vars) return;
    if (rs->content_type && !kf_strnicmp(rs->content_type, "text/html", 9) == 0 &&
        kf_strnicmp(rs->content_type, "text/html", 9)) return;
    Buf *b = &rs->page;
    buf_puts(b, "\n<!-- KoldFusion debug output -->\n<HR NOSHADE SIZE=\"1\">\n<FONT FACE=\"Arial, Helvetica\" SIZE=\"1\" COLOR=\"#000000\">\n");
    if (rs->show_query_info) {
        buf_puts(b, "<P><B>Queries</B>\n");
        /* list is newest-first; print in execution order */
        int n = 0; for (DebugQuery *d = rs->dq; d; d = d->next) n++;
        DebugQuery **arr = kmalloc(sizeof(DebugQuery *) * (n ? n : 1));
        int i = 0; for (DebugQuery *d = rs->dq; d; d = d->next) arr[i++] = d;
        for (i = 0; i < n; i++) {
            DebugQuery *d = arr[i];
            buf_printf(b, "<P><I>%s</I> (Records=%d, Time=%.0fms)<BR>\nSQL = <BR>\n%s\n",
                       kf_html_escape(d->name ? d->name : ""), d->records, d->ms, kf_html_escape(d->sql ? d->sql : ""));
        }
    }
    if (rs->show_proc_time) {
        buf_printf(b, "<P><B>Execution Time</B><P>%.0f milliseconds\n", kf_time_ms() - rs->start_ms);
        if (rs->detail_view && rs->dt) {
            buf_puts(b, "<BR>\n");
            for (DebugTpl *d = rs->dt; d; d = d->next)
                buf_printf(b, "%.0f ms %s<BR>\n", d->ms, kf_html_escape(d->path));
        }
    }
    if (rs->show_vars) {
        buf_puts(b, "<P><B>Parameters</B>\n");
        debug_scope(b, "URL Parameters", rs->url);
        debug_scope(b, "Form Fields", rs->form);
        if (rs->client_enabled) debug_scope(b, "Client Variables", rs->client);
        debug_scope(b, "Cookie Variables", rs->cookie);
        debug_scope(b, "CGI Variables", rs->cgi);
    }
    buf_puts(b, "</FONT>\n");
}

/* ================================================================ request */
static const char *find_up(const char *dir, const char *name) {
    /* walk from dir up to (and including) the web root */
    char *d = kstrdup(dir);
    size_t rootlen = strlen(G.webroot);
    for (;;) {
        char *p = kf_path_join(d, name);
        if (access(p, R_OK) == 0) return p;
        /* case-insensitive variants */
        char *lp = kf_path_join(d, kf_lower(name));
        if (access(lp, R_OK) == 0) return lp;
        size_t n = strlen(d);
        while (n > 1 && d[n - 1] == '/') d[--n] = 0;
        if (n <= rootlen) break;
        char *sl = strrchr(d, '/');
        if (!sl || sl == d) break;
        sl[1] = 0;
    }
    return NULL;
}

static void run_file(Ctx *c, const char *path) {
    KfError *err;
    Template *t = template_get(c->rs, path, &err);
    if (!t) {
        if (err) kf_throw_err(c->rs, err);
        return;
    }
    exec_template(c, t);
}

static int handle_with_cferror(RState *rs, Ctx *c, KfError *e) {
    if (rs->in_error_handler || !rs->cferror) return 0;
    Val *h = struct_get(rs->cferror, "exception");
    int is_request = 0;
    if (!h) { h = struct_get(rs->cferror, "request"); is_request = 1; }
    if (!h || h->t != VT_STRUCT) return 0;
    const char *tpl = v_tostr(*struct_get(h->u.st, "template"));
    const char *mailto = struct_get(h->u.st, "mailto") ? v_tostr(*struct_get(h->u.st, "mailto")) : "";
    Struct *err = struct_new();
    Buf diag; buf_init(&diag);
    Buf saved = rs->page;
    buf_init(&rs->page);
    error_body(rs, e, &diag);
    rs->page = saved;
    struct_set(err, "Diagnostics", v_str(buf_cstr(&diag)));
    struct_set(err, "DateTime", v_str(asctime_now()));
    struct_set(err, "Browser", v_strdup(cgi(rs, "HTTP_USER_AGENT")));
    struct_set(err, "RemoteAddress", v_strdup(cgi(rs, "REMOTE_ADDR")));
    struct_set(err, "HTTPReferer", v_strdup(cgi(rs, "HTTP_REFERER")));
    struct_set(err, "Template", v_strdup(cgi(rs, "CF_TEMPLATE_PATH")));
    struct_set(err, "QueryString", v_strdup(cgi(rs, "QUERY_STRING")));
    struct_set(err, "MailTo", v_strdup(mailto));
    struct_set(err, "Type", v_strdup(e->type));
    struct_set(err, "Message", v_strdup(e->message));
    struct_set(err, "Detail", v_strdup(e->detail));
    if (is_request) {
        /* REQUEST handlers may only use Error.* variables, substituted textually */
        size_t len;
        char *src = kf_read_file(tpl, &len);
        if (!src) return 0;
        Buf out; buf_init(&out);
        for (char *p = src; *p; ) {
            if (*p == '#' && !kf_strnicmp(p + 1, "error.", 6)) {
                char *end = strchr(p + 1, '#');
                if (end) {
                    char *name = kstrndup(p + 7, end - p - 7);
                    Val *v = struct_get(err, name);
                    buf_puts(&out, v ? v_tostr(*v) : "");
                    p = end + 1;
                    continue;
                }
            }
            buf_putc(&out, *p++);
        }
        free(src);
        rs->page.len = 0;
        buf_put(&rs->page, out.s, out.len);
        return 1;
    }
    rs->in_error_handler = 1;
    JmpFrame jf; jf.prev = rs->jf; rs->jf = &jf;
    if (setjmp(jf.jb) == 0) {
        Ctx *ec = ctx_new(rs, NULL);
        ec->variables = c->variables;
        struct_set(ec->variables, "Error", v_struct(err));
        rs->page.len = 0;
        rs->out = &rs->page;
        run_file(ec, tpl);
        rs->jf = jf.prev;
        return 1;
    }
    rs->jf = jf.prev;
    return 0;
}

int run_request(RState *rs, const char *tplpath) {
    t_rs = rs;
    rs->out = &rs->page;
    rs->base_template = tplpath;
    rs->debug_override = -1;
    Ctx *c = ctx_new(rs, NULL);
    c->tagdir = kf_template_dir(tplpath);
    int status = 0;

    JmpFrame jf; jf.prev = NULL; rs->jf = &jf;
    if (setjmp(jf.jb) == 0) {
        const char *app = find_up(kf_template_dir(tplpath), "Application.cfm");
        if (app) run_file(c, app);
        if (rs->validation_errors) {
            const char *hdr = "<H3>Form Entries Incomplete or Invalid</H3>";
            const char *list = kprintf("<UL>\n%s</UL>\n", rs->validation_errors);
            const char *ftr = "<P>Go <A HREF=\"javascript:history.back()\">back</A> and correct the problem.";
            Val *h = rs->cferror ? struct_get(rs->cferror, "validation") : NULL;
            size_t len;
            char *src = h && h->t == VT_STRUCT ? kf_read_file(v_tostr(*struct_get(h->u.st, "template")), &len) : NULL;
            rs->page.len = 0;
            if (src) {
                /* like TYPE="Request": only Error.* variables, substituted textually */
                Buf out; buf_init(&out);
                for (char *p = src; *p; ) {
                    if (*p == '#' && !kf_strnicmp(p + 1, "error.", 6)) {
                        char *e2 = strchr(p + 1, '#');
                        if (e2) {
                            char *nm = kstrndup(p + 7, e2 - p - 7);
                            if (!kf_stricmp(nm, "InvalidFields")) buf_puts(&out, list);
                            else if (!kf_stricmp(nm, "ValidationHeader")) buf_puts(&out, hdr);
                            else if (!kf_stricmp(nm, "ValidationFooter")) buf_puts(&out, ftr);
                            else if (!kf_stricmp(nm, "MailTo")) buf_puts(&out, v_tostr(*struct_get(h->u.st, "mailto")));
                            p = e2 + 1;
                            continue;
                        }
                    }
                    buf_putc(&out, *p++);
                }
                free(src);
                buf_put(&rs->page, out.s, out.len);
            } else {
                buf_printf(&rs->page, "<HTML><HEAD><TITLE>Form Entries Incomplete or Invalid</TITLE></HEAD>\n<BODY BGCOLOR=\"#FFFFFF\">\n"
                                      "<FONT FACE=\"Arial, Helvetica\" SIZE=\"2\">%s\n%s%s\n</FONT></BODY></HTML>\n", hdr, list, ftr);
            }
            rs->debug_override = 0;
            KfError *ab = kf_error_new("__abort", "", "");
            kf_throw_err(rs, ab);
        }
        KfError *err;
        Template *t = template_get(rs, tplpath, &err);
        if (!t) {
            if (err) kf_throw_err(rs, err);
            rs->status = 404; rs->status_text = "Not Found";
            KfError *e = kf_error_new("MissingInclude", "File not found.",
                kprintf("The requested template %s could not be found.", kf_html_escape(cgi(rs, "SCRIPT_NAME"))));
            e->extended = kstrdup(tplpath);
            kf_throw_err(rs, e);
        }
        exec_template(c, t);
        if (app) {
            const char *end = kf_path_join(kf_template_dir(app), "OnRequestEnd.cfm");
            if (access(end, R_OK) == 0) run_file(c, end);
        }
    } else {
        KfError *e = rs->err;
        rs->err = NULL;
        if (e && !strcmp(e->type, "__abort")) {
            /* CFABORT / CFLOCATION: normal termination */
        } else if (e) {
            status = 1;
            rs->out = &rs->page;
            kf_log("application.log", "Error", "%s", error_log_line(rs, e));
            int handled = 0;
            JmpFrame hf; hf.prev = NULL; rs->jf = &hf;
            if (setjmp(hf.jb) == 0) {
                handled = handle_with_cferror(rs, c, e);
                if (!handled) {
                    char *site = cfg(REG_SERVER, "SiteWideErrorHandler", "");
                    if (site && *site && !rs->in_error_handler) {
                        Ctx tmp = *c;
                        tmp.tagdir = G.webroot;
                        const char *p = resolve_template_path(&tmp, site, 0);
                        if (!rs->cferror) rs->cferror = struct_new();
                        Struct *h = struct_new();
                        struct_set(h, "template", v_strdup(p));
                        struct_set(rs->cferror, "exception", v_struct(h));
                        handled = handle_with_cferror(rs, c, e);
                    }
                }
            } else handled = 0;
            rs->jf = &jf;
            if (!handled) render_error_page(rs, e);
        }
    }
    rs->jf = NULL;
    rs->out = &rs->page;
    if (rs->cache_file && !status && !rs->location && !rs->content_file) {
        Buf cf; buf_init(&cf);
        buf_printf(&cf, "<!-- KFCACHE %s -->\n", rs->cache_key);
        buf_put(&cf, rs->page.s ? rs->page.s : "", rs->page.len);
        kf_write_file(rs->cache_file, cf.s, cf.len, 0);
    }
    if (!rs->location && !rs->content_file) render_debug(rs, c);
    return status;
}
