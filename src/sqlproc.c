/*
 * sqlproc.c - stored procedures for the KoldFusion Flat-File Driver.
 *
 * A procedure is created with SQL-Server/Sybase flavoured DDL and kept as its
 * source text in <dbdir>/<Name>.prc next to the table files:
 *
 *     CREATE PROCEDURE AddEmployee
 *         @FirstName VARCHAR(30), @LastName VARCHAR(30),
 *         @Dept VARCHAR(30) = 'Sales', @NewID INT OUTPUT
 *     AS
 *     BEGIN
 *         IF NOT EXISTS (SELECT * FROM Departments WHERE Dept_Name = @Dept)
 *             RETURN 1;
 *         INSERT INTO Employees (FirstName, LastName, Department)
 *             VALUES (@FirstName, @LastName, @Dept);
 *         SET @NewID = @@IDENTITY;
 *         RETURN 0;
 *     END
 *
 * The body is a small T-SQL dialect run statement by statement: DECLARE,
 * SET @v = expr, SELECT @v = col FROM ..., IF/ELSE, WHILE/BREAK/CONTINUE,
 * BEGIN/END, RETURN [n], EXEC proc args, RAISERROR, PRINT, plus any SQL the
 * driver understands. @variables are replaced by literals before a statement
 * is handed to sql.c, and every SELECT that is not an assignment produces a
 * result set. The same interpreter runs ad-hoc T-SQL batches sent through
 * CFQUERY ("DECLARE @n INT; SET @n = 5; SELECT ...") and EXEC / {call ...}.
 *
 * Statements are separated by semicolons, or simply start with a statement
 * keyword (SELECT, INSERT, UPDATE, DELETE, SET, DECLARE, IF, ...), the way
 * SQL Server 6.5/7.0 scripts were written. In a script, a procedure body runs
 * to its matching END (when it starts with BEGIN), to a line holding only GO,
 * or to the end of the text.
 */
#define _GNU_SOURCE
#include "sql.h"
#include <stdlib.h>
#include <stdarg.h>
#include <ctype.h>
#include <math.h>
#include <dirent.h>
#include <unistd.h>
#include <sys/stat.h>

#define DRV        "[Gibson][KoldFusion Flat-File Driver] "
#define MAX_NEST   32            /* SQL Server's procedure nesting limit */
#define MAX_LOOPS  100000        /* WHILE iterations per call (runaway guard) */

/* ================================================================ tokens */
enum { PT_EOF, PT_WORD, PT_VAR, PT_GVAR, PT_STR, PT_NUM, PT_PUNCT, PT_DATE, PT_QMARK };

typedef struct PTok { int t, quoted, pos, end; char *text; } PTok;
typedef struct TV { PTok *v; int n, cap; } TV;

static void tv_push(TV *a, int t, int pos, int end, char *text, int quoted) {
    if (a->n == a->cap) {
        int nc = a->cap ? a->cap * 2 : 64;
        PTok *nv = kmalloc(sizeof(PTok) * nc);
        if (a->n) memcpy(nv, a->v, sizeof(PTok) * a->n);
        a->v = nv; a->cap = nc;
    }
    PTok *k = &a->v[a->n++];
    k->t = t; k->pos = pos; k->end = end; k->text = text; k->quoted = quoted;
}

static int is_wstart(int c) { return isalpha(c) || c == '_' || c >= 0x80; }
static int is_wchar(int c) { return isalnum(c) || c == '_' || c == '$' || c == '#' || c >= 0x80; }

/* Tokenize; with err == NULL problems are tolerated (used to measure extents). */
static int ptokenize(const char *s, TV *tv, char *err, size_t el) {
    int n = (int)strlen(s), i = 0;
    memset(tv, 0, sizeof *tv);
    for (;;) {
        while (i < n && isspace((unsigned char)s[i])) i++;
        if (i >= n) break;
        unsigned char c = (unsigned char)s[i];
        int st = i;
        if (c == '-' && s[i + 1] == '-') { while (i < n && s[i] != '\n') i++; continue; }
        if (c == '/' && s[i + 1] == '*') {
            const char *e = strstr(s + i + 2, "*/");
            i = e ? (int)(e - s) + 2 : n;
            continue;
        }
        if (is_wstart(c)) {
            while (i < n && is_wchar((unsigned char)s[i])) i++;
            tv_push(tv, PT_WORD, st, i, kstrndup(s + st, i - st), 0);
            continue;
        }
        if (c == '@' && (s[i + 1] == '@' || is_wstart((unsigned char)s[i + 1]))) {
            int g = s[i + 1] == '@';
            i += g ? 2 : 1;
            int b = i;
            while (i < n && is_wchar((unsigned char)s[i])) i++;
            tv_push(tv, g ? PT_GVAR : PT_VAR, st, i, kstrndup(s + b, i - b), 0);
            continue;
        }
        if (c == '[' || c == '"' || c == '`' || c == '\'') {
            char close = c == '[' ? ']' : (char)c;
            Buf b; buf_init(&b);
            i++;
            int ok = 0;
            while (i < n) {
                if (s[i] == close) {
                    if (c != '[' && s[i + 1] == close) { buf_putc(&b, close); i += 2; continue; }
                    i++; ok = 1; break;
                }
                buf_putc(&b, s[i++]);
            }
            if (!ok && err) {
                snprintf(err, el, DRV "Unterminated %s starting at '%.20s'.", c == '\'' ? "string" : "quoted name", s + st);
                return 0;
            }
            tv_push(tv, c == '\'' ? PT_STR : PT_WORD, st, i, buf_cstr(&b), c == '\'' ? 0 : 1);
            continue;
        }
        if (isdigit(c) || (c == '.' && isdigit((unsigned char)s[i + 1]))) {
            while (i < n && (isalnum((unsigned char)s[i]) || s[i] == '.')) {
                if ((s[i] == 'e' || s[i] == 'E') && (s[i + 1] == '+' || s[i + 1] == '-')) i++;
                i++;
            }
            tv_push(tv, PT_NUM, st, i, kstrndup(s + st, i - st), 0);
            continue;
        }
        if (c == '#') {                            /* Access #10/22/1999# */
            const char *e = memchr(s + i + 1, '#', n - i - 1);
            if (e && e - (s + i) <= 64 && !memchr(s + i, '\n', e - (s + i))) {
                i = (int)(e - s) + 1;
                tv_push(tv, PT_DATE, st, i, kstrndup(s + st, i - st), 0);
                continue;
            }
        }
        if (c == '?') { i++; tv_push(tv, PT_QMARK, st, i, "?", 0); continue; }
        static const char *two[] = {"<=", ">=", "<>", "!=", "||", "==", NULL};
        int done = 0;
        for (int k = 0; two[k]; k++)
            if (s[i] == two[k][0] && s[i + 1] == two[k][1]) {
                i += 2;
                tv_push(tv, PT_PUNCT, st, i, kstrdup(two[k]), 0);
                done = 1;
                break;
            }
        if (done) continue;
        i++;
        tv_push(tv, PT_PUNCT, st, i, kstrndup(s + st, 1), 0);
    }
    tv_push(tv, PT_EOF, n, n, "", 0);
    return 1;
}

static int kw(const PTok *k, const char *w) { return k->t == PT_WORD && !k->quoted && !kf_stricmp(k->text, w); }
static int pu(const PTok *k, const char *p) { return k->t == PT_PUNCT && !strcmp(k->text, p); }

static const char *STMT_KW[] = {
    "SELECT", "INSERT", "UPDATE", "DELETE", "SET", "DECLARE", "IF", "ELSE", "WHILE", "BEGIN", "END",
    "RETURN", "EXEC", "EXECUTE", "PRINT", "RAISERROR", "BREAK", "CONTINUE", "CREATE", "DROP", "ALTER",
    "TRUNCATE", "COMMIT", "ROLLBACK", "SAVE", "GO", "CALL", NULL
};
static int is_stmt_kw(const PTok *k) {
    if (k->t != PT_WORD || k->quoted) return 0;
    for (int i = 0; STMT_KW[i]; i++) if (!kf_stricmp(STMT_KW[i], k->text)) return 1;
    return 0;
}
static int is_tran_word(const PTok *k) { return kw(k, "TRAN") || kw(k, "TRANSACTION") || kw(k, "DISTRIBUTED") || kw(k, "WORK"); }

/* ================================================================ types */
typedef struct PType { char cls; int size, scale; char *tname; } PType;   /* cls: i f s d b */

static const struct { const char *name; char cls; int scale; int sized; } PTYPES[] = {
    {"INT", 'i', -1, 0}, {"INTEGER", 'i', -1, 0}, {"SMALLINT", 'i', -1, 0}, {"TINYINT", 'i', -1, 0},
    {"BIGINT", 'i', -1, 0}, {"LONG", 'i', -1, 0}, {"BYTE", 'i', -1, 0}, {"SHORT", 'i', -1, 0},
    {"MEDIUMINT", 'i', -1, 0}, {"COUNTER", 'i', -1, 0}, {"AUTOINCREMENT", 'i', -1, 0},
    {"FLOAT", 'f', -1, 0}, {"REAL", 'f', -1, 0}, {"DOUBLE", 'f', -1, 0}, {"SINGLE", 'f', -1, 0},
    {"NUMERIC", 'f', 0, 2}, {"DECIMAL", 'f', 0, 2}, {"DEC", 'f', 0, 2}, {"NUMBER", 'f', -1, 2},
    {"MONEY", 'f', 4, 0}, {"SMALLMONEY", 'f', 4, 0}, {"CURRENCY", 'f', 4, 0},
    {"VARCHAR", 's', -1, 1}, {"CHAR", 's', -1, 1}, {"NVARCHAR", 's', -1, 1}, {"NCHAR", 's', -1, 1},
    {"CHARACTER", 's', -1, 1}, {"VARCHAR2", 's', -1, 1}, {"STRING", 's', -1, 0}, {"TEXT", 's', -1, 0},
    {"NTEXT", 's', -1, 0}, {"MEMO", 's', -1, 0}, {"LONGTEXT", 's', -1, 0}, {"LONGCHAR", 's', -1, 0},
    {"CLOB", 's', -1, 0}, {"SYSNAME", 's', -1, 0}, {"UNIQUEIDENTIFIER", 's', -1, 0},
    {"DATE", 'd', -1, 0}, {"DATETIME", 'd', -1, 0}, {"SMALLDATETIME", 'd', -1, 0}, {"TIME", 'd', -1, 0},
    {"TIMESTAMP", 'd', -1, 0},
    {"BIT", 'b', -1, 0}, {"YESNO", 'b', -1, 0}, {"BOOLEAN", 'b', -1, 0}, {"BOOL", 'b', -1, 0},
    {"LOGICAL", 'b', -1, 0},
};

/* ================================================================ interpreter state */
typedef struct PVar { char *name; PType ty; Val v; int declpos; } PVar;

typedef struct Run {                  /* one procedure / batch activation */
    const char *src; PTok *t; int n;
    PVar *vars; int nvars, capvars;
    const char *proc;                 /* NULL for an ad-hoc batch */
    int depth, loopdepth;
    double ret; int returned;
} Run;

typedef struct Sess {                 /* shared by nested calls */
    const char *dbdir;
    Query **sets; int nsets, capsets;
    Query *last;                      /* batch result: last SELECT / first set of the last EXEC */
    long affected, rowcount;
    long loops;
    int failed;
    char msg[1024];
} Sess;

enum { P_ERR = 0, P_OK, P_RET, P_BRK, P_CONT };

static int line_of(const char *src, int pos) {
    int l = 1;
    for (int i = 0; i < pos && src[i]; i++) if (src[i] == '\n') l++;
    return l;
}

static void add_where(Sess *s, Run *r, int at) {
    if (!r || !r->proc) return;
    size_t l = strlen(s->msg);
    snprintf(s->msg + l, sizeof s->msg - l, " (procedure %s, line %d)", r->proc,
             at >= 0 && at < r->n ? line_of(r->src, r->t[at].pos) : 1);
}

/* error with the driver prefix */
static void perr(Sess *s, Run *r, int at, const char *fmt, ...) __attribute__((format(printf, 4, 5)));
static void perr(Sess *s, Run *r, int at, const char *fmt, ...) {
    if (s->failed) return;
    s->failed = 1;
    size_t n = strlen(DRV);
    memcpy(s->msg, DRV, n);
    va_list ap; va_start(ap, fmt);
    vsnprintf(s->msg + n, sizeof s->msg - n, fmt, ap);
    va_end(ap);
    add_where(s, r, at);
}
/* error text that already carries the driver prefix (from sql.c) */
static void perr_raw(Sess *s, Run *r, int at, const char *msg) {
    if (s->failed) return;
    s->failed = 1;
    snprintf(s->msg, sizeof s->msg, "%s", msg);
    add_where(s, r, at);
}

static void syntax(Sess *s, Run *r, int at) {
    PTok *k = &r->t[at];
    if (k->t == PT_EOF) perr(s, r, at, "Syntax error in SQL statement (unexpected end of statement).");
    else {
        int len = k->end - k->pos;
        perr(s, r, at, "Syntax error in SQL statement near '%.*s'.", len > 40 ? 40 : len, r->src + k->pos);
    }
}

static PVar *var_find(Run *r, const char *name) {
    for (int i = 0; i < r->nvars; i++) if (!kf_stricmp(r->vars[i].name, name)) return &r->vars[i];
    return NULL;
}
static PVar *var_add(Run *r, const char *name, PType ty) {
    if (r->nvars == r->capvars) {
        int nc = r->capvars ? r->capvars * 2 : 16;
        PVar *nv = kmalloc(sizeof(PVar) * nc);
        if (r->nvars) memcpy(nv, r->vars, sizeof(PVar) * r->nvars);
        r->vars = nv; r->capvars = nc;
    }
    PVar *v = &r->vars[r->nvars++];
    v->name = kstrdup(name); v->ty = ty; v->v = v_null(); v->declpos = -1;
    return v;
}

static void push_set(Sess *s, Query *q) {
    if (s->nsets == s->capsets) {
        int nc = s->capsets ? s->capsets * 2 : 8;
        Query **nv = kmalloc(sizeof(Query *) * nc);
        if (s->nsets) memcpy(nv, s->sets, sizeof(Query *) * s->nsets);
        s->sets = nv; s->capsets = nc;
    }
    s->sets[s->nsets++] = q;
}

/* ================================================================ values */
static char *fmt_ts(double d) {
    int y, mo, dd, h, mi, se;
    date_to_parts(d, &y, &mo, &dd, &h, &mi, &se);
    return kprintf("%04d-%02d-%02d %02d:%02d:%02d", y, mo, dd, h, mi, se);
}

static char *num_text(double d) {
    if (d == floor(d) && fabs(d) < 1e15) return kprintf("%.0f", d);
    char *t = kprintf("%.15g", d);
    if (strtod(t, NULL) != d) t = kprintf("%.17g", d);
    return t;
}

/* SQL literal for a value */
static char *lit(Val v) {
    switch (v.t) {
    case VT_NULL: return "NULL";
    case VT_NUM: { char *t = num_text(v.u.n); return v.u.n < 0 ? kprintf("(%s)", t) : t; }
    case VT_BOOL: return v.u.b ? "1" : "0";
    case VT_DATE: return kprintf("{ts '%s'}", fmt_ts(v.u.n));
    default: {
        const char *p = v_tostr(v);
        Buf b; buf_init(&b);
        buf_putc(&b, '\'');
        for (; *p; p++) { if (*p == '\'') buf_putc(&b, '\''); buf_putc(&b, *p); }
        buf_putc(&b, '\'');
        return buf_cstr(&b);
    }
    }
}

static const char *val_text(Val v) {
    switch (v.t) {
    case VT_NULL: return "NULL";
    case VT_NUM: return fmt_number(v.u.n);
    case VT_BOOL: return v.u.b ? "1" : "0";
    case VT_DATE: return fmt_ts(v.u.n);
    default: return v_tostr(v);
    }
}

static int strict_num(Val v, double *out) {
    switch (v.t) {
    case VT_NUM: case VT_DATE: *out = v.u.n; return 1;
    case VT_BOOL: *out = v.u.b; return 1;
    case VT_STR: return v_isnumeric_str(kf_trim(v.u.str.s), out);
    default: return 0;
    }
}

/* convert a value to a declared type (T-SQL implicit conversion) */
static int coerce(Sess *s, Run *r, int at, Val in, const PType *ty, Val *out) {
    double d;
    if (in.t == VT_NULL) { *out = in; return 1; }
    switch (ty->cls) {
    case 'i':
        if (!strict_num(in, &d)) {
            perr(s, r, at, "Conversion failed when converting the value '%.60s' to data type %s.", val_text(in), kf_lower(ty->tname));
            return 0;
        }
        *out = v_num(d < 0 ? ceil(d) : floor(d));
        return 1;
    case 'f':
        if (!strict_num(in, &d)) {
            perr(s, r, at, "Error converting data type varchar to %s ('%.60s').", kf_lower(ty->tname), val_text(in));
            return 0;
        }
        if (ty->scale >= 0) {
            double p = pow(10, ty->scale);
            double a = floor(fabs(d) * p + 0.5 + 1e-9) / p;
            d = d < 0 ? -a : a;
        }
        *out = v_num(d);
        return 1;
    case 'd':
        if (in.t == VT_DATE || in.t == VT_NUM) { *out = v_date(in.u.n); return 1; }
        if (in.t == VT_STR && date_parse(in.u.str.s, &d)) { *out = v_date(d); return 1; }
        perr(s, r, at, "Conversion failed when converting date and/or time from character string ('%.60s').", val_text(in));
        return 0;
    case 'b': {
        int b;
        if (strict_num(in, &d)) { *out = v_num(d != 0); return 1; }
        if (v_tobool(in, &b)) { *out = v_num(b ? 1 : 0); return 1; }
        perr(s, r, at, "Conversion failed when converting the value '%.60s' to data type bit.", val_text(in));
        return 0;
    }
    default: {
        const char *t = val_text(in);
        if (ty->size > 0) {
            long chars = 0; size_t i = 0;
            while (t[i] && chars < ty->size) { i++; while ((t[i] & 0xC0) == 0x80) i++; chars++; }
            if (t[i]) t = kstrndup(t, i);
        }
        *out = v_strdup(t);
        return 1;
    }
    }
}

/* ================================================================ text building */
static char *subst(Sess *s, Run *r, int from, int to) {
    Buf b; buf_init(&b);
    if (from >= to) return "";
    int cur = r->t[from].pos;
    for (int k = from; k < to; k++) {
        PTok *t = &r->t[k];
        const char *rep = NULL;
        if (t->t == PT_VAR) {
            PVar *v = var_find(r, t->text);
            if (!v) { perr(s, r, k, "Must declare the variable '@%s'.", t->text); return NULL; }
            rep = lit(v->v);
        } else if (t->t == PT_GVAR) {
            if (!kf_stricmp(t->text, "ROWCOUNT")) rep = kprintf("%ld", s->rowcount);
            else if (!kf_stricmp(t->text, "ERROR") || !kf_stricmp(t->text, "TRANCOUNT") || !kf_stricmp(t->text, "PROCID")) rep = "0";
            else if (!kf_stricmp(t->text, "FETCH_STATUS")) rep = "(-1)";
            else if (!kf_stricmp(t->text, "NESTLEVEL")) rep = kprintf("%d", r->depth);
            else if (!kf_stricmp(t->text, "SPID")) rep = "1";
        } else if (t->t == PT_QMARK) {
            perr(s, r, k, "Wrong number of parameters: the statement has parameter markers (?) but no values were bound to them.");
            return NULL;
        }
        if (!rep) continue;
        buf_put(&b, r->src + cur, t->pos - cur);
        buf_puts(&b, rep);
        cur = t->end;
    }
    buf_put(&b, r->src + cur, r->t[to - 1].end - cur);
    return buf_cstr(&b);
}

static int run_sql(Sess *s, Run *r, int at, const char *sql, int typed, Query **q, long *aff) {
    char err[1024];
    *q = NULL; *aff = 0;
    if (!sql_exec1(s->dbdir, sql, q, aff, typed, err, sizeof err)) { perr_raw(s, r, at, err); return 0; }
    return 1;
}

static int eval_sql(Sess *s, Run *r, int at, const char *sql, Val *out) {
    Query *q; long aff;
    if (!run_sql(s, r, at, sql, 1, &q, &aff)) return 0;
    *out = q && q->nrows && q->ncols ? q->data[0][0] : v_null();
    return 1;
}

static int eval_range(Sess *s, Run *r, int from, int to, Val *out) {
    if (from >= to) { syntax(s, r, from); return 0; }
    /* plain literals and variables need no trip through the SQL engine */
    if (to == from + 1) {
        PTok *t = &r->t[from];
        if (t->t == PT_VAR) {
            PVar *v = var_find(r, t->text);
            if (!v) { perr(s, r, from, "Must declare the variable '@%s'.", t->text); return 0; }
            *out = v->v; return 1;
        }
        if (t->t == PT_STR) { *out = v_str(t->text); return 1; }
        if (kw(t, "NULL")) { *out = v_null(); return 1; }
    }
    char *e = subst(s, r, from, to);
    if (!e) return 0;
    return eval_sql(s, r, from, kprintf("SELECT %s AS KFV", e), out);
}

static int eval_cond(Sess *s, Run *r, int from, int to, int *res) {
    char *e = subst(s, r, from, to);
    if (!e) return 0;
    Val v;
    if (!eval_sql(s, r, from, kprintf("SELECT CASE WHEN %s THEN 1 ELSE 0 END AS KFV", e), &v)) return 0;
    double d;
    *res = strict_num(v, &d) && d != 0;
    return 1;
}

/* ================================================================ statement extents */
/* End (exclusive) of the simple statement starting at i; *next skips a ';'. */
static int stmt_end(Run *r, int i, int *next) {
    PTok *t = r->t;
    const char *first = t[i].t == PT_WORD && !t[i].quoted ? t[i].text : "";
    int depth = 0, cdepth = 0, seen_set = 0, seen_values = 0, seen_sel = 0, after_union = 0, brace = pu(&t[i], "{");
    int j = i + 1;
    for (; t[j].t != PT_EOF; j++) {
        PTok *k = &t[j];
        if (pu(k, "(")) { depth++; continue; }
        if (pu(k, ")")) { if (depth == 0) break; depth--; continue; }
        if (brace && pu(k, "}")) { j++; break; }
        if (depth || brace) continue;
        if (pu(k, ";")) break;
        if (k->t != PT_WORD || k->quoted) continue;
        if (kw(k, "CASE")) { cdepth++; continue; }
        if (kw(k, "END")) { if (cdepth) { cdepth--; continue; } break; }
        if (cdepth) continue;
        if (kw(k, "UNION")) { after_union = 1; continue; }
        if (kw(k, "VALUES")) { seen_values = 1; continue; }
        if (kw(k, "SELECT")) {
            if (after_union) { after_union = 0; continue; }
            if (!kf_stricmp(first, "INSERT") && !seen_values && !seen_sel) { seen_sel = 1; continue; }
            break;
        }
        if (kw(k, "SET")) {
            if (!kf_stricmp(first, "UPDATE") && !seen_set) { seen_set = 1; continue; }
            break;
        }
        if (kw(k, "IF") && (kw(&t[j - 1], "TABLE") || kw(&t[j - 1], "PROCEDURE") || kw(&t[j - 1], "PROC") ||
                            kw(&t[j - 1], "VIEW") || kw(&t[j - 1], "INDEX"))) continue;
        if ((kw(k, "TRAN") || kw(k, "TRANSACTION")) && j == i + 1) continue;
        if (is_stmt_kw(k)) break;
    }
    *next = pu(&t[j], ";") ? j + 1 : j;
    return j;
}

/* End of an IF/WHILE condition: the first statement keyword outside parentheses. */
static int cond_end(Run *r, int i) {
    int depth = 0, cdepth = 0, j = i;
    for (; r->t[j].t != PT_EOF; j++) {
        PTok *k = &r->t[j];
        if (pu(k, "(")) { depth++; continue; }
        if (pu(k, ")")) { if (depth) depth--; continue; }
        if (depth) continue;
        if (pu(k, ";")) break;
        if (kw(k, "CASE")) { cdepth++; continue; }
        if (kw(k, "END") && cdepth) { cdepth--; continue; }
        if (cdepth) continue;
        if (is_stmt_kw(k)) break;
    }
    return j;
}

/* split [from,to) on top-level commas: fills starts[] (count returned) */
static int split_commas(Run *r, int from, int to, int *starts, int *ends, int max) {
    int n = 0, depth = 0, st = from;
    if (from >= to) return 0;
    for (int j = from; j <= to; j++) {
        if (j < to) {
            if (pu(&r->t[j], "(")) depth++;
            else if (pu(&r->t[j], ")")) depth--;
            if (depth || !pu(&r->t[j], ",")) continue;
        }
        if (n < max) { starts[n] = st; ends[n] = j; }
        n++;
        st = j + 1;
    }
    return n;
}

/* ================================================================ procedure files */
typedef struct PParam { char *name; PType ty; int output, has_def, d0, d1; } PParam;
typedef struct ProcDef {
    char *name, *src;
    TV tv;
    PParam *p; int np;
    int body;                     /* first token of the body */
} ProcDef;

static char *proc_file(const char *dbdir, const char *name) {
    DIR *d = opendir(dbdir);
    if (!d) return NULL;
    struct dirent *de;
    char *found = NULL;
    while ((de = readdir(d))) {
        size_t l = strlen(de->d_name);
        if (l > 4 && !strcmp(de->d_name + l - 4, ".prc") && l - 4 == strlen(name) && !kf_strnicmp(de->d_name, name, l - 4)) {
            found = kf_path_join(dbdir, de->d_name);
            break;
        }
    }
    closedir(d);
    return found;
}

static int table_exists(const char *dbdir, const char *name) {
    DIR *d = opendir(dbdir);
    if (!d) return 0;
    struct dirent *de;
    int found = 0;
    while ((de = readdir(d)) && !found) {
        size_t l = strlen(de->d_name);
        if (l > 4 && !strcmp(de->d_name + l - 4, ".tbl") && l - 4 == strlen(name) && !kf_strnicmp(de->d_name, name, l - 4)) found = 1;
    }
    closedir(d);
    return found;
}

/* type at *pi: NAME [PRECISION|VARYING] [(n[,m]) | (MAX)] */
static int parse_type(Sess *s, Run *r, int *pi, PType *ty) {
    int i = *pi;
    PTok *t = &r->t[i];
    if (t->t != PT_WORD) { syntax(s, r, i); return 0; }
    memset(ty, 0, sizeof *ty);
    int k = -1;
    for (size_t x = 0; x < sizeof PTYPES / sizeof PTYPES[0]; x++) if (!kf_stricmp(PTYPES[x].name, t->text)) { k = (int)x; break; }
    if (k < 0) { perr(s, r, i, "Column, parameter, or variable: Cannot find data type %s.", t->text); return 0; }
    ty->cls = PTYPES[k].cls;
    ty->scale = PTYPES[k].scale;
    Buf tn; buf_init(&tn);
    buf_puts(&tn, kf_upper(PTYPES[k].name));
    i++;
    if (kw(&r->t[i], "PRECISION") || kw(&r->t[i], "VARYING")) { buf_printf(&tn, " %s", kf_upper(r->t[i].text)); i++; }
    if (PTYPES[k].sized == 1) ty->size = 1;              /* CHAR / VARCHAR without a length is 1 character */
    if (pu(&r->t[i], "(")) {
        i++;
        if (kw(&r->t[i], "MAX")) { ty->size = 0; buf_puts(&tn, "(MAX)"); i++; }
        else if (r->t[i].t == PT_NUM) {
            long a = atol(r->t[i].text), b = -1;
            i++;
            if (pu(&r->t[i], ",") && r->t[i + 1].t == PT_NUM) { b = atol(r->t[i + 1].text); i += 2; }
            if (PTYPES[k].sized == 1) ty->size = a > 0 ? (int)a : 1;
            if (PTYPES[k].sized == 2) ty->scale = b >= 0 ? (int)b : 0;
            if (b >= 0) buf_printf(&tn, "(%ld,%ld)", a, b); else buf_printf(&tn, "(%ld)", a);
        } else { syntax(s, r, i); return 0; }
        if (!pu(&r->t[i], ")")) { syntax(s, r, i); return 0; }
        i++;
    }
    ty->tname = buf_cstr(&tn);
    *pi = i;
    return 1;
}

/* qualified name owner.name / db..name / name;1 -> last part */
static char *parse_qname(Sess *s, Run *r, int *pi) {
    int i = *pi;
    if (r->t[i].t != PT_WORD) { syntax(s, r, i); return NULL; }
    char *nm = r->t[i++].text;
    while (pu(&r->t[i], ".")) {
        i++;
        if (pu(&r->t[i], ".")) i++;
        if (r->t[i].t != PT_WORD) { syntax(s, r, i); return NULL; }
        nm = r->t[i++].text;
    }
    if (pu(&r->t[i], ";") && r->t[i + 1].t == PT_NUM) i += 2;     /* procedure group number */
    *pi = i;
    return nm;
}

/* parse "CREATE|ALTER PROC[EDURE] name params AS body" (tokens in pd->tv) */
static int parse_header(Sess *s, Run *r, ProcDef *pd) {
    int i = 0;
    if (!(kw(&r->t[i], "CREATE") || kw(&r->t[i], "ALTER"))) { syntax(s, r, i); return 0; }
    i++;
    if (!(kw(&r->t[i], "PROCEDURE") || kw(&r->t[i], "PROC"))) { syntax(s, r, i); return 0; }
    i++;
    if (!(pd->name = parse_qname(s, r, &i))) return 0;
    if (!sql_valid_table_name(pd->name)) { perr(s, r, i, "'%s' is not a valid procedure name.", pd->name); return 0; }
    int paren = 0;
    if (pu(&r->t[i], "(")) { paren = 1; i++; }
    int cap = 0;
    while (r->t[i].t == PT_VAR) {
        PParam p; memset(&p, 0, sizeof p);
        p.name = r->t[i].text;
        for (int k = 0; k < pd->np; k++)
            if (!kf_stricmp(pd->p[k].name, p.name)) {
                perr(s, r, i, "The variable name '@%s' has already been declared. Variable names must be unique within a query batch or stored procedure.", p.name);
                return 0;
            }
        i++;
        if (kw(&r->t[i], "AS")) i++;
        if (!parse_type(s, r, &i, &p.ty)) return 0;
        if (pu(&r->t[i], "=")) {
            i++;
            p.has_def = 1; p.d0 = i;
            int depth = 0;
            while (r->t[i].t != PT_EOF) {
                if (pu(&r->t[i], "(")) depth++;
                else if (pu(&r->t[i], ")")) { if (!depth) break; depth--; }
                else if (!depth && (pu(&r->t[i], ",") || kw(&r->t[i], "OUTPUT") || kw(&r->t[i], "OUT") ||
                                    kw(&r->t[i], "AS") || kw(&r->t[i], "WITH") || kw(&r->t[i], "READONLY"))) break;
                i++;
            }
            p.d1 = i;
            if (p.d0 == p.d1) { syntax(s, r, i); return 0; }
        }
        if (kw(&r->t[i], "OUTPUT") || kw(&r->t[i], "OUT")) { p.output = 1; i++; }
        if (kw(&r->t[i], "READONLY")) i++;
        if (pd->np == cap) {
            cap = cap ? cap * 2 : 8;
            PParam *np = kmalloc(sizeof(PParam) * cap);
            if (pd->np) memcpy(np, pd->p, sizeof(PParam) * pd->np);
            pd->p = np;
        }
        pd->p[pd->np++] = p;
        if (!pu(&r->t[i], ",")) break;
        i++;
    }
    if (paren) { if (!pu(&r->t[i], ")")) { syntax(s, r, i); return 0; } i++; }
    if (kw(&r->t[i], "WITH")) {
        i++;
        while (r->t[i].t == PT_WORD && !kw(&r->t[i], "AS")) { i++; if (pu(&r->t[i], ",")) i++; }
    }
    if (kw(&r->t[i], "FOR") && kw(&r->t[i + 1], "REPLICATION")) i += 2;
    if (!kw(&r->t[i], "AS")) { syntax(s, r, i); return 0; }
    i++;
    while (pu(&r->t[i], ";")) i++;
    if (r->t[i].t == PT_EOF) { perr(s, r, i, "Syntax error in CREATE PROCEDURE: the procedure has no statements."); return 0; }
    pd->body = i;
    return 1;
}

static int run_body(Sess *s, Run *r, int from, int run);

/* load and parse a procedure; NULL with s->failed set when it does not exist */
static ProcDef *load_proc(Sess *s, Run *caller, int at, const char *name) {
    char *path = proc_file(s->dbdir, name);
    size_t len;
    char *data = path ? kf_read_file(path, &len) : NULL;
    if (!data) { perr(s, caller, at, "Could not find stored procedure '%s'.", name); return NULL; }
    ProcDef *pd = kmalloc(sizeof(ProcDef));
    pd->src = kstrdup(data);
    free(data);
    char err[512];
    if (!ptokenize(pd->src, &pd->tv, err, sizeof err)) { perr_raw(s, caller, at, err); return NULL; }
    Run hr; memset(&hr, 0, sizeof hr);
    hr.src = pd->src; hr.t = pd->tv.v; hr.n = pd->tv.n; hr.proc = name;
    if (!parse_header(s, &hr, pd)) return NULL;
    return pd;
}

/* ================================================================ calls */
typedef struct CallArg {
    const char *name;            /* without @, NULL = positional */
    int output, use_default;
    Val value;
    Val out; int has_out;
} CallArg;

static int call_proc(Sess *s, Run *caller, int at, const char *name, CallArg *args, int nargs, double *status) {
    int depth = caller ? caller->depth + 1 : 1;
    if (depth > MAX_NEST) {
        perr(s, caller, at, "Maximum stored procedure nesting level exceeded (limit %d).", MAX_NEST);
        return 0;
    }
    ProcDef *pd = load_proc(s, caller, at, name);
    if (!pd) return 0;
    Run r; memset(&r, 0, sizeof r);
    r.src = pd->src; r.t = pd->tv.v; r.n = pd->tv.n; r.proc = pd->name; r.depth = depth;
    int *slot = kmalloc(sizeof(int) * (pd->np + 1));
    for (int k = 0; k < pd->np; k++) slot[k] = -1;
    int pos = 0, named = 0;
    for (int a = 0; a < nargs; a++) {
        int k;
        if (args[a].name) {
            named = 1;
            const char *an = args[a].name[0] == '@' ? args[a].name + 1 : args[a].name;
            for (k = 0; k < pd->np; k++) if (!kf_stricmp(pd->p[k].name, an)) break;
            if (k == pd->np) { perr(s, caller, at, "@%s is not a parameter for procedure %s.", an, pd->name); return 0; }
            if (slot[k] >= 0) { perr(s, caller, at, "Parameter '@%s' was supplied multiple times.", an); return 0; }
        } else {
            if (named) {
                perr(s, caller, at, "Must pass parameter number %d and subsequent parameters as '@name = value'. "
                     "After the form '@name = value' has been used, all subsequent parameters must be passed in the form '@name = value'.", a + 1);
                return 0;
            }
            k = pos++;
            if (k >= pd->np) { perr(s, caller, at, "Procedure or function %s has too many arguments specified.", pd->name); return 0; }
        }
        slot[k] = a;
        if (args[a].output && !pd->p[k].output) {
            perr(s, caller, at, "The formal parameter \"@%s\" was not declared as an OUTPUT parameter, but the actual parameter passed in requested output.", pd->p[k].name);
            return 0;
        }
    }
    /* bind: defaults are evaluated in the procedure's own (empty) scope */
    for (int k = 0; k < pd->np; k++) {
        PParam *p = &pd->p[k];
        Val v = v_null();
        if (slot[k] >= 0 && !args[slot[k]].use_default) {
            if (!coerce(s, caller, at, args[slot[k]].value, &p->ty, &v)) return 0;
        } else if (p->has_def) {
            if (!eval_range(s, &r, p->d0, p->d1, &v) || !coerce(s, &r, p->d0, v, &p->ty, &v)) return 0;
        } else if (!p->output || slot[k] < 0) {
            perr(s, caller, at, "Procedure '%s' expects parameter '@%s', which was not supplied.", pd->name, p->name);
            return 0;
        }
        PVar *pv = var_add(&r, p->name, p->ty);
        pv->v = v;
    }
    if (run_body(s, &r, pd->body, 1) == P_ERR) return 0;
    for (int k = 0; k < pd->np; k++) {
        if (slot[k] < 0 || !args[slot[k]].output) continue;
        args[slot[k]].out = r.vars[k].v;
        args[slot[k]].has_out = 1;
    }
    *status = r.returned ? r.ret : 0;
    return 1;
}

/* EXEC [@rc =] name [args] | EXEC ('dynamic sql') */
static int run_exec_stmt(Sess *s, Run *r, int i, int end, int run);
static int run_batch_text(Sess *s, Run *parent, int at, const char *text);

/* {[? =] call name[(a, b)]} and CALL name(a, b) */
static int run_odbc_call(Sess *s, Run *r, int i, int end, int run) {
    int j = i;
    int brace = pu(&r->t[j], "{");
    if (brace) j++;
    if (r->t[j].t == PT_QMARK && pu(&r->t[j + 1], "=")) j += 2;
    if (!kw(&r->t[j], "CALL")) { syntax(s, r, j); return P_ERR; }
    j++;
    char *name = parse_qname(s, r, &j);
    if (!name) return P_ERR;
    int a0 = j, a1 = j;
    if (pu(&r->t[j], "(")) {
        int depth = 0;
        a0 = j + 1;
        for (; j < end; j++) {
            if (pu(&r->t[j], "(")) depth++;
            else if (pu(&r->t[j], ")") && --depth == 0) break;
        }
        if (j >= end) { syntax(s, r, j); return P_ERR; }
        a1 = j++;
    }
    if (brace) { if (!pu(&r->t[j], "}")) { syntax(s, r, j); return P_ERR; } j++; }
    if (j != end) { syntax(s, r, j); return P_ERR; }
    if (!run) return P_OK;
    int st[256], en[256];
    int na = split_commas(r, a0, a1, st, en, 256);
    if (na > 256) { perr(s, r, i, "Too many parameters."); return P_ERR; }
    CallArg *args = kmalloc(sizeof(CallArg) * (na + 1));
    for (int a = 0; a < na; a++) {
        if (st[a] == en[a]) { syntax(s, r, st[a]); return P_ERR; }
        if (en[a] == st[a] + 1 && kw(&r->t[st[a]], "DEFAULT")) { args[a].use_default = 1; continue; }
        if (!eval_range(s, r, st[a], en[a], &args[a].value)) return P_ERR;
    }
    int before = s->nsets;
    double status;
    if (!call_proc(s, r, i, name, args, na, &status)) return P_ERR;
    if (s->nsets > before) s->last = s->sets[before];
    return P_OK;
}

static int run_exec_stmt(Sess *s, Run *r, int i, int end, int run) {
    int j = i + 1;
    PVar *rcvar = NULL;
    int rcpos = -1;
    if (r->t[j].t == PT_VAR && pu(&r->t[j + 1], "=")) { rcpos = j; j += 2; }
    if (pu(&r->t[j], "(")) {                      /* EXEC ('SELECT ...') */
        int depth = 0, k = j;
        for (; k < end; k++) {
            if (pu(&r->t[k], "(")) depth++;
            else if (pu(&r->t[k], ")") && --depth == 0) break;
        }
        if (k >= end || k + 1 != end) { syntax(s, r, k); return P_ERR; }
        if (!run) return P_OK;
        Val v;
        if (!eval_range(s, r, j + 1, k, &v)) return P_ERR;
        return run_batch_text(s, r, i, val_text(v)) ? P_OK : P_ERR;
    }
    char *name = parse_qname(s, r, &j);
    if (!name) return P_ERR;
    if (!run) return P_OK;
    if (rcpos >= 0 && !(rcvar = var_find(r, r->t[rcpos].text))) {
        perr(s, r, rcpos, "Must declare the variable '@%s'.", r->t[rcpos].text);
        return P_ERR;
    }
    int st[256], en[256];
    int na = split_commas(r, j, end, st, en, 256);
    if (na > 256) { perr(s, r, i, "Too many parameters."); return P_ERR; }
    CallArg *args = kmalloc(sizeof(CallArg) * (na + 1));
    PVar **outvars = kmalloc(sizeof(PVar *) * (na + 1));
    for (int a = 0; a < na; a++) {
        int a0 = st[a], a1 = en[a];
        if (a0 < a1 && r->t[a0].t == PT_VAR && pu(&r->t[a0 + 1], "=")) { args[a].name = r->t[a0].text; a0 += 2; }
        if (a1 > a0 && (kw(&r->t[a1 - 1], "OUTPUT") || kw(&r->t[a1 - 1], "OUT"))) { args[a].output = 1; a1--; }
        if (a0 >= a1) { syntax(s, r, a0); return P_ERR; }
        if (a1 == a0 + 1 && kw(&r->t[a0], "DEFAULT")) { args[a].use_default = 1; continue; }
        if (a1 == a0 + 1 && r->t[a0].t == PT_VAR) {
            PVar *v = var_find(r, r->t[a0].text);
            if (!v) { perr(s, r, a0, "Must declare the variable '@%s'.", r->t[a0].text); return P_ERR; }
            args[a].value = v->v;
            if (args[a].output) outvars[a] = v;
            continue;
        }
        if (!eval_range(s, r, a0, a1, &args[a].value)) return P_ERR;
    }
    int before = s->nsets;
    double status;
    if (!call_proc(s, r, i, name, args, na, &status)) return P_ERR;
    if (s->nsets > before) s->last = s->sets[before];
    for (int a = 0; a < na; a++)
        if (outvars[a] && args[a].has_out && !coerce(s, r, i, args[a].out, &outvars[a]->ty, &outvars[a]->v)) return P_ERR;
    if (rcvar && !coerce(s, r, rcpos, v_num(status), &rcvar->ty, &rcvar->v)) return P_ERR;
    return P_OK;
}

/* ================================================================ statements */
static int do_declare(Sess *s, Run *r, int i, int end, int run) {
    int j = i + 1;
    for (;;) {
        if (r->t[j].t != PT_VAR) { syntax(s, r, j); return P_ERR; }
        int vp = j;
        const char *name = r->t[j++].text;
        if (kw(&r->t[j], "AS")) j++;
        PType ty;
        if (!parse_type(s, r, &j, &ty)) return P_ERR;
        int e0 = -1, e1 = -1;
        if (pu(&r->t[j], "=")) {
            e0 = ++j;
            int depth = 0;
            for (; j < end; j++) {
                if (pu(&r->t[j], "(")) depth++;
                else if (pu(&r->t[j], ")")) depth--;
                else if (!depth && pu(&r->t[j], ",")) break;
            }
            e1 = j;
        }
        if (run) {
            PVar *v = var_find(r, name);
            if (v && v->declpos != r->t[vp].pos) {
                perr(s, r, vp, "The variable name '@%s' has already been declared. Variable names must be unique within a query batch or stored procedure.", name);
                return P_ERR;
            }
            if (!v) { v = var_add(r, name, ty); v->declpos = r->t[vp].pos; }
            if (e0 >= 0) {
                Val x;
                if (!eval_range(s, r, e0, e1, &x) || !coerce(s, r, e0, x, &v->ty, &v->v)) return P_ERR;
            }
        }
        if (j >= end) break;
        if (!pu(&r->t[j], ",")) { syntax(s, r, j); return P_ERR; }
        j++;
    }
    return P_OK;
}

static int do_set(Sess *s, Run *r, int i, int end, int run) {
    int j = i + 1;
    if (r->t[j].t != PT_VAR) return P_OK;          /* SET NOCOUNT ON, SET ANSI_NULLS OFF, ... */
    int vp = j++;
    const char *op = NULL;
    if (r->t[j].t == PT_PUNCT && strchr("+-*/%", r->t[j].text[0]) && !r->t[j].text[1] && pu(&r->t[j + 1], "=")) { op = r->t[j].text; j++; }
    if (!pu(&r->t[j], "=")) { syntax(s, r, j); return P_ERR; }
    j++;
    if (j >= end) { syntax(s, r, j); return P_ERR; }
    if (!run) return P_OK;
    PVar *v = var_find(r, r->t[vp].text);
    if (!v) { perr(s, r, vp, "Must declare the variable '@%s'.", r->t[vp].text); return P_ERR; }
    Val x;
    if (op) {
        char *e = subst(s, r, j, end);
        if (!e || !eval_sql(s, r, j, kprintf("SELECT %s %s (%s) AS KFV", lit(v->v), op, e), &x)) return P_ERR;
    } else if (!eval_range(s, r, j, end, &x)) return P_ERR;
    if (!coerce(s, r, j, x, &v->ty, &v->v)) return P_ERR;
    s->rowcount = 1;
    return P_OK;
}

/* SELECT @a = expr, @b = expr [FROM ...]: the last row wins, no rows leaves the variables alone */
static int do_select_assign(Sess *s, Run *r, int i, int items, int end, int run) {
    int from = end, depth = 0, cdepth = 0;
    for (int j = items; j < end; j++) {
        if (pu(&r->t[j], "(")) depth++;
        else if (pu(&r->t[j], ")")) depth--;
        else if (!depth && kw(&r->t[j], "CASE")) cdepth++;
        else if (!depth && kw(&r->t[j], "END") && cdepth) cdepth--;
        else if (!depth && !cdepth && (kw(&r->t[j], "FROM") || kw(&r->t[j], "WHERE") || kw(&r->t[j], "ORDER") ||
                                      kw(&r->t[j], "GROUP") || kw(&r->t[j], "HAVING") || kw(&r->t[j], "UNION"))) { from = j; break; }
    }
    int st[128], en[128];
    int n = split_commas(r, items, from, st, en, 128);
    if (n > 128) { perr(s, r, i, "Too many variables in SELECT."); return P_ERR; }
    PVar **vars = kmalloc(sizeof(PVar *) * (n + 1));
    Buf b; buf_init(&b);
    buf_puts(&b, "SELECT ");
    if (run && items > i + 1) {
        char *pre = subst(s, r, i + 1, items);
        if (!pre) return P_ERR;
        buf_printf(&b, "%s ", pre);
    }
    for (int k = 0; k < n; k++) {
        if (!(r->t[st[k]].t == PT_VAR && pu(&r->t[st[k] + 1], "=") && st[k] + 2 < en[k])) {
            perr(s, r, st[k], "A SELECT statement that assigns a value to a variable must not be combined with data-retrieval operations.");
            return P_ERR;
        }
        if (!run) continue;
        if (!(vars[k] = var_find(r, r->t[st[k]].text))) {
            perr(s, r, st[k], "Must declare the variable '@%s'.", r->t[st[k]].text);
            return P_ERR;
        }
        char *e = subst(s, r, st[k] + 2, en[k]);
        if (!e) return P_ERR;
        buf_printf(&b, "%s%s AS KFV%d", k ? ", " : "", e, k + 1);
    }
    if (!run) return P_OK;
    if (from < end) {
        char *rest = subst(s, r, from, end);
        if (!rest) return P_ERR;
        buf_printf(&b, " %s", rest);
    }
    Query *q; long aff;
    if (!run_sql(s, r, i, buf_cstr(&b), 1, &q, &aff)) return P_ERR;
    if (q && q->nrows)
        for (int k = 0; k < n && k < q->ncols; k++)
            if (!coerce(s, r, st[k], q->data[k][q->nrows - 1], &vars[k]->ty, &vars[k]->v)) return P_ERR;
    s->rowcount = q ? q->nrows : 0;
    return P_OK;
}

/* RAISERROR ('message %s', severity, state [, args]) */
static int do_raiserror(Sess *s, Run *r, int i, int end, int run) {
    int a0 = i + 1, a1 = end;
    for (int j = a0; j < end; j++) if (kw(&r->t[j], "WITH")) { a1 = j; break; }
    if (pu(&r->t[a0], "(") && pu(&r->t[a1 - 1], ")")) { a0++; a1--; }
    if (!run) return P_OK;
    int st[32], en[32];
    int n = split_commas(r, a0, a1, st, en, 32);
    if (n < 1 || n > 32) { syntax(s, r, a0); return P_ERR; }
    if (n == 1 && en[0] - st[0] == 2) { en[1] = en[0]; st[1] = en[0] = st[0] + 1; n = 2; }   /* RAISERROR 50001 'text' */
    Val args[32];
    for (int k = 0; k < n; k++) if (!eval_range(s, r, st[k], en[k], &args[k])) return P_ERR;
    double sev = 16;
    if (n > 1) strict_num(args[1], &sev);
    const char *fmt = val_text(args[0]);
    double num;
    if (args[0].t == VT_NUM && n == 2 && args[1].t == VT_STR) { fmt = args[1].u.str.s; sev = 16; }
    else if (strict_num(args[0], &num) && args[0].t == VT_NUM) fmt = kprintf("Error %s", fmt_number(num));
    Buf b; buf_init(&b);
    int ai = 3;
    for (const char *p = fmt; *p; p++) {
        if (*p != '%') { buf_putc(&b, *p); continue; }
        p++;
        while (*p && strchr("-+ #0123456789.lhI", *p)) p++;
        if (!*p) break;
        if (*p == '%') { buf_putc(&b, '%'); continue; }
        buf_puts(&b, ai < n ? val_text(args[ai++]) : "(null)");
    }
    if (sev <= 10) return P_OK;                       /* informational message */
    if (!s->failed) {                                 /* the application's own text, as the server sent it */
        s->failed = 1;
        snprintf(s->msg, sizeof s->msg, DRV "%s", buf_cstr(&b));
    }
    return P_ERR;
}

static int run_plain(Sess *s, Run *r, int i, int end, int run) {
    if (!run) return P_OK;
    char *sql;
    if (kw(&r->t[i], "TRUNCATE")) {
        int j = i + 1;
        if (kw(&r->t[j], "TABLE")) j++;
        char *rest = subst(s, r, j, end);
        if (!rest) return P_ERR;
        sql = kprintf("DELETE FROM %s", rest);
    } else if (!(sql = subst(s, r, i, end))) return P_ERR;
    Query *q; long aff;
    int isselect = kw(&r->t[i], "SELECT") || pu(&r->t[i], "(");
    if (!run_sql(s, r, i, sql, 0, &q, &aff)) return P_ERR;
    if (isselect && q) {
        q->sql = sql;
        push_set(s, q);
        s->last = q;
        s->rowcount = q->nrows;
    } else s->rowcount = aff;
    s->affected = isselect && q ? q->nrows : aff;
    return P_OK;
}

static int create_proc(Sess *s, const char *text, int alter);
static int drop_proc(Sess *s, Run *r, int i, int end, int run);

static int run_stmt(Sess *s, Run *r, int *pi, int run) {
    int i = *pi;
    PTok *t = r->t;
    while (pu(&t[i], ";")) i++;
    PTok *k = &t[i];
    if (k->t == PT_EOF) { *pi = i; return P_OK; }

    if (kw(k, "BEGIN") && !is_tran_word(&t[i + 1])) {
        i++;
        int flow = P_OK;
        for (;;) {
            while (pu(&t[i], ";")) i++;
            if (kw(&t[i], "END")) { i++; break; }
            if (t[i].t == PT_EOF) { perr(s, r, i, "Syntax error: BEGIN without a matching END."); return P_ERR; }
            int f = run_stmt(s, r, &i, run && flow == P_OK);
            if (f == P_ERR) return P_ERR;
            if (run && flow == P_OK) flow = f;
        }
        *pi = i;
        return run ? flow : P_OK;
    }
    if (kw(k, "IF") || kw(k, "WHILE")) {
        int isloop = kw(k, "WHILE");
        int c0 = i + 1, c1 = cond_end(r, c0);
        if (c1 == c0 || t[c1].t == PT_EOF || kw(&t[c1], "END") || kw(&t[c1], "ELSE")) { syntax(s, r, c1); return P_ERR; }
        if (!isloop) {
            int take = 0;
            if (run && !eval_cond(s, r, c0, c1, &take)) return P_ERR;
            i = c1;
            int f = run_stmt(s, r, &i, run && take);
            if (f == P_ERR) return P_ERR;
            int flow = run && take ? f : P_OK;
            int j = i;
            while (pu(&t[j], ";")) j++;
            if (kw(&t[j], "ELSE")) {
                i = j + 1;
                int f2 = run_stmt(s, r, &i, run && !take);
                if (f2 == P_ERR) return P_ERR;
                if (run && !take) flow = f2;
            }
            *pi = i;
            return flow;
        }
        int flow = P_OK;
        r->loopdepth++;
        while (run) {
            int b;
            if (!eval_cond(s, r, c0, c1, &b)) return P_ERR;
            if (!b) break;
            if (++s->loops > MAX_LOOPS) { perr(s, r, i, "WHILE loop exceeded %d iterations.", MAX_LOOPS); return P_ERR; }
            int j = c1;
            int f = run_stmt(s, r, &j, 1);
            if (f == P_ERR) return P_ERR;
            if (f == P_BRK) break;
            if (f == P_RET) { flow = P_RET; break; }
        }
        int j = c1;
        if (run_stmt(s, r, &j, 0) == P_ERR) return P_ERR;
        r->loopdepth--;
        *pi = j;
        return flow;
    }
    if (kw(k, "END") || kw(k, "ELSE")) { syntax(s, r, i); return P_ERR; }

    int next, end = stmt_end(r, i, &next);
    *pi = next;
    if (kw(k, "BREAK") || kw(k, "CONTINUE")) {
        if (!r->loopdepth) {
            perr(s, r, i, "Cannot use a %s statement outside the scope of a WHILE statement.", kf_upper(k->text));
            return P_ERR;
        }
        if (end != i + 1) { syntax(s, r, i + 1); return P_ERR; }
        return run ? (kw(k, "BREAK") ? P_BRK : P_CONT) : P_OK;
    }
    if (kw(k, "RETURN")) {
        if (!run) return P_OK;
        r->returned = 1;
        r->ret = 0;
        if (end > i + 1) {
            Val v; double d;
            if (!eval_range(s, r, i + 1, end, &v)) return P_ERR;
            if (v.t != VT_NULL) {
                if (!strict_num(v, &d)) { perr(s, r, i, "Conversion failed when converting the value '%.60s' to data type int.", val_text(v)); return P_ERR; }
                r->ret = d < 0 ? ceil(d) : floor(d);
            }
        }
        return P_RET;
    }
    if (kw(k, "DECLARE")) return do_declare(s, r, i, end, run);
    if (kw(k, "SET")) return do_set(s, r, i, end, run);
    if (kw(k, "PRINT")) return end > i + 1 ? P_OK : (syntax(s, r, end), P_ERR);
    if (kw(k, "RAISERROR")) return do_raiserror(s, r, i, end, run);
    if (kw(k, "EXEC") || kw(k, "EXECUTE")) return run_exec_stmt(s, r, i, end, run);
    if (pu(k, "{") || kw(k, "CALL")) return run_odbc_call(s, r, i, end, run);
    if (kw(k, "ROLLBACK")) {
        if (!run) return P_OK;
        perr(s, r, i, "ROLLBACK is not supported by this driver; wrap the call in CFTRANSACTION and use CFTRANSACTION ACTION=\"ROLLBACK\".");
        return P_ERR;
    }
    if (kw(k, "GO") || kw(k, "COMMIT") || kw(k, "SAVE") || kw(k, "BEGIN")) return P_OK;   /* BEGIN TRAN / COMMIT: CFTRANSACTION does that */
    if ((kw(k, "CREATE") || kw(k, "ALTER")) && (kw(&t[i + 1], "PROCEDURE") || kw(&t[i + 1], "PROC"))) {
        perr(s, r, i, "'CREATE/ALTER PROCEDURE' must be the first statement in a query batch.");
        return P_ERR;
    }
    if (kw(k, "DROP") && (kw(&t[i + 1], "PROCEDURE") || kw(&t[i + 1], "PROC"))) return drop_proc(s, r, i, end, run);
    if (kw(k, "SELECT")) {
        int j = i + 1;
        for (;;) {
            if (kw(&t[j], "DISTINCT") || kw(&t[j], "ALL")) j++;
            else if (kw(&t[j], "TOP")) {
                j++;
                if (pu(&t[j], "(")) { while (t[j].t != PT_EOF && !pu(&t[j], ")")) j++; }
                if (t[j].t != PT_EOF) j++;
                if (kw(&t[j], "PERCENT")) j++;
            } else break;
        }
        if (t[j].t == PT_VAR && pu(&t[j + 1], "=")) return do_select_assign(s, r, i, j, end, run);
        return run_plain(s, r, i, end, run);
    }
    if (kw(k, "INSERT") || kw(k, "UPDATE") || kw(k, "DELETE") || kw(k, "CREATE") || kw(k, "DROP") ||
        kw(k, "ALTER") || kw(k, "TRUNCATE") || pu(k, "("))
        return run_plain(s, r, i, end, run);
    syntax(s, r, i);
    return P_ERR;
}

/* run statements from token `from` to the end of the text */
static int run_body(Sess *s, Run *r, int from, int run) {
    int i = from, flow = P_OK;
    while (r->t[i].t != PT_EOF) {
        int f = run_stmt(s, r, &i, run && flow == P_OK);
        if (f == P_ERR) return P_ERR;
        if (run && flow == P_OK && f == P_RET) flow = P_RET;
    }
    return run ? flow : P_OK;
}

/* an ad-hoc batch (CFQUERY text, EXEC('...')) with its own variables */
static int run_batch_text(Sess *s, Run *parent, int at, const char *text) {
    TV tv;
    char err[512];
    if (!ptokenize(text, &tv, err, sizeof err)) { perr_raw(s, parent, at, err); return 0; }
    Run r; memset(&r, 0, sizeof r);
    r.src = text; r.t = tv.v; r.n = tv.n;
    r.depth = parent ? parent->depth + 1 : 0;
    if (r.depth > MAX_NEST) { perr(s, parent, at, "Maximum stored procedure nesting level exceeded (limit %d).", MAX_NEST); return 0; }
    if (run_body(s, &r, 0, 0) == P_ERR) return 0;       /* syntax check first: nothing runs on a typo */
    return run_body(s, &r, 0, 1) != P_ERR;
}

/* ================================================================ DDL */
static int write_proc_file(Sess *s, const char *path, const char *text) {
    char *tmp = kprintf("%s.tmp%d", path, (int)getpid());
    if (!kf_write_file(tmp, text, strlen(text), 0) || rename(tmp, path) != 0) {
        unlink(tmp);
        perr(s, NULL, -1, "Could not write the procedure file %s.", path);
        return 0;
    }
    return 1;
}

static int create_proc(Sess *s, const char *text, int alter) {
    ProcDef pd; memset(&pd, 0, sizeof pd);
    char err[512];
    while (isspace((unsigned char)*text)) text++;
    pd.src = kf_trim(text);
    size_t l = strlen(pd.src);
    while (l && (pd.src[l - 1] == ';' || isspace((unsigned char)pd.src[l - 1]))) pd.src[--l] = 0;
    /* a trailing GO line belongs to the script, not the procedure */
    if (l > 2 && !kf_stricmp(pd.src + l - 2, "GO") && (pd.src[l - 3] == '\n' || pd.src[l - 3] == '\r')) {
        pd.src[l - 2] = 0;
        pd.src = kf_trim(pd.src);
    }
    if (!ptokenize(pd.src, &pd.tv, err, sizeof err)) { perr_raw(s, NULL, -1, err); return 0; }
    Run r; memset(&r, 0, sizeof r);
    r.src = pd.src; r.t = pd.tv.v; r.n = pd.tv.n;
    if (!parse_header(s, &r, &pd)) return 0;
    r.proc = pd.name;
    if (run_body(s, &r, pd.body, 0) == P_ERR) return 0;           /* syntax check */
    char *path = proc_file(s->dbdir, pd.name);
    if (alter && !path) { perr(s, NULL, -1, "Cannot alter the procedure '%s', because it does not exist.", pd.name); return 0; }
    if (!alter && (path || table_exists(s->dbdir, pd.name))) {
        perr(s, NULL, -1, "There is already an object named '%s' in the database.", pd.name);
        return 0;
    }
    if (!path) path = kf_path_join(s->dbdir, kprintf("%s.prc", pd.name));
    const char *out = pd.src;
    if (alter) out = kprintf("CREATE%s", pd.src + 5);     /* stored as CREATE ... */
    return write_proc_file(s, path, kprintf("%s\n", out));
}

static int drop_proc(Sess *s, Run *r, int i, int end, int run) {
    int j = i + 2, ifx = 0;
    if (kw(&r->t[j], "IF") && kw(&r->t[j + 1], "EXISTS")) { ifx = 1; j += 2; }
    for (;;) {
        char *name = parse_qname(s, r, &j);
        if (!name) return P_ERR;
        if (run) {
            char *path = proc_file(s->dbdir, name);
            if (!path) {
                if (!ifx) { perr(s, r, i, "Cannot drop the procedure '%s', because it does not exist or you do not have permission.", name); return P_ERR; }
            } else if (unlink(path) != 0) { perr(s, r, i, "Could not delete the procedure file for '%s'.", name); return P_ERR; }
        }
        if (j >= end) break;
        if (!pu(&r->t[j], ",")) { syntax(s, r, j); return P_ERR; }
        j++;
    }
    return P_OK;
}

/* ================================================================ public API */
static int starts_proc_ddl(const PTok *t, int *alter) {
    *alter = kw(&t[0], "ALTER");
    return (kw(&t[0], "CREATE") || kw(&t[0], "ALTER")) && (kw(&t[1], "PROCEDURE") || kw(&t[1], "PROC"));
}

size_t sqlproc_extent(const char *text) {
    /* cheap test first: this runs for every statement of every script */
    const char *p = text;
    if (!kf_strnicmp(p, "CREATE", 6)) p += 6;
    else if (!kf_strnicmp(p, "ALTER", 5)) p += 5;
    else return 0;
    if (!isspace((unsigned char)*p) && *p != '/' && *p != '-') return 0;
    for (;;) {
        while (isspace((unsigned char)*p)) p++;
        if (p[0] == '-' && p[1] == '-') { while (*p && *p != '\n') p++; continue; }
        if (p[0] == '/' && p[1] == '*') { const char *e = strstr(p + 2, "*/"); p = e ? e + 2 : p + strlen(p); continue; }
        break;
    }
    if (kf_strnicmp(p, "PROC", 4) || (is_wchar((unsigned char)p[4]) && (kf_strnicmp(p, "PROCEDURE", 9) || is_wchar((unsigned char)p[9]))))
        return 0;
    Arena *caller = g_arena, *work = arena_new();
    g_arena = work;
    TV tv;
    size_t len = 0;
    int alter;
    ptokenize(text, &tv, NULL, 0);
    if (tv.n > 2 && starts_proc_ddl(tv.v, &alter)) {
        len = strlen(text);
        int i = 2, depth = 0;
        while (tv.v[i].t != PT_EOF && !(depth == 0 && kw(&tv.v[i], "AS") && tv.v[i - 1].t != PT_VAR)) {
            if (pu(&tv.v[i], "(")) depth++;
            else if (pu(&tv.v[i], ")")) depth--;
            i++;
        }
        if (tv.v[i].t != PT_EOF) i++;
        if (kw(&tv.v[i], "BEGIN")) {
            int nest = 0;
            for (; tv.v[i].t != PT_EOF; i++) {
                if ((kw(&tv.v[i], "BEGIN") && !is_tran_word(&tv.v[i + 1])) || kw(&tv.v[i], "CASE")) nest++;
                else if (kw(&tv.v[i], "END") && --nest == 0) { len = (size_t)tv.v[i].end; break; }
            }
        } else {
            for (; tv.v[i].t != PT_EOF; i++) {
                if (!kw(&tv.v[i], "GO")) continue;
                int a = tv.v[i].pos, b = tv.v[i].end;
                while (a > 0 && (text[a - 1] == ' ' || text[a - 1] == '\t')) a--;
                while (text[b] == ' ' || text[b] == '\t' || text[b] == '\r') b++;
                if ((a == 0 || text[a - 1] == '\n') && (text[b] == '\n' || !text[b])) { len = (size_t)b; break; }
            }
        }
    }
    g_arena = caller;
    arena_free(work);
    return len;
}

static void sess_init(Sess *s, const char *dbdir) {
    memset(s, 0, sizeof *s);
    s->dbdir = dbdir && *dbdir ? dbdir : ".";
}

static void put_err(Sess *s, char *err, size_t errlen) {
    if (err && errlen) snprintf(err, errlen, "%s", s->msg);
}

/* the statement as a CFQUERY-level result: copied into the caller's arena */
static int finish(Sess *s, Arena *caller, Arena *work, int ok, Query **out, long *affected, char *err, size_t errlen) {
    g_arena = caller;
    if (ok) {
        if (out) *out = s->last ? query_copy(s->last) : NULL;
        if (affected) *affected = s->affected;
    } else put_err(s, err, errlen);
    arena_free(work);
    return ok;
}

int sqlproc_statement(const char *dbdir, const char *stmt, Query **out, long *affected, char *err, size_t errlen) {
    const char *p = stmt;
    while (isspace((unsigned char)*p)) p++;
    static const char *lead[] = {"CREATE", "ALTER", "DROP", "EXEC", "EXECUTE", "CALL", "GO", "TRUNCATE", "COMMIT", "ROLLBACK", NULL};
    int hit = *p == '{';
    for (int i = 0; !hit && lead[i]; i++) {
        size_t l = strlen(lead[i]);
        if (!kf_strnicmp(p, lead[i], l) && !is_wchar((unsigned char)p[l])) hit = 1;
    }
    if (!hit) return -1;
    if (out) *out = NULL;
    if (affected) *affected = 0;
    Arena *caller = g_arena, *work = arena_new();
    g_arena = work;
    Sess s; sess_init(&s, dbdir);
    TV tv;
    char e2[512];
    int ok;
    if (!ptokenize(p, &tv, e2, sizeof e2)) { g_arena = caller; arena_free(work); return -1; }   /* let sql.c report it */
    PTok *t = tv.v;
    int alter;
    if (starts_proc_ddl(t, &alter)) ok = create_proc(&s, p, alter);
    else if (kw(&t[0], "DROP") && (kw(&t[1], "PROCEDURE") || kw(&t[1], "PROC"))) {
        Run r; memset(&r, 0, sizeof r);
        r.src = p; r.t = t; r.n = tv.n;
        int next, end = stmt_end(&r, 0, &next);
        ok = drop_proc(&s, &r, 0, end, 1) != P_ERR;
        if (ok && t[next].t != PT_EOF) { syntax(&s, &r, next); ok = 0; }
    } else if (kw(&t[0], "CREATE") || kw(&t[0], "ALTER") || kw(&t[0], "DROP")) {
        g_arena = caller; arena_free(work);
        return -1;
    } else ok = run_batch_text(&s, NULL, -1, p);
    return finish(&s, caller, work, ok, out, affected, err, errlen);
}

int sqlproc_batch(const char *dbdir, const char *sql, Query **out, long *affected, char *err, size_t errlen) {
    const char *p = sql;
    while (isspace((unsigned char)*p)) p++;
    if (!kf_strnicmp(p, "CREATE", 6) || !kf_strnicmp(p, "ALTER", 5)) return -1;   /* DDL scripts: statement by statement */
    if (!strchr(p, '@') && *p != '{') {
        static const char *lead[] = {"DECLARE", "IF", "WHILE", "BEGIN", "PRINT", "RAISERROR", "RETURN", "COMMIT", NULL};
        int hit = 0;
        for (int i = 0; !hit && lead[i]; i++) {
            size_t l = strlen(lead[i]);
            if (!kf_strnicmp(p, lead[i], l) && !is_wchar((unsigned char)p[l])) hit = 1;
        }
        if (!hit) return -1;
    }
    Arena *caller = g_arena, *work = arena_new();
    g_arena = work;
    TV tv;
    char e2[512];
    int tsql = 0;
    if (ptokenize(p, &tv, e2, sizeof e2)) {
        int alter;
        if (tv.n > 1 && starts_proc_ddl(tv.v, &alter)) tsql = 0;
        else if (*p == '{') tsql = 1;
        else for (int i = 0; i < tv.n && !tsql; i++) {
            if (tv.v[i].t == PT_VAR) tsql = 1;
            /* @@ROWCOUNT, @@NESTLEVEL, ... need the interpreter; @@IDENTITY / @@VERSION the engine knows */
            if (tv.v[i].t == PT_GVAR && kf_stricmp(tv.v[i].text, "IDENTITY") && kf_stricmp(tv.v[i].text, "VERSION")) tsql = 1;
            if (i == 0 && (kw(&tv.v[0], "DECLARE") || kw(&tv.v[0], "IF") || kw(&tv.v[0], "WHILE") || kw(&tv.v[0], "PRINT") ||
                           kw(&tv.v[0], "RAISERROR") || kw(&tv.v[0], "RETURN") || kw(&tv.v[0], "BEGIN") ||
                           kw(&tv.v[0], "COMMIT"))) tsql = 1;
        }
        for (int i = 0; i + 1 < tv.n && tsql; i++)        /* a script that creates procedures goes statement by statement */
            if ((kw(&tv.v[i], "CREATE") || kw(&tv.v[i], "ALTER")) && (kw(&tv.v[i + 1], "PROCEDURE") || kw(&tv.v[i + 1], "PROC"))) tsql = 0;
    }
    if (!tsql) { g_arena = caller; arena_free(work); return -1; }
    Sess s; sess_init(&s, dbdir);
    int ok = run_batch_text(&s, NULL, -1, p);
    return finish(&s, caller, work, ok, out, affected, err, errlen);
}

int sql_call_procedure(const char *dbdir, const char *proc, SqlParam *params, int nparams,
                       SqlProcResult *res, char *err, size_t errlen) {
    memset(res, 0, sizeof *res);
    if (err && errlen) err[0] = 0;
    Arena *caller = g_arena, *work = arena_new();
    g_arena = work;
    Sess s; sess_init(&s, dbdir);
    CallArg *args = kmalloc(sizeof(CallArg) * (nparams + 1));
    for (int i = 0; i < nparams; i++) {
        args[i].name = params[i].name && *params[i].name ? params[i].name : NULL;
        args[i].output = params[i].dir == SQL_PARAM_OUT || params[i].dir == SQL_PARAM_INOUT;
        args[i].use_default = params[i].use_default;
        args[i].value = params[i].dir == SQL_PARAM_OUT ? v_null() : params[i].value;
    }
    /* "dbo.Proc" / "Proc;1" are accepted like in an EXEC */
    const char *name = proc;
    const char *dot = strrchr(name, '.');
    if (dot) name = dot + 1;
    char *nm = kstrndup(name, strcspn(name, ";"));
    double status = 0;
    int ok = call_proc(&s, NULL, -1, kf_trim(nm), args, nparams, &status);
    g_arena = caller;
    if (ok) {
        res->sets = kmalloc(sizeof(Query *) * (s.nsets + 1));
        for (int i = 0; i < s.nsets; i++) res->sets[i] = query_copy(s.sets[i]);
        res->nsets = s.nsets;
        res->status = status;
        res->affected = s.affected;
        for (int i = 0; i < nparams; i++) {
            params[i].has_out = args[i].has_out;
            params[i].out = args[i].has_out ? v_deepcopy(args[i].out) : v_null();
        }
    } else put_err(&s, err, errlen);
    arena_free(work);
    return ok;
}

static int name_cmp(const void *a, const void *b) { return kf_stricmp(*(char *const *)a, *(char *const *)b); }

int sql_list_procedures(const char *dbdir, Query **out, char *err, size_t errlen) {
    const char *cols[] = {"PROCEDURE_NAME", "PARAMETERS", "PARAMETER_COUNT", "SOURCE"};
    if (err && errlen) err[0] = 0;
    DIR *d = opendir(dbdir && *dbdir ? dbdir : ".");
    if (!d) { if (err) snprintf(err, errlen, DRV "Data source directory '%s' not found.", dbdir); return 0; }
    Query *q = query_new(4, cols);
    char **names = NULL; int n = 0, cap = 0;
    struct dirent *de;
    while ((de = readdir(d))) {
        size_t l = strlen(de->d_name);
        if (l <= 4 || strcmp(de->d_name + l - 4, ".prc")) continue;
        if (n == cap) { cap = cap ? cap * 2 : 16; char **nn = kmalloc(sizeof(char *) * cap); if (n) memcpy(nn, names, sizeof(char *) * n); names = nn; }
        names[n++] = kstrndup(de->d_name, l - 4);
    }
    closedir(d);
    if (n) qsort(names, n, sizeof(char *), name_cmp);
    Arena *caller = g_arena;
    for (int i = 0; i < n; i++) {
        Arena *work = arena_new();
        g_arena = work;
        Sess s; sess_init(&s, dbdir);
        ProcDef *pd = load_proc(&s, NULL, -1, names[i]);
        Buf b; buf_init(&b);
        if (pd)
            for (int k = 0; k < pd->np; k++)
                buf_printf(&b, "%s@%s %s%s%.*s%s", k ? ", " : "", pd->p[k].name, pd->p[k].ty.tname,
                           pd->p[k].has_def ? " = " : "",
                           pd->p[k].has_def ? pd->tv.v[pd->p[k].d1 - 1].end - pd->tv.v[pd->p[k].d0].pos : 0,
                           pd->p[k].has_def ? pd->src + pd->tv.v[pd->p[k].d0].pos : "",
                           pd->p[k].output ? " OUTPUT" : "");
        g_arena = caller;
        int row = query_add_row(q);
        query_set(q, 0, row, v_strdup(pd ? pd->name : names[i]));
        query_set(q, 1, row, v_strdup(pd ? buf_cstr(&b) : "(invalid procedure file)"));
        query_set(q, 2, row, v_num(pd ? pd->np : 0));
        query_set(q, 3, row, v_strdup(pd ? pd->src : s.msg));
        arena_free(work);
    }
    if (out) *out = q;
    return 1;
}

int sql_seed_procedures(const char *dbdir, const char *script, char *err, size_t errlen) {
    if (err && errlen) err[0] = 0;
    if (!script) return 1;
    Arena *caller = g_arena, *work = arena_new();
    g_arena = work;
    TV tv;
    int ok = 1;
    ptokenize(script, &tv, NULL, 0);
    for (int i = 0; i + 2 < tv.n && ok; i++) {
        int alter;
        if (!starts_proc_ddl(&tv.v[i], &alter)) continue;
        if (i > 0 && !pu(&tv.v[i - 1], ";") && !kw(&tv.v[i - 1], "GO") && !kw(&tv.v[i - 1], "END")) continue;
        const char *at = script + tv.v[i].pos;
        size_t len = sqlproc_extent(at);
        if (!len) continue;
        Sess s; sess_init(&s, dbdir);
        Run r; memset(&r, 0, sizeof r);
        r.src = script; r.t = tv.v; r.n = tv.n;
        int j = i + 2;
        char *name = parse_qname(&s, &r, &j);
        if (name && !proc_file(s.dbdir, name)) {
            ok = create_proc(&s, kstrndup(at, len), 0);
            if (!ok) put_err(&s, err, errlen);
        }
        int start = tv.v[i].pos;
        while (i + 1 < tv.n && tv.v[i + 1].pos < start + (int)len) i++;
    }
    g_arena = caller;
    arena_free(work);
    return ok;
}
