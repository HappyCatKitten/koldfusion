/*
 * script.c - CFSCRIPT parser and executor (ColdFusion 4.5 level: statements,
 * if/else, while, do-while, for, for-in, switch, break, continue; no
 * user-defined functions - those arrived in ColdFusion 5).
 */
#define _GNU_SOURCE
#include "engine.h"
#include <ctype.h>
#include <stdlib.h>

typedef struct SP {
    const char *s;
    int pos, len;
    const char *err;
    int errpos;
    int line0, col0;
} SP;

static void sws(SP *p) {
    for (;;) {
        while (p->pos < p->len && isspace((unsigned char)p->s[p->pos])) p->pos++;
        if (p->pos + 1 < p->len && p->s[p->pos] == '/' && p->s[p->pos + 1] == '/') {
            while (p->pos < p->len && p->s[p->pos] != '\n') p->pos++;
            continue;
        }
        if (p->pos + 1 < p->len && p->s[p->pos] == '/' && p->s[p->pos + 1] == '*') {
            p->pos += 2;
            while (p->pos + 1 < p->len && !(p->s[p->pos] == '*' && p->s[p->pos + 1] == '/')) p->pos++;
            p->pos = p->pos + 2 <= p->len ? p->pos + 2 : p->len;
            continue;
        }
        break;
    }
}
static int sch(SP *p) { sws(p); return p->pos < p->len ? (unsigned char)p->s[p->pos] : 0; }
static int skw(SP *p, const char *w) {
    sws(p);
    size_t n = strlen(w);
    if (p->pos + (int)n > p->len || kf_strnicmp(p->s + p->pos, w, n)) return 0;
    if (p->pos + (int)n < p->len && kf_is_ident_char((unsigned char)p->s[p->pos + n])) return 0;
    p->pos += (int)n;
    return 1;
}
static int ssym(SP *p, char c) { if (sch(p) == c) { p->pos++; return 1; } return 0; }
static void sfail(SP *p, const char *m) { if (!p->err) { p->err = m; p->errpos = p->pos; } }

static Stmt *new_stmt(SP *p, SKind k) {
    Stmt *s = kmalloc(sizeof(Stmt));
    s->k = k;
    s->line = p->line0; s->col = p->col0;
    return s;
}

static Expr *sexpr(SP *p, int assign) {
    sws(p);
    const char *err = NULL;
    int pos = p->pos;
    Expr *e = expr_parse(p->s, &pos, p->len, assign ? 5 : 1, 0, 0, &err, 0);
    if (!e) { p->err = err; p->errpos = pos; return NULL; }
    p->pos = pos;
    return e;
}

static Stmt *sstmt(SP *p);

static Stmt *sblock_until_brace(SP *p) {
    Stmt *b = new_stmt(p, S_BLOCK);
    Stmt *kids[4096]; int n = 0;
    while (!p->err) {
        int c = sch(p);
        if (c == '}') { p->pos++; break; }
        if (!c) { sfail(p, "Missing closing brace } in CFSCRIPT block"); return NULL; }
        Stmt *s = sstmt(p);
        if (!s) return NULL;
        if (n < 4096) kids[n++] = s;
    }
    b->kids = kmalloc(sizeof(Stmt *) * (n ? n : 1));
    memcpy(b->kids, kids, sizeof(Stmt *) * n);
    b->nkids = n;
    return b;
}

static int expect_semi(SP *p) {
    if (ssym(p, ';')) return 1;
    sfail(p, "Missing semicolon. CFSCRIPT statements must end with a semicolon.");
    return 0;
}

static Stmt *sstmt(SP *p) {
    int c = sch(p);
    if (p->err) return NULL;
    if (c == '{') { p->pos++; return sblock_until_brace(p); }
    if (c == ';') { p->pos++; return new_stmt(p, S_EMPTY); }
    if (skw(p, "if")) {
        Stmt *s = new_stmt(p, S_IF);
        if (!ssym(p, '(')) { sfail(p, "Missing ( after if"); return NULL; }
        if (!(s->e = sexpr(p, 0))) return NULL;
        if (!ssym(p, ')')) { sfail(p, "Missing ) in if condition"); return NULL; }
        if (!(s->body = sstmt(p))) return NULL;
        if (skw(p, "else")) { if (!(s->els = sstmt(p))) return NULL; }
        return s;
    }
    if (skw(p, "while")) {
        Stmt *s = new_stmt(p, S_WHILE);
        if (!ssym(p, '(')) { sfail(p, "Missing ( after while"); return NULL; }
        if (!(s->e = sexpr(p, 0))) return NULL;
        if (!ssym(p, ')')) { sfail(p, "Missing ) in while condition"); return NULL; }
        if (!(s->body = sstmt(p))) return NULL;
        return s;
    }
    if (skw(p, "do")) {
        Stmt *s = new_stmt(p, S_DO);
        if (!(s->body = sstmt(p))) return NULL;
        if (!skw(p, "while")) { sfail(p, "Missing while after do block"); return NULL; }
        if (!ssym(p, '(')) { sfail(p, "Missing ( after while"); return NULL; }
        if (!(s->e = sexpr(p, 0))) return NULL;
        if (!ssym(p, ')')) { sfail(p, "Missing ) in while condition"); return NULL; }
        if (!expect_semi(p)) return NULL;
        return s;
    }
    if (skw(p, "for")) {
        if (!ssym(p, '(')) { sfail(p, "Missing ( after for"); return NULL; }
        /* for (key in struct) */
        int save = p->pos;
        sws(p);
        int ns = p->pos;
        while (p->pos < p->len && kf_is_ident_char((unsigned char)p->s[p->pos])) p->pos++;
        if (p->pos > ns) {
            const char *var = kstrndup(p->s + ns, p->pos - ns);
            if (skw(p, "in")) {
                Stmt *s = new_stmt(p, S_FORIN);
                s->var = var;
                if (!(s->e = sexpr(p, 0))) return NULL;
                if (!ssym(p, ')')) { sfail(p, "Missing ) in for-in"); return NULL; }
                if (!(s->body = sstmt(p))) return NULL;
                return s;
            }
        }
        p->pos = save;
        Stmt *s = new_stmt(p, S_FOR);
        if (sch(p) != ';') { if (!(s->e = sexpr(p, 1))) return NULL; }
        if (!ssym(p, ';')) { sfail(p, "Missing ; in for statement"); return NULL; }
        if (sch(p) != ';') { if (!(s->e2 = sexpr(p, 0))) return NULL; }
        if (!ssym(p, ';')) { sfail(p, "Missing ; in for statement"); return NULL; }
        if (sch(p) != ')') { if (!(s->e3 = sexpr(p, 1))) return NULL; }
        if (!ssym(p, ')')) { sfail(p, "Missing ) in for statement"); return NULL; }
        if (!(s->body = sstmt(p))) return NULL;
        return s;
    }
    if (skw(p, "switch")) {
        Stmt *s = new_stmt(p, S_SWITCH);
        if (!ssym(p, '(')) { sfail(p, "Missing ( after switch"); return NULL; }
        if (!(s->e = sexpr(p, 0))) return NULL;
        if (!ssym(p, ')')) { sfail(p, "Missing ) in switch"); return NULL; }
        if (!ssym(p, '{')) { sfail(p, "Missing { in switch"); return NULL; }
        /* flatten: kids are statements; caseval[i] marks a case label before kid i */
        Stmt *kids[2048]; Expr *cv[2048]; int isdef[2048]; int n = 0;
        Expr *pending_case = NULL; int pending_def = 0;
        for (;;) {
            int c2 = sch(p);
            if (c2 == '}') { p->pos++; break; }
            if (!c2) { sfail(p, "Missing } in switch"); return NULL; }
            if (skw(p, "case")) {
                Expr *v = sexpr(p, 0);
                if (!v) return NULL;
                if (!ssym(p, ':')) { sfail(p, "Missing : after case value"); return NULL; }
                /* consecutive labels: emit an empty statement carrying the label */
                if (pending_case || pending_def) {
                    kids[n] = new_stmt(p, S_EMPTY); cv[n] = pending_case; isdef[n] = pending_def; n++;
                }
                pending_case = v; pending_def = 0;
                continue;
            }
            if (skw(p, "default")) {
                if (!ssym(p, ':')) { sfail(p, "Missing : after default"); return NULL; }
                if (pending_case || pending_def) {
                    kids[n] = new_stmt(p, S_EMPTY); cv[n] = pending_case; isdef[n] = pending_def; n++;
                }
                pending_case = NULL; pending_def = 1;
                continue;
            }
            Stmt *st = sstmt(p);
            if (!st) return NULL;
            if (n < 2048) { kids[n] = st; cv[n] = pending_case; isdef[n] = pending_def; n++; }
            pending_case = NULL; pending_def = 0;
        }
        if (pending_case || pending_def) { kids[n] = new_stmt(p, S_EMPTY); cv[n] = pending_case; isdef[n] = pending_def; n++; }
        s->kids = kmalloc(sizeof(Stmt *) * (n ? n : 1)); memcpy(s->kids, kids, sizeof(Stmt *) * n);
        s->caseval = kmalloc(sizeof(Expr *) * (n ? n : 1)); memcpy(s->caseval, cv, sizeof(Expr *) * n);
        s->isdefault = kmalloc(sizeof(int) * (n ? n : 1)); memcpy(s->isdefault, isdef, sizeof(int) * n);
        s->nkids = n;
        return s;
    }
    if (skw(p, "break")) { if (!expect_semi(p)) return NULL; return new_stmt(p, S_BREAK); }
    if (skw(p, "continue")) { if (!expect_semi(p)) return NULL; return new_stmt(p, S_CONTINUE); }
    if (skw(p, "function")) {
        sfail(p, "User-defined functions are not supported in CFSCRIPT. (They were introduced in ColdFusion 5.0; KoldFusion 4.5 does not support them.)");
        return NULL;
    }
    if (skw(p, "var")) { /* tolerate "var x = 1;" as a plain assignment */ }
    Stmt *s = new_stmt(p, S_EXPR);
    if (!(s->e = sexpr(p, 1))) return NULL;
    if (!expect_semi(p)) return NULL;
    return s;
}

Stmt *script_parse(const char *src, int len, int line0, int col0, const char **err, int *eline, int *ecol) {
    SP p = { src, 0, len, NULL, 0, line0, col0 };
    Stmt *b = new_stmt(&p, S_BLOCK);
    Stmt *kids[8192]; int n = 0;
    while (!p.err) {
        if (!sch(&p)) break;
        Stmt *s = sstmt(&p);
        if (!s) break;
        if (n < 8192) kids[n++] = s;
    }
    if (p.err) {
        *err = p.err;
        int l = line0, c = col0;
        for (int i = 0; i < p.errpos && i < len; i++) { if (src[i] == '\n') { l++; c = 1; } else c++; }
        *eline = l; *ecol = c;
        return NULL;
    }
    b->kids = kmalloc(sizeof(Stmt *) * (n ? n : 1));
    memcpy(b->kids, kids, sizeof(Stmt *) * n);
    b->nkids = n;
    return b;
}

/* ================================================================ exec */
void script_exec(Ctx *c, Stmt *s, int *flow) {
    *flow = FL_OK;
    switch (s->k) {
    case S_EMPTY: return;
    case S_EXPR: eval(c, s->e); return;
    case S_BLOCK:
        for (int i = 0; i < s->nkids; i++) {
            script_exec(c, s->kids[i], flow);
            if (*flow) return;
        }
        return;
    case S_IF:
        if (val_truth(c, eval(c, s->e), s->e)) script_exec(c, s->body, flow);
        else if (s->els) script_exec(c, s->els, flow);
        return;
    case S_WHILE:
        while (val_truth(c, eval(c, s->e), s->e)) {
            check_timeout(c);
            script_exec(c, s->body, flow);
            if (*flow == FL_BREAK) { *flow = FL_OK; break; }
            if (*flow == FL_CONTINUE) { *flow = FL_OK; continue; }
            if (*flow) return;
        }
        return;
    case S_DO:
        do {
            check_timeout(c);
            script_exec(c, s->body, flow);
            if (*flow == FL_BREAK) { *flow = FL_OK; break; }
            if (*flow == FL_CONTINUE) { *flow = FL_OK; continue; }
            if (*flow) return;
        } while (val_truth(c, eval(c, s->e), s->e));
        return;
    case S_FOR:
        if (s->e) eval(c, s->e);
        for (;;) {
            check_timeout(c);
            if (s->e2 && !val_truth(c, eval(c, s->e2), s->e2)) break;
            script_exec(c, s->body, flow);
            if (*flow == FL_BREAK) { *flow = FL_OK; break; }
            if (*flow == FL_CONTINUE) *flow = FL_OK;
            if (*flow) return;
            if (s->e3) eval(c, s->e3);
        }
        return;
    case S_FORIN: {
        Val v = eval(c, s->e);
        if (v.t != VT_STRUCT)
            kf_throw_at(c, s->e, "Expression", "The for-in statement requires a structure.",
                        "The expression after IN must evaluate to a structure.");
        Struct *st = v.u.st;
        int n = st->n;
        const char **keys = kmalloc(sizeof(char *) * (n ? n : 1));
        for (int i = 0; i < n; i++) keys[i] = st->e[i].key;
        for (int i = 0; i < n; i++) {
            check_timeout(c);
            assign_path(c, s->var, v_str(keys[i]));
            script_exec(c, s->body, flow);
            if (*flow == FL_BREAK) { *flow = FL_OK; break; }
            if (*flow == FL_CONTINUE) *flow = FL_OK;
            if (*flow) return;
        }
        return;
    }
    case S_SWITCH: {
        Val v = eval_to_simple(c, s->e);
        int start = -1, def = -1;
        for (int i = 0; i < s->nkids; i++) {
            if (s->isdefault[i] && def < 0) def = i;
            if (s->caseval[i] && v_compare(v, eval_to_simple(c, s->caseval[i])) == 0) { start = i; break; }
        }
        if (start < 0) start = def;
        if (start < 0) return;
        for (int i = start; i < s->nkids; i++) {
            script_exec(c, s->kids[i], flow);
            if (*flow == FL_BREAK) { *flow = FL_OK; return; }
            if (*flow) return;
        }
        return;
    }
    case S_BREAK: *flow = FL_BREAK; return;
    case S_CONTINUE: *flow = FL_CONTINUE; return;
    case S_RETURN: return;
    }
}
