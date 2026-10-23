/*
 * expr.c - CFML expression parser and evaluator
 *
 * Operator precedence (lowest first), as documented for ColdFusion 4.5:
 *   IMP, EQV, XOR, OR, AND, NOT, comparisons (IS/EQ/NEQ/GT/...), &, + -,
 *   MOD, \, * /, ^, unary + -
 */
#define _GNU_SOURCE
#include "engine.h"
#include <stdlib.h>
#include <ctype.h>
#include <math.h>

/* ================================================================ parser */
#define PF_SCRIPT   1
#define PF_STOPHASH 2

typedef struct P {
    const char *s;
    int pos, len;
    int flags;
    const char *err;
    int errpos;
} P;

__thread const char *t_parse_base;     /* template source for line numbers */
__thread int t_parse_base_len;

static Expr *new_expr(P *p, EKind k, int start) {
    Expr *e = kmalloc(sizeof(Expr));
    e->k = k;
    e->src = p->s + start;
    e->srclen = 0;
    if (t_parse_base && p->s >= t_parse_base && p->s + start <= t_parse_base + t_parse_base_len)
        pos_to_linecol(t_parse_base, (size_t)(p->s + start - t_parse_base), &e->line, &e->col);
    return e;
}
static void finish(P *p, Expr *e) { e->srclen = (int)(p->s + p->pos - e->src); if (e->srclen < 0) e->srclen = 0; }

static int ch(P *p) { return p->pos < p->len ? (unsigned char)p->s[p->pos] : 0; }
static int ch_at(P *p, int o) { return p->pos + o < p->len ? (unsigned char)p->s[p->pos + o] : 0; }

static void ws(P *p) {
    for (;;) {
        while (p->pos < p->len && isspace((unsigned char)p->s[p->pos])) p->pos++;
        if (p->flags & PF_SCRIPT) {
            if (ch(p) == '/' && ch_at(p, 1) == '/') {
                while (p->pos < p->len && p->s[p->pos] != '\n') p->pos++;
                continue;
            }
            if (ch(p) == '/' && ch_at(p, 1) == '*') {
                p->pos += 2;
                while (p->pos < p->len && !(p->s[p->pos] == '*' && ch_at(p, 1) == '/')) p->pos++;
                if (p->pos < p->len) p->pos += 2;
                continue;
            }
        }
        break;
    }
}

static void fail(P *p, const char *msg) {
    if (!p->err) { p->err = msg; p->errpos = p->pos; }
}

/* case-insensitive keyword at current position followed by a non-ident char */
static int peek_word(P *p, const char *w) {
    ws(p);
    size_t n = strlen(w);
    if (p->pos + (int)n > p->len) return 0;
    if (kf_strnicmp(p->s + p->pos, w, n)) return 0;
    if (p->pos + (int)n < p->len && kf_is_ident_char((unsigned char)p->s[p->pos + n])) return 0;
    return 1;
}
static int accept_word(P *p, const char *w) {
    if (!peek_word(p, w)) return 0;
    p->pos += (int)strlen(w);
    return 1;
}
/* accept a sequence of words, e.g. "GREATER THAN OR EQUAL TO", all or nothing */
static int accept_words(P *p, const char *words) {
    int save = p->pos;
    char buf[64];
    const char *w = words;
    while (*w) {
        int n = 0;
        while (*w && *w != ' ') buf[n++] = *w++;
        buf[n] = 0;
        while (*w == ' ') w++;
        if (!accept_word(p, buf)) { p->pos = save; return 0; }
    }
    return 1;
}
static int accept_sym(P *p, const char *sym) {
    ws(p);
    size_t n = strlen(sym);
    if (p->pos + (int)n > p->len || strncmp(p->s + p->pos, sym, n)) return 0;
    p->pos += (int)n;
    return 1;
}

static Expr *parse_expr(P *p);
static Expr *parse_unary(P *p);

static Expr *mk_bin(P *p, int op, Expr *a, Expr *b, int start) {
    Expr *e = new_expr(p, E_BIN, start);
    e->op = op; e->a = a; e->b = b;
    e->line = a->line; e->col = a->col;
    finish(p, e);
    return e;
}

static int is_reserved_word(P *p) {
    static const char *kw[] = {"AND","OR","NOT","XOR","EQV","IMP","IS","EQ","NEQ","GT","LT","GTE",
                               "LTE","GE","LE","CONTAINS","MOD","EQUAL","GREATER","LESS","DOES",NULL};
    for (int i = 0; kw[i]; i++) if (peek_word(p, kw[i])) return 1;
    return 0;
}

static Expr *parse_string_lit(P *p) {
    int start = p->pos;
    char q = (char)ch(p);
    p->pos++;
    Expr *e = new_expr(p, E_STRI, start);
    Buf cur; buf_init(&cur);
    Expr *parts[256]; int np = 0;
    int ok = 0;
    while (p->pos < p->len) {
        char c = p->s[p->pos];
        if (c == q) {
            if (ch_at(p, 1) == q) { buf_putc(&cur, q); p->pos += 2; continue; }
            p->pos++; ok = 1; break;
        }
        if (c == '#') {
            if (ch_at(p, 1) == '#') { buf_putc(&cur, '#'); p->pos += 2; continue; }
            /* interpolation */
            if (cur.len) {
                Expr *l = new_expr(p, E_LIT, p->pos); l->lit = v_strn(cur.s, cur.len);
                if (np < 255) parts[np++] = l;
                buf_init(&cur);
            }
            p->pos++;
            int oldflags = p->flags;
            p->flags |= PF_STOPHASH;
            Expr *x = parse_expr(p);
            p->flags = oldflags;
            if (!x) return NULL;
            ws(p);
            if (ch(p) != '#') { fail(p, "Invalid expression: missing closing # in string"); return NULL; }
            p->pos++;
            if (np < 255) parts[np++] = x;
            continue;
        }
        buf_putc(&cur, c);
        p->pos++;
    }
    if (!ok) { p->pos = start; fail(p, "Invalid expression: unterminated string constant"); return NULL; }
    if (np == 0) {
        e->k = E_LIT;
        e->lit = v_strn(cur.s ? cur.s : "", cur.len);
        finish(p, e);
        return e;
    }
    if (cur.len) {
        Expr *l = new_expr(p, E_LIT, p->pos); l->lit = v_strn(cur.s, cur.len);
        parts[np++] = l;
    }
    e->args = kmalloc(sizeof(Expr *) * np);
    memcpy(e->args, parts, sizeof(Expr *) * np);
    e->nargs = np;
    finish(p, e);
    return e;
}

static Expr *parse_postfix(P *p, Expr *e, int start) {
    for (;;) {
        int save = p->pos;
        ws(p);
        if (ch(p) == '.' && !isdigit(ch_at(p, 1))) {
            p->pos++;
            ws(p);
            int s = p->pos;
            if (!kf_is_ident_start(ch(p)) && !isdigit(ch(p))) { fail(p, "Invalid expression: expected a name after '.'"); return NULL; }
            while (kf_is_ident_char(ch(p))) p->pos++;
            Expr *d = new_expr(p, E_DOT, start);
            d->a = e; d->name = kstrndup(p->s + s, p->pos - s);
            d->line = e->line; d->col = e->col;
            int save2 = p->pos;
            ws(p);
            if (ch(p) == '(') {
                /* object.method(...) - only meaningful for COM/Java objects */
                p->pos++;
                Expr *m = new_expr(p, E_CALL, start);
                m->name = kprintf("%s.%s", "__method", d->name);
                m->a = e;
                Expr *args[64]; int na = 0;
                if (!accept_sym(p, ")")) {
                    for (;;) {
                        Expr *a = parse_expr(p);
                        if (!a) return NULL;
                        if (na < 64) args[na++] = a;
                        if (accept_sym(p, ",")) continue;
                        if (accept_sym(p, ")")) break;
                        fail(p, "Invalid expression: expected , or ) in method call");
                        return NULL;
                    }
                }
                m->nargs = na;
                m->args = kmalloc(sizeof(Expr *) * (na ? na : 1));
                memcpy(m->args, args, sizeof(Expr *) * na);
                finish(p, m);
                e = m;
                continue;
            }
            p->pos = save2;
            finish(p, d);
            e = d;
            continue;
        }
        if (ch(p) == '[') {
            p->pos++;
            Expr *idx = parse_expr(p);
            if (!idx) return NULL;
            if (!accept_sym(p, "]")) { fail(p, "Invalid expression: missing ]"); return NULL; }
            Expr *d = new_expr(p, E_INDEX, start);
            d->a = e; d->b = idx;
            d->line = e->line; d->col = e->col;
            finish(p, d);
            e = d;
            continue;
        }
        if ((p->flags & PF_SCRIPT) && (accept_sym(p, "++") || accept_sym(p, "--"))) {
            Expr *d = new_expr(p, E_POSTINC, start);
            d->op = p->s[p->pos - 1] == '+' ? '+' : '-';
            d->a = e;
            finish(p, d);
            e = d;
            continue;
        }
        p->pos = save;
        return e;
    }
}

static Expr *parse_primary(P *p) {
    ws(p);
    int start = p->pos;
    int c = ch(p);
    if (!c) { fail(p, "Invalid expression: unexpected end of expression"); return NULL; }
    if (c == '(') {
        p->pos++;
        Expr *e = parse_expr(p);
        if (!e) return NULL;
        if (!accept_sym(p, ")")) { fail(p, "Invalid expression: missing closing parenthesis"); return NULL; }
        return parse_postfix(p, e, start);
    }
    if (c == '"' || c == '\'') {
        Expr *e = parse_string_lit(p);
        if (!e) return NULL;
        return parse_postfix(p, e, start);
    }
    if (c == '#') {
        /* <cfset x = #y#> style: hashes around an expression are allowed */
        p->pos++;
        int oldflags = p->flags;
        p->flags |= PF_STOPHASH;
        Expr *e = parse_expr(p);
        p->flags = oldflags;
        if (!e) return NULL;
        ws(p);
        if (ch(p) != '#') { fail(p, "Invalid expression: missing closing #"); return NULL; }
        p->pos++;
        return parse_postfix(p, e, start);
    }
    if (isdigit(c) || (c == '.' && isdigit(ch_at(p, 1)))) {
        char *end;
        double d = strtod(p->s + p->pos, &end);
        int n = (int)(end - (p->s + p->pos));
        if (p->pos + n > p->len) n = p->len - p->pos;
        Expr *e = new_expr(p, E_LIT, start);
        /* keep literal text so 007 stays "007" in string context; exponents are evaluated */
        if (memchr(p->s + p->pos, 'e', n) || memchr(p->s + p->pos, 'E', n)) e->lit = v_num(d);
        else e->lit = v_strn(kstrndup(p->s + p->pos, n), n);
        (void)d;
        p->pos += n;
        if (kf_is_ident_start(ch(p))) { fail(p, "Invalid expression: bad number format"); return NULL; }
        finish(p, e);
        return parse_postfix(p, e, start);
    }
    if (kf_is_ident_start(c)) {
        if (is_reserved_word(p)) { fail(p, "Invalid expression: operator where an operand was expected"); return NULL; }
        while (kf_is_ident_char(ch(p))) p->pos++;
        const char *name = kstrndup(p->s + start, p->pos - start);
        int save = p->pos;
        ws(p);
        if (ch(p) == '(') {
            p->pos++;
            Expr *e = new_expr(p, E_CALL, start);
            e->name = name;
            Expr *args[64]; int n = 0;
            ws(p);
            if (!accept_sym(p, ")")) {
                for (;;) {
                    Expr *a = parse_expr(p);
                    if (!a) return NULL;
                    if (n < 64) args[n++] = a;
                    if (accept_sym(p, ",")) continue;
                    if (accept_sym(p, ")")) break;
                    fail(p, "Invalid expression: expected , or ) in function call");
                    return NULL;
                }
            }
            e->nargs = n;
            e->args = kmalloc(sizeof(Expr *) * (n ? n : 1));
            memcpy(e->args, args, sizeof(Expr *) * n);
            finish(p, e);
            return parse_postfix(p, e, start);
        }
        p->pos = save;
        if (!kf_stricmp(name, "true") || !kf_stricmp(name, "false")) {
            Expr *e = new_expr(p, E_LIT, start);
            e->lit = v_str(kf_stricmp(name, "true") ? "false" : "true");
            if (!kf_stricmp(name, "true")) e->lit = v_str("true");
            finish(p, e);
            return e;
        }
        Expr *e = new_expr(p, E_VAR, start);
        e->name = name;
        finish(p, e);
        return parse_postfix(p, e, start);
    }
    fail(p, "Invalid expression format. The usual cause is an error in the expression structure.");
    return NULL;
}

static Expr *parse_unary(P *p) {
    ws(p);
    int start = p->pos;
    if (ch(p) == '-' && ch_at(p, 1) != '-' && ch_at(p, 1) != '=') {
        p->pos++;
        Expr *a = parse_unary(p);
        if (!a) return NULL;
        Expr *e = new_expr(p, E_UN, start); e->op = OP_NEG; e->a = a; finish(p, e);
        return e;
    }
    if (ch(p) == '+' && ch_at(p, 1) != '+' && ch_at(p, 1) != '=') {
        p->pos++;
        Expr *a = parse_unary(p);
        if (!a) return NULL;
        Expr *e = new_expr(p, E_UN, start); e->op = OP_POS; e->a = a; finish(p, e);
        return e;
    }
    if ((p->flags & PF_SCRIPT) && (accept_sym(p, "++") || accept_sym(p, "--"))) {
        int op = p->s[p->pos - 1];
        Expr *a = parse_unary(p);
        if (!a) return NULL;
        Expr *e = new_expr(p, E_PREINC, start); e->op = op; e->a = a; finish(p, e);
        return e;
    }
    return parse_primary(p);
}

static Expr *parse_pow(P *p) {
    int start = p->pos;
    Expr *a = parse_unary(p);
    while (a && accept_sym(p, "^")) {
        Expr *b = parse_unary(p);
        if (!b) return NULL;
        a = mk_bin(p, OP_POW, a, b, start);
    }
    return a;
}
static Expr *parse_muldiv(P *p) {
    int start = p->pos;
    Expr *a = parse_pow(p);
    while (a) {
        ws(p);
        int op = 0;
        if (ch(p) == '*' && ch_at(p, 1) != '=') { p->pos++; op = OP_MUL; }
        else if (ch(p) == '/' && ch_at(p, 1) != '=' && ch_at(p, 1) != '/' && ch_at(p, 1) != '*' && ch_at(p, 1) != '>') { p->pos++; op = OP_DIV; }
        else break;
        Expr *b = parse_pow(p);
        if (!b) return NULL;
        a = mk_bin(p, op, a, b, start);
    }
    return a;
}
static Expr *parse_idiv(P *p) {
    int start = p->pos;
    Expr *a = parse_muldiv(p);
    while (a && accept_sym(p, "\\")) {
        Expr *b = parse_muldiv(p);
        if (!b) return NULL;
        a = mk_bin(p, OP_IDIV, a, b, start);
    }
    return a;
}
static Expr *parse_mod(P *p) {
    int start = p->pos;
    Expr *a = parse_idiv(p);
    while (a) {
        ws(p);
        if (accept_word(p, "MOD")) {}
        else if ((p->flags & PF_SCRIPT) && ch(p) == '%' && ch_at(p, 1) != '=') p->pos++;
        else break;
        Expr *b = parse_idiv(p);
        if (!b) return NULL;
        a = mk_bin(p, OP_MOD, a, b, start);
    }
    return a;
}
static Expr *parse_add(P *p) {
    int start = p->pos;
    Expr *a = parse_mod(p);
    while (a) {
        ws(p);
        int op;
        if (ch(p) == '+' && ch_at(p, 1) != '+' && ch_at(p, 1) != '=') op = OP_ADD;
        else if (ch(p) == '-' && ch_at(p, 1) != '-' && ch_at(p, 1) != '=') op = OP_SUB;
        else break;
        p->pos++;
        Expr *b = parse_mod(p);
        if (!b) return NULL;
        a = mk_bin(p, op, a, b, start);
    }
    return a;
}
static Expr *parse_cat(P *p) {
    int start = p->pos;
    Expr *a = parse_add(p);
    while (a) {
        ws(p);
        if (ch(p) == '&' && ch_at(p, 1) != '&' && ch_at(p, 1) != '=') p->pos++;
        else break;
        Expr *b = parse_add(p);
        if (!b) return NULL;
        a = mk_bin(p, OP_CAT, a, b, start);
    }
    return a;
}
static int parse_cmp_op(P *p) {
    if (accept_words(p, "IS NOT")) return OP_NEQ;
    if (accept_word(p, "IS")) return OP_EQ;
    if (accept_word(p, "EQ")) return OP_EQ;
    if (accept_words(p, "NOT EQUAL")) return OP_NEQ;
    if (accept_word(p, "EQUAL")) return OP_EQ;
    if (accept_word(p, "NEQ")) return OP_NEQ;
    if (accept_words(p, "GREATER THAN OR EQUAL TO")) return OP_GTE;
    if (accept_words(p, "GREATER THAN")) return OP_GT;
    if (accept_words(p, "LESS THAN OR EQUAL TO")) return OP_LTE;
    if (accept_words(p, "LESS THAN")) return OP_LT;
    if (accept_word(p, "GTE") || accept_word(p, "GE")) return OP_GTE;
    if (accept_word(p, "LTE") || accept_word(p, "LE")) return OP_LTE;
    if (accept_word(p, "GT")) return OP_GT;
    if (accept_word(p, "LT")) return OP_LT;
    if (accept_word(p, "CONTAINS")) return OP_CONTAINS;
    if (accept_words(p, "DOES NOT CONTAIN")) return OP_NCONTAINS;
    if (p->flags & PF_SCRIPT) {
        if (accept_sym(p, "==")) return OP_EQ;
        if (accept_sym(p, "!=")) return OP_NEQ;
        if (accept_sym(p, "<>")) return OP_NEQ;
        if (accept_sym(p, "<=")) return OP_LTE;
        if (accept_sym(p, ">=")) return OP_GTE;
        if (accept_sym(p, "<")) return OP_LT;
        ws(p);
        if (ch(p) == '>' ) { p->pos++; return OP_GT; }
    }
    return 0;
}
static Expr *parse_cmp(P *p) {
    int start = p->pos;
    Expr *a = parse_cat(p);
    while (a) {
        int op = parse_cmp_op(p);
        if (!op) break;
        Expr *b = parse_cat(p);
        if (!b) return NULL;
        a = mk_bin(p, op, a, b, start);
    }
    return a;
}
static Expr *parse_not(P *p) {
    ws(p);
    int start = p->pos;
    if (accept_word(p, "NOT") || ((p->flags & PF_SCRIPT) && ch(p) == '!' && ch_at(p, 1) != '=' && (p->pos++, 1))) {
        Expr *a = parse_not(p);
        if (!a) return NULL;
        Expr *e = new_expr(p, E_UN, start); e->op = OP_NOT; e->a = a; finish(p, e);
        return e;
    }
    return parse_cmp(p);
}
static Expr *parse_and(P *p) {
    int start = p->pos;
    Expr *a = parse_not(p);
    while (a && (accept_word(p, "AND") || ((p->flags & PF_SCRIPT) && accept_sym(p, "&&")))) {
        Expr *b = parse_not(p);
        if (!b) return NULL;
        a = mk_bin(p, OP_AND, a, b, start);
    }
    return a;
}
static Expr *parse_or(P *p) {
    int start = p->pos;
    Expr *a = parse_and(p);
    while (a && (accept_word(p, "OR") || ((p->flags & PF_SCRIPT) && accept_sym(p, "||")))) {
        Expr *b = parse_and(p);
        if (!b) return NULL;
        a = mk_bin(p, OP_OR, a, b, start);
    }
    return a;
}
static Expr *parse_xor(P *p) {
    int start = p->pos;
    Expr *a = parse_or(p);
    while (a && accept_word(p, "XOR")) {
        Expr *b = parse_or(p);
        if (!b) return NULL;
        a = mk_bin(p, OP_XOR, a, b, start);
    }
    return a;
}
static Expr *parse_eqv(P *p) {
    int start = p->pos;
    Expr *a = parse_xor(p);
    while (a && accept_word(p, "EQV")) {
        Expr *b = parse_xor(p);
        if (!b) return NULL;
        a = mk_bin(p, OP_EQV, a, b, start);
    }
    return a;
}
static Expr *parse_imp(P *p) {
    int start = p->pos;
    Expr *a = parse_eqv(p);
    while (a && accept_word(p, "IMP")) {
        Expr *b = parse_eqv(p);
        if (!b) return NULL;
        a = mk_bin(p, OP_IMP, a, b, start);
    }
    return a;
}
static Expr *parse_expr(P *p) { return parse_imp(p); }

/* assignment is only valid at statement level (cfset, cfscript) */
static Expr *parse_assignment(P *p) {
    int start = p->pos;
    Expr *lhs = parse_expr(p);
    if (!lhs) return NULL;
    ws(p);
    int op = 0;
    if (ch(p) == '=' && ch_at(p, 1) != '=') { p->pos++; op = '='; }
    else if (p->flags & PF_SCRIPT) {
        if (accept_sym(p, "+=")) op = OP_ADD;
        else if (accept_sym(p, "-=")) op = OP_SUB;
        else if (accept_sym(p, "*=")) op = OP_MUL;
        else if (accept_sym(p, "/=")) op = OP_DIV;
        else if (accept_sym(p, "&=")) op = OP_CAT;
        else if (accept_sym(p, "%=")) op = OP_MOD;
    }
    if (!op) return lhs;
    Expr *rhs = parse_expr(p);
    if (!rhs) return NULL;
    Expr *e = new_expr(p, E_ASSIGN, start);
    e->a = lhs; e->b = rhs; e->op = op == '=' ? 0 : op;
    e->line = lhs->line; e->col = lhs->col;
    finish(p, e);
    return e;
}

/* public entry. flags: 1 script, 2 stop at '#', 4 allow assignment */
Expr *expr_parse(const char *src, int *pos, int len, int script, int line0, int col0,
                 const char **err, int stop_at_hash) {
    (void)line0; (void)col0;
    P p = { src, *pos, len, (script & 1 ? PF_SCRIPT : 0) | (stop_at_hash ? PF_STOPHASH : 0), NULL, 0 };
    Expr *e = (script & 4) ? parse_assignment(&p) : parse_expr(&p);
    if (!e || p.err) {
        *err = p.err ? p.err : "Invalid expression format";
        *pos = p.errpos ? p.errpos : p.pos;
        return NULL;
    }
    ws(&p);
    *pos = p.pos;
    *err = NULL;
    return e;
}

Expr *expr_parse_string(const char *s, const char **err) {
    int pos = 0, len = (int)strlen(s);
    const char *saved = t_parse_base; t_parse_base = NULL;
    Expr *e = expr_parse(s, &pos, len, 4, 1, 1, err, 0);
    t_parse_base = saved;
    if (!e) return NULL;
    while (pos < len && isspace((unsigned char)s[pos])) pos++;
    if (pos < len) { *err = "Invalid expression format. The usual cause is an error in the expression structure."; return NULL; }
    return e;
}

/* ============================================================ evaluation */
static const char *SCOPES[] = {"VARIABLES","FORM","URL","CGI","COOKIE","CLIENT","SESSION",
                               "APPLICATION","SERVER","REQUEST","ATTRIBUTES","CALLER","THISTAG",NULL};

static int is_scope_name(const char *n) {
    for (int i = 0; SCOPES[i]; i++) if (!kf_stricmp(n, SCOPES[i])) return 1;
    return 0;
}

/* Administrator > Locking > "Full checking": shared scopes need a CFLOCK */
static void lock_check(Ctx *c, char mode, const char *scope, const char *prefix) {
    RState *rs = c->rs;
    if (mode != 'f') return;
    for (int i = 0; i < rs->locks_held; i++) {
        const char *n = rs->held_lock_names[i];
        if (n && (!strncmp(n, prefix, strlen(prefix)) || !strncmp(n, "NAME:", 5))) return;
    }
    kf_throw(c, "Lock", kprintf("Symbol %s is being accessed without a lock.", scope),
             kprintf("The KoldFusion Administrator has enabled full lock checking for the %s scope. Wrap every access to %s "
                     "variables in a CFLOCK tag (SCOPE=\"%s\").", scope, scope, scope));
}

Struct *scope_by_name(Ctx *c, const char *name, int for_write) {
    RState *rs = c->rs;
    (void)for_write;
    switch (toupper((unsigned char)name[0])) {
    case 'V': if (!kf_stricmp(name, "variables")) return c->variables; break;
    case 'F': if (!kf_stricmp(name, "form")) return rs->form; break;
    case 'U': if (!kf_stricmp(name, "url")) return rs->url; break;
    case 'C':
        if (!kf_stricmp(name, "cgi")) return rs->cgi;
        if (!kf_stricmp(name, "cookie")) return rs->cookie;
        if (!kf_stricmp(name, "caller")) return c->caller;
        if (!kf_stricmp(name, "client")) {
            if (!rs->client_enabled)
                kf_throw(c, "Application", "Client variables are not enabled for this application.",
                         "To use Client variables you must enable them with CLIENTMANAGEMENT=\"Yes\" in the CFAPPLICATION tag.");
            rs->client_dirty = 1;
            return rs->client;
        }
        break;
    case 'S':
        if (!kf_stricmp(name, "server")) { lock_check(c, rs->lockmode_server, "SERVER", "SERVER"); return rs->server; }
        if (!kf_stricmp(name, "session")) {
            if (!rs->session)
                kf_throw(c, "Application", "Session variables are not enabled for this application.",
                         "You must use a CFAPPLICATION tag with SESSIONMANAGEMENT=\"Yes\" before using Session variables. "
                         "Session variables may also have been disabled by the KoldFusion Administrator.");
            lock_check(c, rs->lockmode_session, "SESSION", "SESSION:");
            return rs->session;
        }
        break;
    case 'A':
        if (!kf_stricmp(name, "application")) {
            if (!rs->application)
                kf_throw(c, "Application", "Application variables are not enabled.",
                         "You must use a CFAPPLICATION tag with a NAME attribute before using Application variables.");
            lock_check(c, rs->lockmode_app, "APPLICATION", "APPLICATION:");
            return rs->application;
        }
        if (!kf_stricmp(name, "attributes")) return c->attributes;
        break;
    case 'R': if (!kf_stricmp(name, "request")) return rs->request; break;
    case 'T': if (!kf_stricmp(name, "thistag")) return c->thistag; break;
    }
    return NULL;
}

static const char *expr_text(Expr *e) {
    if (!e || !e->src || e->srclen <= 0) return "";
    return kstrndup(e->src, e->srclen);
}

static void throw_unresolved(Ctx *c, Expr *e, const char *name) __attribute__((noreturn));
static void throw_unresolved(Ctx *c, Expr *e, const char *name) {
    (void)e;
    kf_throw_at(c, e, "Expression",
        kprintf("Error resolving parameter <B>%s</B>", kf_upper(name)),
        "KoldFusion was unable to determine the value of the parameter. This problem is very likely due to the fact that either:"
        "<P><OL><LI>You have misspelled the parameter name, or"
        "<LI>You have not specified a QUERY attribute for a CFOUTPUT, CFMAIL, or CFTABLE tag.</OL>");
}

/* look up an unscoped variable */
static int query_member(Query *q, const char *name, Val *out);
static int lookup_unscoped(Ctx *c, const char *name, Val *out) {
    RState *rs = c->rs;
    if (c->qloop && (!kf_stricmp(name, "currentrow") || !kf_stricmp(name, "recordcount") || !kf_stricmp(name, "columnlist")))
        return query_member(c->qloop->q, name, out);
    for (QLoop *ql = c->qloop; ql; ql = ql->prev) {
        int ci = query_col_index(ql->q, name);
        if (ci >= 0) {
            int row = ql->q->currentrow > 0 ? ql->q->currentrow - 1 : 0;
            *out = query_get(ql->q, ci, row);
            return 1;
        }
    }
    Val *v;
    if ((v = struct_get(c->variables, name))) { *out = *v; return 1; }
    if ((v = struct_get(rs->cgi, name))) { *out = *v; return 1; }
    if ((v = struct_get(rs->url, name))) { *out = *v; return 1; }
    if ((v = struct_get(rs->form, name))) { *out = *v; return 1; }
    if ((v = struct_get(rs->cookie, name))) { *out = *v; return 1; }
    if (rs->client_enabled && rs->client && (v = struct_get(rs->client, name))) { *out = *v; return 1; }
    return 0;
}

static int query_member(Query *q, const char *name, Val *out) {
    if (!kf_stricmp(name, "recordcount")) { *out = v_num(q->nrows); return 1; }
    if (!kf_stricmp(name, "currentrow")) { *out = v_num(q->currentrow > 0 ? q->currentrow : (q->nrows ? 1 : 0)); return 1; }
    if (!kf_stricmp(name, "columnlist")) { *out = v_str(query_column_list(q)); return 1; }
    int ci = query_col_index(q, name);
    if (ci < 0) return 0;
    int row = q->currentrow > 0 ? q->currentrow - 1 : 0;
    *out = query_get(q, ci, row);
    return 1;
}

/* soft = 1: return 0 if missing instead of throwing */
static int get_var(Ctx *c, Expr *e, Val *out, int soft) {
    switch (e->k) {
    case E_VAR: {
        if (is_scope_name(e->name) && kf_stricmp(e->name, "variables")) {
            /* a local variable that shadows a scope name (CF 4.x allowed it) wins for bare references */
            Val *lv = struct_get(c->variables, e->name);
            if (lv) { *out = *lv; return 1; }
        }
        if (is_scope_name(e->name)) {
            Struct *s;
            if (soft) {
                /* IsDefined("Session") must not throw */
                RState *rs = c->rs;
                if (!kf_stricmp(e->name, "session") && !rs->session) return 0;
                if (!kf_stricmp(e->name, "application") && !rs->application) return 0;
                if (!kf_stricmp(e->name, "client") && !rs->client_enabled) return 0;
            }
            s = scope_by_name(c, e->name, 0);
            if (s) { *out = v_struct(s); return 1; }
        }
        if (lookup_unscoped(c, e->name, out)) return 1;
        if (soft) return 0;
        throw_unresolved(c, e, e->name);
    }
    case E_DOT: {
        Val base;
        /* scope.var */
        if (e->a->k == E_VAR && is_scope_name(e->a->name)) {
            Struct *s;
            if (soft) {
                RState *rs = c->rs;
                if (!kf_stricmp(e->a->name, "session") && !rs->session) return 0;
                if (!kf_stricmp(e->a->name, "application") && !rs->application) return 0;
                if (!kf_stricmp(e->a->name, "client") && !rs->client_enabled) return 0;
            }
            s = scope_by_name(c, e->a->name, 0);
            if (s) {
                Val *v = struct_get(s, e->name);
                if (v) { *out = *v; return 1; }
                /* Form.tree.node: a field whose name contains dots */
                for (int i = 0; i < s->n; i++) {
                    if (!kf_strnicmp(s->e[i].key, e->name, strlen(e->name)) && s->e[i].key[strlen(e->name)] == '.') {
                        Val tmp = v_null();
                        Struct *sub = struct_new();
                        size_t pl = strlen(e->name) + 1;
                        for (int j = 0; j < s->n; j++)
                            if (!kf_strnicmp(s->e[j].key, e->name, pl - 1) && s->e[j].key[pl - 1] == '.')
                                struct_set(sub, s->e[j].key + pl, s->e[j].v);
                        tmp = v_struct(sub);
                        *out = tmp;
                        return 1;
                    }
                }
                if (!kf_stricmp(e->a->name, "cgi")) { *out = v_str(""); return 1; }
                if (soft) return 0;
                throw_unresolved(c, e, kprintf("%s.%s", e->a->name, e->name));
            }
        }
        if (!get_var(c, e->a, &base, soft)) return 0;
        if (base.t == VT_STRUCT) {
            Val *v = struct_get(base.u.st, e->name);
            if (v) { *out = *v; return 1; }
            if (soft) return 0;
            kf_throw_at(c, e, "Expression",
                kprintf("Error resolving parameter <B>%s</B>", kf_upper(expr_text(e))),
                kprintf("The structure referenced as %s does not contain an element named %s.",
                        kf_upper(expr_text(e->a)), kf_upper(e->name)));
        }
        if (base.t == VT_QUERY) {
            if (query_member(base.u.q, e->name, out)) return 1;
            if (soft) return 0;
            kf_throw_at(c, e, "Expression",
                kprintf("Error resolving parameter <B>%s</B>", kf_upper(expr_text(e))),
                kprintf("The query %s does not contain a column named %s.", kf_upper(expr_text(e->a)), kf_upper(e->name)));
        }
        if (base.t == VT_OBJECT) return java_get_field(c, e, base, e->name, out, soft);
        if (soft) return 0;
        throw_unresolved(c, e, expr_text(e));
    }
    case E_INDEX: {
        Val base;
        /* query.column[row] */
        if (e->a->k == E_DOT) {
            Val qb;
            int ok = 0;
            if (!(e->a->a->k == E_VAR && is_scope_name(e->a->a->name)))
                ok = get_var(c, e->a->a, &qb, 1);
            if (ok && qb.t == VT_QUERY) {
                Query *q = qb.u.q;
                int ci = query_col_index(q, e->a->name);
                if (ci >= 0) {
                    double r = val_number(c, eval(c, e->b), e->b);
                    if (r < 1 || r > q->nrows) {
                        if (soft) return 0;
                        kf_throw_at(c, e, "Expression", kprintf("Row index %s is out of range.", fmt_number(r)),
                                    kprintf("The query %s has %d rows.", kf_upper(expr_text(e->a->a)), q->nrows));
                    }
                    *out = query_get(q, ci, (int)r - 1);
                    return 1;
                }
            }
        }
        /* query["col"][row] */
        if (e->a->k == E_INDEX) {
            Val qb;
            if (get_var(c, e->a->a, &qb, 1) && qb.t == VT_QUERY) {
                Query *q = qb.u.q;
                const char *col = val_simple_str(c, eval(c, e->a->b), e->a->b);
                int ci = query_col_index(q, col);
                if (ci >= 0) {
                    double r = val_number(c, eval(c, e->b), e->b);
                    if (r < 1 || r > q->nrows) {
                        if (soft) return 0;
                        kf_throw_at(c, e, "Expression", kprintf("Row index %s is out of range.", fmt_number(r)),
                                    kprintf("The query has %d rows.", q->nrows));
                    }
                    *out = query_get(q, ci, (int)r - 1);
                    return 1;
                }
            }
        }
        if (!get_var(c, e->a, &base, soft)) return 0;
        Val idx = eval(c, e->b);
        if (base.t == VT_ARRAY) {
            double d = val_number(c, idx, e->b);
            Val *v = array_get(base.u.a, (int)d);
            if (v) { *out = *v; return 1; }
            if (soft) return 0;
            kf_throw_at(c, e, "Expression", "An error occurred while dereferencing an array element.",
                kprintf("The element at position %s of array %s cannot be found. The array has %d elements.",
                        fmt_number(d), kf_upper(expr_text(e->a)), base.u.a->n));
        }
        if (base.t == VT_STRUCT) {
            const char *k = val_simple_str(c, idx, e->b);
            Val *v = struct_get(base.u.st, k);
            if (v) { *out = *v; return 1; }
            if (soft) return 0;
            kf_throw_at(c, e, "Expression",
                kprintf("Error resolving parameter <B>%s</B>", kf_upper(expr_text(e))),
                kprintf("The structure referenced as %s does not contain an element named %s.",
                        kf_upper(expr_text(e->a)), kf_upper(k)));
        }
        if (base.t == VT_QUERY) {
            const char *k = val_simple_str(c, idx, e->b);
            int ci = query_col_index(base.u.q, k);
            if (ci >= 0) {
                /* q["col"] -> column value at current row */
                if (query_member(base.u.q, k, out)) return 1;
            }
            if (soft) return 0;
        }
        if (soft) return 0;
        kf_throw_at(c, e, "Expression", "Invalid use of the [] operator.",
                    kprintf("%s is not an array or a structure.", kf_upper(expr_text(e->a))));
    }
    default:
        if (soft) {
            /* other expressions: evaluate (may throw) */
            *out = eval(c, e);
            return 1;
        }
        *out = eval(c, e);
        return 1;
    }
}

const char *val_simple_str(Ctx *c, Val v, Expr *where) {
    if (v_is_simple(v) || v.t == VT_BINARY) return v_tostr(v);
    kf_throw_at(c, where, "Expression", "Complex object types cannot be converted to simple values.",
        "The expression has requested a variable or an intermediate expression result as a simple value, "
        "however, the result cannot be converted to a simple value. Simple values are strings, numbers, "
        "boolean values, and date/time values. Queries, arrays, and COM objects are examples of complex values.");
}

double val_number(Ctx *c, Val v, Expr *where) {
    double d;
    if (v_tonum(v, &d)) return d;
    if (!v_is_simple(v)) val_simple_str(c, v, where);
    kf_throw_at(c, where, "Expression", kprintf("Cannot convert %s to number.", kf_html_escape(v_tostr(v))),
        "Please, check the KoldFusion manual for the allowed conversions between data types.");
}

int val_truth(Ctx *c, Val v, Expr *where) {
    int b;
    if (v_tobool(v, &b)) return b;
    if (!v_is_simple(v)) val_simple_str(c, v, where);
    kf_throw_at(c, where, "Expression", kprintf("Cannot convert %s to Boolean.", kf_html_escape(v_tostr(v))),
        "Please, check the KoldFusion manual for the allowed conversions between data types.");
}

Val op_binary(Ctx *c, int op, Val a, Val b, Expr *where) {
    double x, y;
    switch (op) {
    case OP_ADD: case OP_SUB: case OP_MUL: case OP_DIV: case OP_POW:
        x = val_number(c, a, where ? where->a : NULL);
        y = val_number(c, b, where ? where->b : NULL);
        switch (op) {
        case OP_ADD: return v_num(x + y);
        case OP_SUB: return v_num(x - y);
        case OP_MUL: return v_num(x * y);
        case OP_DIV:
            if (y == 0) kf_throw_at(c, where, "Expression", "Division by zero.", "The expression attempted to divide by zero.");
            return v_num(x / y);
        default: return v_num(pow(x, y));
        }
    case OP_IDIV: case OP_MOD: {
        x = val_number(c, a, where ? where->a : NULL);
        y = val_number(c, b, where ? where->b : NULL);
        long lx = (long)x, ly = (long)y;
        if (ly == 0) kf_throw_at(c, where, "Expression", "Division by zero.", "The expression attempted to divide by zero.");
        return v_num(op == OP_IDIV ? (double)(lx / ly) : (double)(lx % ly));
    }
    case OP_CAT: {
        const char *s1 = val_simple_str(c, a, where ? where->a : NULL);
        const char *s2 = val_simple_str(c, b, where ? where->b : NULL);
        size_t l1 = (a.t == VT_STR) ? a.u.str.len : strlen(s1);
        size_t l2 = (b.t == VT_STR) ? b.u.str.len : strlen(s2);
        char *r = kmalloc(l1 + l2 + 1);
        memcpy(r, s1, l1); memcpy(r + l1, s2, l2); r[l1 + l2] = 0;
        return v_strn(r, l1 + l2);
    }
    case OP_EQ: case OP_NEQ: case OP_LT: case OP_LTE: case OP_GT: case OP_GTE: {
        val_simple_str(c, a, where ? where->a : NULL);
        val_simple_str(c, b, where ? where->b : NULL);
        int r = v_compare(a, b);
        switch (op) {
        case OP_EQ: return v_bool(r == 0);
        case OP_NEQ: return v_bool(r != 0);
        case OP_LT: return v_bool(r < 0);
        case OP_LTE: return v_bool(r <= 0);
        case OP_GT: return v_bool(r > 0);
        default: return v_bool(r >= 0);
        }
    }
    case OP_CONTAINS: case OP_NCONTAINS: {
        const char *s1 = val_simple_str(c, a, where ? where->a : NULL);
        const char *s2 = val_simple_str(c, b, where ? where->b : NULL);
        int r = kf_stristr(s1, s2) != NULL;
        return v_bool(op == OP_CONTAINS ? r : !r);
    }
    case OP_AND: return v_bool(val_truth(c, a, NULL) && val_truth(c, b, NULL));
    case OP_OR: return v_bool(val_truth(c, a, NULL) || val_truth(c, b, NULL));
    case OP_XOR: return v_bool(val_truth(c, a, NULL) != val_truth(c, b, NULL));
    case OP_EQV: return v_bool(val_truth(c, a, NULL) == val_truth(c, b, NULL));
    case OP_IMP: return v_bool(!val_truth(c, a, NULL) || val_truth(c, b, NULL));
    }
    return v_null();
}

static Val call_function(Ctx *c, Expr *e) {
    int minargs, maxargs;
    if (!strncmp(e->name, "__method.", 9)) {
        Val obj = eval(c, e->a);
        if (obj.t == VT_OBJECT) return java_invoke(c, e, obj, e->name + 9);
        kf_throw_at(c, e, "Object", kprintf("Cannot call the method %s.", kf_upper(e->name + 9)),
                    kprintf("Methods can only be called on COM, CORBA or Java objects created with CFOBJECT or CreateObject(); "
                            "the value is a %s. KoldFusion for UNIX has no COM support and no Java VM is configured.", v_typename(obj)));
    }
    BuiltinFn fn = e->fn;
    if (!fn) {
        fn = func_lookup(e->name, &minargs, &maxargs);
        if (!fn)
            kf_throw_at(c, e, "Expression",
                kprintf("Error resolving function <B>%s</B>", kf_upper(e->name)),
                kprintf("The function %s is not a valid KoldFusion function. Check the spelling of the function name "
                        "and refer to the CFML Language Reference for a list of supported functions.", kf_upper(e->name)));
        if (e->nargs < minargs || (maxargs >= 0 && e->nargs > maxargs)) {
            const char *takes;
            if (minargs == maxargs) takes = kprintf("The function accepts %d parameter%s.", minargs, minargs == 1 ? "" : "s");
            else if (maxargs < 0) takes = kprintf("The function accepts %d or more parameters.", minargs);
            else takes = kprintf("The function accepts %d to %d parameters.", minargs, maxargs);
            kf_throw_at(c, e, "Expression",
                kprintf("Parameter validation error for function %s.", kf_upper(e->name)), takes);
        }
        e->fn = (void *)fn;
    }
    Val argv[64];
    if (func_is_lazy(fn)) {
        for (int i = 0; i < e->nargs && i < 64; i++) argv[i] = v_null();
    } else {
        for (int i = 0; i < e->nargs && i < 64; i++) argv[i] = eval(c, e->args[i]);
    }
    return fn(c, e->nargs, argv, e);
}

Val eval(Ctx *c, Expr *e) {
    switch (e->k) {
    case E_LIT: return e->lit;
    case E_STRI: {
        if (e->nargs == 1 && e->args[0]->k != E_LIT) return eval(c, e->args[0]);
        Buf b; buf_init(&b);
        for (int i = 0; i < e->nargs; i++) {
            Val v = eval(c, e->args[i]);
            if (v.t == VT_STR) buf_put(&b, v.u.str.s, v.u.str.len);
            else buf_puts(&b, val_simple_str(c, v, e->args[i]));
        }
        return v_strn(buf_cstr(&b), b.len);
    }
    case E_VAR: case E_DOT: case E_INDEX: {
        Val v;
        get_var(c, e, &v, 0);
        return v;
    }
    case E_CALL: return call_function(c, e);
    case E_BIN: {
        if (e->op == OP_AND) {
            if (!val_truth(c, eval(c, e->a), e->a)) return v_bool(0);
            return v_bool(val_truth(c, eval(c, e->b), e->b));
        }
        if (e->op == OP_OR) {
            if (val_truth(c, eval(c, e->a), e->a)) return v_bool(1);
            return v_bool(val_truth(c, eval(c, e->b), e->b));
        }
        Val a = eval(c, e->a);
        Val b = eval(c, e->b);
        return op_binary(c, e->op, a, b, e);
    }
    case E_UN: {
        Val a = eval(c, e->a);
        switch (e->op) {
        case OP_NEG: return v_num(-val_number(c, a, e->a));
        case OP_POS: return v_num(val_number(c, a, e->a));
        case OP_NOT: return v_bool(!val_truth(c, a, e->a));
        }
        return a;
    }
    case E_ASSIGN: {
        Val v = eval(c, e->b);
        if (e->op) v = op_binary(c, e->op, eval(c, e->a), v, e);
        assign(c, e->a, v);
        return v;
    }
    case E_POSTINC: case E_PREINC: {
        Val old = eval(c, e->a);
        double d = val_number(c, old, e->a);
        Val nv = v_num(e->op == '+' ? d + 1 : d - 1);
        assign(c, e->a, nv);
        return e->k == E_POSTINC ? v_num(d) : nv;
    }
    }
    return v_null();
}

Val eval_to_simple(Ctx *c, Expr *e) {
    Val v = eval(c, e);
    val_simple_str(c, v, e);
    return v;
}

const char *eval_str(Ctx *c, Expr *e) {
    Val v = eval(c, e);
    return val_simple_str(c, v, e);
}

/* ============================================================ assignment */
Val *lvalue(Ctx *c, Expr *e, int create, int *is_new) {
    if (is_new) *is_new = 0;
    switch (e->k) {
    case E_VAR: {
        if (is_scope_name(e->name)) {
            Struct *s = scope_by_name(c, e->name, 1);
            if (s) { Val *v = kmalloc(sizeof(Val)); *v = v_struct(s); return v; }
        }
        Val *v = struct_get(c->variables, e->name);
        if (!v) {
            /* reading an existing unscoped var from another scope (e.g. a form field) */
            Val tmp;
            if (lookup_unscoped(c, e->name, &tmp) && !v_is_simple(tmp)) {
                Val *r = kmalloc(sizeof(Val)); *r = tmp; return r;
            }
            if (!create) return NULL;
            struct_set(c->variables, e->name, v_struct(struct_new()));
            v = struct_get(c->variables, e->name);
            if (is_new) *is_new = 1;
        }
        return v;
    }
    case E_DOT: {
        Val *b = lvalue(c, e->a, create, NULL);
        if (!b) return NULL;
        if (b->t == VT_STRUCT) {
            Val *v = struct_get(b->u.st, e->name);
            if (!v && create) {
                struct_set(b->u.st, e->name, v_struct(struct_new()));
                v = struct_get(b->u.st, e->name);
                if (is_new) *is_new = 1;
            }
            return v;
        }
        if (b->t == VT_QUERY) {
            Val *r = kmalloc(sizeof(Val));
            if (query_member(b->u.q, e->name, r)) return r;
            return NULL;
        }
        if (!create) return NULL;
        kf_throw_at(c, e, "Expression", kprintf("The variable %s is not a structure.", kf_upper(expr_text(e->a))),
                    "You have attempted to reference a member of a variable that is not a structure.");
    }
    case E_INDEX: {
        Val *b = lvalue(c, e->a, create, NULL);
        if (!b) return NULL;
        Val idx = eval(c, e->b);
        if (b->t == VT_ARRAY) {
            int i = (int)val_number(c, idx, e->b);
            Val *v = array_get(b->u.a, i);
            if ((!v || v->t == VT_NULL) && create && i >= 1) {
                if (b->u.a->dims > 1) {
                    Array *sub = array_new();
                    sub->dims = b->u.a->dims - 1;
                    array_set(b->u.a, i, v_arr(sub));
                } else array_set(b->u.a, i, v_struct(struct_new()));
                v = array_get(b->u.a, i);
            }
            return v;
        }
        if (b->t == VT_STRUCT) {
            const char *k = val_simple_str(c, idx, e->b);
            Val *v = struct_get(b->u.st, k);
            if (!v && create) {
                struct_set(b->u.st, k, v_struct(struct_new()));
                v = struct_get(b->u.st, k);
            }
            return v;
        }
        return NULL;
    }
    default: {
        Val *r = kmalloc(sizeof(Val));
        *r = eval(c, e);
        return r;
    }
    }
}

static Val assign_prep(Val v) {
    /* arrays are passed by value in CFML */
    if (v.t == VT_ARRAY) return v_arr(array_copy(v.u.a, 0));
    return v;
}

void assign(Ctx *c, Expr *lhs, Val v) {
    v = assign_prep(v);
    switch (lhs->k) {
    case E_VAR:
        /* ColdFusion 4.x let you create a local variable named like a scope;
         * dotted references (attributes.x) still reach the real scope */
        struct_set(c->variables, lhs->name, v);
        return;
    case E_DOT: {
        if (lhs->a->k == E_VAR && !kf_stricmp(lhs->a->name, "cgi"))
            kf_throw_at(c, lhs, "Expression", "CGI variables are read-only.", "You cannot assign values to CGI variables.");
        Val *b = lvalue(c, lhs->a, 1, NULL);
        if (b->t == VT_STRUCT) { struct_set(b->u.st, lhs->name, v); return; }
        if (b->t == VT_OBJECT) { java_set_field(c, lhs, *b, lhs->name, v); return; }
        if (b->t == VT_QUERY) {
            Query *q = b->u.q;
            int ci = query_col_index(q, lhs->name);
            if (ci >= 0 && q->nrows) { query_set(q, ci, q->currentrow > 0 ? q->currentrow - 1 : 0, v); return; }
        }
        kf_throw_at(c, lhs, "Expression", kprintf("The variable %s is not a structure.", kf_upper(expr_text(lhs->a))),
                    "You have attempted to set a member of a variable that is not a structure.");
    }
    case E_INDEX: {
        Val *b = lvalue(c, lhs->a, 1, NULL);
        Val idx = eval(c, lhs->b);
        if (b->t == VT_ARRAY) {
            double d = val_number(c, idx, lhs->b);
            if (d < 1) kf_throw_at(c, lhs, "Expression", "Array index out of range.",
                                   kprintf("Array indexes start at 1; %s is not a valid index.", fmt_number(d)));
            array_set(b->u.a, (int)d, v);
            return;
        }
        if (b->t == VT_STRUCT) { struct_set(b->u.st, val_simple_str(c, idx, lhs->b), v); return; }
        kf_throw_at(c, lhs, "Expression", "Invalid use of the [] operator.",
                    kprintf("%s is not an array or a structure.", kf_upper(expr_text(lhs->a))));
    }
    case E_LIT: case E_STRI: {
        const char *path = eval_str(c, lhs);
        assign_path(c, path, v);
        return;
    }
    default:
        kf_throw_at(c, lhs, "Expression", "Invalid assignment.",
                    kprintf("The expression %s cannot be assigned a value.", kf_html_escape(expr_text(lhs))));
    }
}

static Expr *parse_path(Ctx *c, const char *path) {
    const char *err;
    Expr *e = expr_parse_string(path, &err);
    if (!e || (e->k != E_VAR && e->k != E_DOT && e->k != E_INDEX))
        kf_throw(c, "Expression", kprintf("Invalid variable name %s.", kf_html_escape(path)),
                 "Variable names must start with a letter and contain only letters, numbers and underscores.");
    return e;
}

void assign_path(Ctx *c, const char *path, Val v) {
    assign(c, parse_path(c, path), v);
}

int resolve_path(Ctx *c, const char *path, Val *out) {
    const char *err;
    Expr *e = expr_parse_string(path, &err);
    if (!e || (e->k != E_VAR && e->k != E_DOT && e->k != E_INDEX))
        kf_throw(c, "Expression", kprintf("Parameter 1 of function IsDefined, which is now \"%s\", must be a syntactically valid variable name.",
                                          kf_html_escape(path)), "");
    Val tmp;
    return get_var(c, e, out ? out : &tmp, 1);
}

/* parse just a quoted string literal (tag attribute values) */
Expr *expr_parse_strlit(const char *src, int *pos, int len, const char **err) {
    P p = { src, *pos, len, 0, NULL, 0 };
    Expr *e = parse_string_lit(&p);
    if (!e || p.err) {
        *err = p.err ? p.err : "Invalid attribute value";
        *pos = p.errpos ? p.errpos : p.pos;
        return NULL;
    }
    *pos = p.pos;
    return e;
}
