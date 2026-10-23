/*
 * parse.c - CFML template parser
 *
 * Builds a tree of Nodes from template source. CFML comments <!--- ---> nest
 * and are dropped. Inside CFOUTPUT / CFMAIL / CFQUERY bodies, text is split
 * into literal text and #expression# nodes; elsewhere # is just a character.
 */
#define _GNU_SOURCE
#include "engine.h"
#include <stdlib.h>
#include <ctype.h>

extern __thread const char *t_parse_base;
extern __thread int t_parse_base_len;
Expr *expr_parse_strlit(const char *src, int *pos, int len, const char **err);

/* incremental line/column lookup: cache the last answer */
static __thread const char *lc_src;
static __thread size_t lc_off;
static __thread int lc_line, lc_col;
void parse_thread_reset(void) { lc_src = NULL; lc_off = 0; }   /* the cached source may be freed memory now */

void pos_to_linecol(const char *src, size_t off, int *line, int *col) {
    size_t i = 0; int l = 1, c = 1;
    if (lc_src == src && off >= lc_off) { i = lc_off; l = lc_line; c = lc_col; }
    for (; i < off && src[i]; i++) {
        if (src[i] == '\n') { l++; c = 1; } else c++;
    }
    lc_src = src; lc_off = i; lc_line = l; lc_col = c;
    *line = l; *col = c;
}

typedef struct PS {
    Template *t;
    const char *s;
    int len;
    int pos;
    Node *stack[256];
    int sp;
    KfError *err;
} PS;

static Node *new_node(PS *ps, NKind k, int off) {
    Node *n = kmalloc(sizeof(Node));
    n->k = k;
    n->tpl = ps->t;
    pos_to_linecol(ps->s, off, &n->line, &n->col);
    return n;
}

static void add_kid(Node *parent, Node *kid) {
    if (parent->nkids == parent->kcap) {
        int nc = parent->kcap ? parent->kcap * 2 : 8;
        Node **nk = kmalloc(sizeof(Node *) * nc);
        if (parent->nkids) memcpy(nk, parent->kids, sizeof(Node *) * parent->nkids);
        parent->kids = nk; parent->kcap = nc;
    }
    parent->kids[parent->nkids++] = kid;
}

static void perr(PS *ps, int off, const char *heading, const char *msg, const char *detail) {
    if (ps->err) return;
    KfError *e = kf_error_new("Template", msg, detail);
    e->heading = heading;
    e->tplpath = ps->t->path;
    pos_to_linecol(ps->s, off, &e->line, &e->col);
    ps->err = e;
}

static void parse_construct_error(PS *ps, int off, const char *why) {
    int line, col;
    pos_to_linecol(ps->s, off, &line, &col);
    int n = 0;
    while (off + n < ps->len && n < 60 && ps->s[off + n] != '\n') n++;
    perr(ps, off, "Just in time compilation error",
         kprintf("Invalid parser construct found on line %d at position %d. KoldFusion was looking at the following text:"
                 "<P>%s<P>%s", line, col, kf_html_escape(kstrndup(ps->s + off, n ? n : 1)), why ? why : ""),
         "");
}

static int in_output_context(PS *ps) {
    for (int i = ps->sp; i >= 1; i--) {
        const char *t = ps->stack[i]->tag;
        if (!strcmp(t, "cfoutput") || !strcmp(t, "cfmail") || !strcmp(t, "cfquery")) return 1;
    }
    return 0;
}

static void add_text(PS *ps, int start, int end) {
    if (end <= start) return;
    Node *top = ps->stack[ps->sp];
    if (!in_output_context(ps)) {
        Node *n = new_node(ps, N_TEXT, start);
        n->text = ps->s + start; n->len = end - start;
        add_kid(top, n);
        return;
    }
    /* split on #expr# */
    int i = start, seg = start;
    Buf lit; buf_init(&lit);
    while (i < end) {
        if (ps->s[i] != '#') { i++; continue; }
        if (i + 1 < end && ps->s[i + 1] == '#') {
            buf_put(&lit, ps->s + seg, i - seg + 1);
            i += 2; seg = i;
            continue;
        }
        buf_put(&lit, ps->s + seg, i - seg);
        if (lit.len) {
            Node *n = new_node(ps, N_TEXT, seg);
            n->text = lit.s; n->len = lit.len;
            add_kid(top, n);
            buf_init(&lit);
        }
        int epos = i + 1;
        const char *err = NULL;
        Expr *e = expr_parse(ps->s, &epos, end, 0, 0, 0, &err, 1);
        if (!e || epos >= end || ps->s[epos] != '#') {
            parse_construct_error(ps, e ? epos : (epos > i ? epos : i),
                                  err ? err : "Invalid expression format. The usual cause is an error in the expression structure.");
            return;
        }
        Node *n = new_node(ps, N_EXPR, i);
        n->expr = e;
        n->rawsrc = ps->s + i; n->rawlen = epos - i + 1;
        add_kid(top, n);
        i = epos + 1; seg = i;
    }
    buf_put(&lit, ps->s + seg, end - seg);
    if (lit.len) {
        Node *n = new_node(ps, N_TEXT, seg);
        n->text = lit.s; n->len = lit.len;
        add_kid(top, n);
    }
}

static int is_tag_start(PS *ps, int i, int *closing) {
    const char *s = ps->s + i;
    int rem = ps->len - i;
    if (rem < 4 || s[0] != '<') return 0;
    int o = 1;
    *closing = 0;
    if (s[1] == '/') { o = 2; *closing = 1; }
    if (rem < o + 3) return 0;
    if (tolower((unsigned char)s[o]) != 'c' || tolower((unsigned char)s[o + 1]) != 'f') return 0;
    return kf_is_ident_char((unsigned char)s[o + 2]);
}

static void skip_ws(PS *ps) { while (ps->pos < ps->len && isspace((unsigned char)ps->s[ps->pos])) ps->pos++; }

/* the rest of a tag after its name: attributes or an expression */
static int parse_tag_body(PS *ps, Node *n) {
    const char *tag = n->tag;
    if (!strcmp(tag, "cfset") || !strcmp(tag, "cfif") || !strcmp(tag, "cfelseif")) {
        skip_ws(ps);
        const char *err = NULL;
        int epos = ps->pos;
        Expr *e = expr_parse(ps->s, &epos, ps->len, !strcmp(tag, "cfset") ? 4 : 0, 0, 0, &err, 0);
        if (!e) { parse_construct_error(ps, epos, err); return 0; }
        n->expr = e;
        ps->pos = epos;
        skip_ws(ps);
        if (ps->pos < ps->len && ps->s[ps->pos] == '/' && ps->pos + 1 < ps->len && ps->s[ps->pos + 1] == '>') {
            ps->pos += 2; n->selfclose = 1; return 1;
        }
        if (ps->pos >= ps->len || ps->s[ps->pos] != '>') {
            parse_construct_error(ps, ps->pos, "Invalid expression format. The usual cause is an error in the expression structure.");
            return 0;
        }
        ps->pos++;
        return 1;
    }
    Attr attrs[128]; int na = 0;
    for (;;) {
        skip_ws(ps);
        if (ps->pos >= ps->len) { perr(ps, ps->pos, "Just in time compilation error",
                                      kprintf("Missing closing &gt; for tag %s.", kf_upper(tag)), ""); return 0; }
        char c = ps->s[ps->pos];
        if (c == '>') { ps->pos++; break; }
        if (c == '/' && ps->pos + 1 < ps->len && ps->s[ps->pos + 1] == '>') { ps->pos += 2; n->selfclose = 1; break; }
        int ns = ps->pos;
        while (ps->pos < ps->len && (kf_is_ident_char((unsigned char)ps->s[ps->pos]) || ps->s[ps->pos] == '-' ||
                                     ps->s[ps->pos] == ':' || ps->s[ps->pos] == '.'))
            ps->pos++;
        if (ps->pos == ns) {
            parse_construct_error(ps, ps->pos, kprintf("Invalid attribute in tag %s.", kf_upper(tag)));
            return 0;
        }
        Attr *a = &attrs[na < 127 ? na++ : na];
        a->name = kf_lower(kstrndup(ps->s + ns, ps->pos - ns));
        skip_ws(ps);
        if (ps->pos < ps->len && ps->s[ps->pos] == '=') {
            ps->pos++;
            skip_ws(ps);
            if (ps->pos < ps->len && (ps->s[ps->pos] == '"' || ps->s[ps->pos] == '\'')) {
                const char *err = NULL;
                int vs = ps->pos;
                Expr *e = expr_parse_strlit(ps->s, &ps->pos, ps->len, &err);
                if (!e) { parse_construct_error(ps, ps->pos, err); return 0; }
                a->val = e;
                a->raw = kstrndup(ps->s + vs + 1, ps->pos - vs - 2 > 0 ? ps->pos - vs - 2 : 0);
            } else {
                int vs = ps->pos;
                while (ps->pos < ps->len && !isspace((unsigned char)ps->s[ps->pos]) && ps->s[ps->pos] != '>') {
                    if (ps->s[ps->pos] == '/' && ps->pos + 1 < ps->len && ps->s[ps->pos + 1] == '>') break;
                    ps->pos++;
                }
                const char *raw = kstrndup(ps->s + vs, ps->pos - vs);
                a->raw = raw;
                if (strchr(raw, '#')) {
                    const char *q = kprintf("\"%s\"", raw);
                    int qp = 0; const char *err = NULL;
                    const char *saved = t_parse_base; t_parse_base = NULL;
                    a->val = expr_parse_strlit(q, &qp, (int)strlen(q), &err);
                    t_parse_base = saved;
                    if (!a->val) { parse_construct_error(ps, vs, err); return 0; }
                } else {
                    Expr *e = kmalloc(sizeof(Expr));
                    e->k = E_LIT; e->lit = v_str(raw);
                    a->val = e;
                }
            }
        } else {
            Expr *e = kmalloc(sizeof(Expr));
            e->k = E_LIT; e->lit = v_str("");
            a->val = e; a->raw = "";
        }
    }
    n->nattrs = na;
    n->attrs = kmalloc(sizeof(Attr) * (na ? na : 1));
    memcpy(n->attrs, attrs, sizeof(Attr) * na);
    return 1;
}

static const char *find_nocase(const char *s, int from, int len, const char *needle) {
    size_t nl = strlen(needle);
    for (int i = from; i + (int)nl <= len; i++)
        if (!kf_strnicmp(s + i, needle, nl)) return s + i;
    return NULL;
}

static void flatten_unclosed(PS *ps, int idx) {
    /* stack[idx] had no end tag: hoist its children to be its following siblings */
    Node *n = ps->stack[idx];
    Node *parent = ps->stack[idx - 1];
    Node **kids = n->kids; int nk = n->nkids;
    n->kids = NULL; n->nkids = n->kcap = 0;
    for (int i = 0; i < nk; i++) add_kid(parent, kids[i]);
}

static void context_error(PS *ps, Node *n) {
    char *T = kf_upper(n->tag);
    int line = n->line, col = n->col;
    perr(ps, 0, "Just in time compilation error",
         kprintf("Context validation error for tag %s.", T),
         kprintf("The start tag must have a matching end tag. An explicit end tag can be provided by adding &lt;/%s&gt;. "
                 "If the body of the tag is empty you can use the shortcut &lt;%s .../&gt;. "
                 "The error occurred while processing an element with a general identifier of (%s), "
                 "occupying document position (%d:%d).", T, T, T, line, col));
    if (ps->err) { ps->err->line = line; ps->err->col = col; }
}

Template *template_parse(const char *path, char *src, size_t len, Arena *a, KfError **perr_out) {
    Arena *saved = g_arena;
    g_arena = a;
    const char *saved_base = t_parse_base; int saved_len = t_parse_base_len;
    t_parse_base = src; t_parse_base_len = (int)len;

    Template *t = kmalloc(sizeof(Template));
    t->path = kstrdup(path);
    t->src = src; t->srclen = len;
    t->arena = a;

    PS ps; memset(&ps, 0, sizeof ps);
    ps.t = t; ps.s = src; ps.len = (int)len;
    Node *root = new_node(&ps, N_TAG, 0);
    root->tag = "#root";
    ps.stack[0] = root; ps.sp = 0;
    t->root = root;

    int text_start = 0;
    while (ps.pos < ps.len && !ps.err) {
        const char *s = ps.s;
        int i = ps.pos;
        if (s[i] != '<') {
            const char *nx = memchr(s + i, '<', ps.len - i);
            ps.pos = nx ? (int)(nx - s) : ps.len;
            continue;
        }
        /* CFML comment */
        if (i + 4 < ps.len && !strncmp(s + i, "<!---", 5)) {
            add_text(&ps, text_start, i);
            int depth = 1, j = i + 5;
            while (j < ps.len && depth) {
                if (!strncmp(s + j, "<!---", 5)) { depth++; j += 5; }
                else if (!strncmp(s + j, "--->", 4)) { depth--; j += 4; }
                else j++;
            }
            if (depth) { perr(&ps, i, "Just in time compilation error", "Unterminated CFML comment.",
                              "A CFML comment beginning with &lt;!--- was not closed with ---&gt;."); break; }
            ps.pos = text_start = j;
            continue;
        }
        int closing;
        if (!is_tag_start(&ps, i, &closing)) { ps.pos++; continue; }
        add_text(&ps, text_start, i);
        if (ps.err) break;
        int ns = i + (closing ? 2 : 1);
        int ne = ns;
        while (ne < ps.len && kf_is_ident_char((unsigned char)s[ne])) ne++;
        char *name = kf_lower(kstrndup(s + ns, ne - ns));
        ps.pos = ne;
        if (closing) {
            skip_ws(&ps);
            if (ps.pos < ps.len && s[ps.pos] == '>') ps.pos++;
            int found = -1;
            for (int k = ps.sp; k >= 1; k--) if (!strcmp(ps.stack[k]->tag, name)) { found = k; break; }
            if (found < 0) {
                if (tag_is_paired(name) == 2) {
                    perr(&ps, i, "Just in time compilation error",
                         kprintf("Context validation error for tag %s.", kf_upper(name)),
                         kprintf("The end tag &lt;/%s&gt; encountered on line %d at column %d requires a matching start tag.",
                                 kf_upper(name), 0, 0));
                    pos_to_linecol(ps.s, i, &ps.err->line, &ps.err->col);
                    ps.err->detail = kprintf("The end tag &lt;/%s&gt; encountered on line %d at column %d requires a matching start tag.",
                                             kf_upper(name), ps.err->line, ps.err->col);
                }
                text_start = ps.pos;
                continue;
            }
            for (int k = ps.sp; k > found; k--) {
                if (tag_is_paired(ps.stack[k]->tag) == 2) { context_error(&ps, ps.stack[k]); break; }
                flatten_unclosed(&ps, k);
            }
            if (ps.err) break;
            Node *n = ps.stack[found];
            n->has_end = 1;
            pos_to_linecol(ps.s, ps.pos, &n->eline, &n->ecol);
            ps.sp = found - 1;
            text_start = ps.pos;
            continue;
        }
        Node *n = new_node(&ps, N_TAG, i);
        n->tag = name;
        if (!parse_tag_body(&ps, n)) break;
        n->rawsrc = s + i; n->rawlen = ps.pos - i;
        pos_to_linecol(ps.s, ps.pos, &n->eline, &n->ecol);
        add_kid(ps.stack[ps.sp], n);
        text_start = ps.pos;
        if (!strcmp(name, "cfscript") && !n->selfclose) {
            const char *endp = find_nocase(s, ps.pos, ps.len, "</cfscript>");
            if (!endp) { context_error(&ps, n); break; }
            int bstart = ps.pos, blen = (int)(endp - s) - ps.pos;
            const char *err = NULL; int eline = 0, ecol = 0;
            int line0, col0;
            pos_to_linecol(ps.s, bstart, &line0, &col0);
            n->script = script_parse(s + bstart, blen, line0, col0, &err, &eline, &ecol);
            if (!n->script) {
                int off = bstart;
                /* locate error position */
                int l = line0, c = col0, k = bstart;
                while (k < bstart + blen && (l < eline || (l == eline && c < ecol))) {
                    if (s[k] == '\n') { l++; c = 1; } else c++;
                    k++;
                }
                off = k;
                parse_construct_error(&ps, off, err);
                break;
            }
            n->has_end = 1;
            ps.pos = (int)(endp - s) + 11;
            text_start = ps.pos;
            continue;
        }
        if (!n->selfclose && tag_is_paired(name) && ps.sp < 255) ps.stack[++ps.sp] = n;
    }
    if (!ps.err) {
        add_text(&ps, text_start, ps.len);
        for (int k = ps.sp; k >= 1 && !ps.err; k--) {
            if (tag_is_paired(ps.stack[k]->tag) == 2) { context_error(&ps, ps.stack[k]); break; }
            flatten_unclosed(&ps, k);
        }
    }
    if (ps.err && !ps.err->tplpath) ps.err->tplpath = t->path;
    t_parse_base = saved_base; t_parse_base_len = saved_len;
    g_arena = saved;
    if (ps.err) {
        /* copy the error into the caller's arena */
        KfError *e = kf_error_new(ps.err->type, ps.err->message, ps.err->detail);
        e->heading = ps.err->heading ? kstrdup(ps.err->heading) : NULL;
        e->tplpath = kstrdup(path);
        e->line = ps.err->line; e->col = ps.err->col;
        *perr_out = e;
        return NULL;
    }
    *perr_out = NULL;
    return t;
}

void template_dump(Node *n, int depth) {
    for (int i = 0; i < n->nkids; i++) {
        Node *k = n->kids[i];
        fprintf(stderr, "%*s", depth * 2, "");
        if (k->k == N_TEXT) fprintf(stderr, "TEXT [%.*s]\n", (int)k->len, k->text);
        else if (k->k == N_EXPR) fprintf(stderr, "EXPR [%.*s]\n", k->rawlen, k->rawsrc);
        else { fprintf(stderr, "TAG %s (%d kids)\n", k->tag, k->nkids); template_dump(k, depth + 1); }
    }
}
