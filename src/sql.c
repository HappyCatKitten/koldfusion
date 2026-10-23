/*
 * sql.c - the KoldFusion Flat-File Driver.
 *
 * A small SQL engine in the spirit of the Access/Jet + ODBC stack that 1999
 * CFML applications talked to. Each database is a directory, each table one
 * human-readable text file:
 *
 *     #KFTABLE 1
 *     Emp_ID:COUNTER:AUTOINC:PK<TAB>FirstName:VARCHAR(50)<TAB>StartDate:DATE ...
 *     26                                  <- next auto-increment value
 *     1<TAB>Carol<TAB>1997-03-14          <- one row per line
 *
 * Fields are tab separated; \t \n \r \\ are escaped and \N is NULL. Column
 * definitions are Name:TYPE followed by optional flags AUTOINC, PK, NOTNULL,
 * UNIQUE and finally DEFAULT=<sql expression>. Writes go to a temp file that
 * is renamed over the table, so readers never see half a table.
 *
 * Pipeline for one statement: lex -> parse (AST) -> bind (load tables,
 * resolve column references, expand *) -> execute. Everything temporary
 * lives in a private arena that is thrown away when the statement is done;
 * the result Query is copied into the caller's g_arena at the very end,
 * after the global lock is released, so an arena-limit error in the caller
 * can never leave the lock held. Parsed tables are cached (keyed by path,
 * inode, size and mtime) in arenas of their own and are never mutated: a
 * write builds a new row list, saves it and drops the cache entry.
 */
#define _GNU_SOURCE
#include "sql.h"
#include <stdlib.h>
#include <ctype.h>
#include <math.h>
#include <errno.h>
#include <pthread.h>
#include <dirent.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>

#define DRV        "[Gibson][KoldFusion Flat-File Driver] "
#define MAX_SRC    64            /* tables per SELECT (bitmask width) */
#define CACHE_MAX  64            /* parsed tables kept in memory */
#ifndef KF_SQL_FSYNC
#define KF_SQL_FSYNC 1           /* fsync table files before the rename */
#endif

/* grow-by-doubling push for arrays that are only ever appended with VPUSH:
 * capacity is implicitly the next power of two above n */
#define VPUSH(arr, n, item) do {                                            \
        if (((n) & ((n) - 1)) == 0) {                                       \
            int nc_ = (n) ? (n) * 2 : 4;                                    \
            void *na_ = kmalloc(sizeof(*(arr)) * nc_);                      \
            if (n) memcpy(na_, (arr), sizeof(*(arr)) * (n));                \
            (arr) = na_;                                                    \
        }                                                                   \
        (arr)[(n)++] = (item);                                              \
    } while (0)

/* ================================================================ errors */
typedef struct Exec {
    int  failed;
    char msg[1024];
    const char *dbdir;
} Exec;

static void xerr(Exec *x, const char *fmt, ...) __attribute__((format(printf, 2, 3)));
static void xerr(Exec *x, const char *fmt, ...) {
    if (x->failed) return;                 /* keep the first (root cause) error */
    x->failed = 1;
    size_t n = strlen(DRV);
    memcpy(x->msg, DRV, n);
    va_list ap; va_start(ap, fmt);
    vsnprintf(x->msg + n, sizeof x->msg - n, fmt, ap);
    va_end(ap);
}

/* ================================================================ globals */
static pthread_mutex_t g_lock = PTHREAD_MUTEX_INITIALIZER;
static unsigned long   g_serial;                 /* statement counter (cache pinning) */
static __thread double g_identity;               /* SELECT @@IDENTITY */
static __thread int    g_have_identity;

/* ========================================================= storage types */
enum { CT_INT = 1, CT_FLOAT, CT_TEXT, CT_DATE, CT_BIT };

typedef struct ColDef {
    char *name;
    char *tname;              /* declared type, e.g. "VARCHAR(50)", "COUNTER" */
    char *defexpr;            /* DEFAULT expression source text or NULL */
    int   ct;                 /* CT_* storage class */
    int   size;               /* max characters for sized text, 0 = unlimited */
    int   scale;              /* decimal places to round to, -1 = none */
    int   autoinc, pk, notnull, unique;
} ColDef;

typedef struct Table {
    char   *name, *path;
    int     ncols;
    ColDef *cols;
    double  nextid;           /* next auto-increment value */
    int     nrows, rowcap;
    Val   **rows;             /* rows[r][c]; VT_NULL, VT_NUM, VT_STR or VT_DATE */
} Table;

static const struct { const char *name; int ct, autoinc, scale, kind; } TYPES[] = {
    /* kind: 0 plain, 1 sized text "(n)", 2 decimal "(p,s)" */
    {"INTEGER", CT_INT, 0, -1, 0}, {"INT", CT_INT, 0, -1, 0}, {"LONG", CT_INT, 0, -1, 0},
    {"SMALLINT", CT_INT, 0, -1, 0}, {"TINYINT", CT_INT, 0, -1, 0}, {"BIGINT", CT_INT, 0, -1, 0},
    {"BYTE", CT_INT, 0, -1, 0}, {"SHORT", CT_INT, 0, -1, 0}, {"MEDIUMINT", CT_INT, 0, -1, 0},
    {"COUNTER", CT_INT, 1, -1, 0}, {"AUTOINCREMENT", CT_INT, 1, -1, 0}, {"AUTONUMBER", CT_INT, 1, -1, 0},
    {"IDENTITY", CT_INT, 1, -1, 0}, {"SERIAL", CT_INT, 1, -1, 0},
    {"VARCHAR", CT_TEXT, 0, -1, 1}, {"CHAR", CT_TEXT, 0, -1, 1}, {"NVARCHAR", CT_TEXT, 0, -1, 1},
    {"NCHAR", CT_TEXT, 0, -1, 1}, {"CHARACTER", CT_TEXT, 0, -1, 1}, {"VARCHAR2", CT_TEXT, 0, -1, 1},
    {"STRING", CT_TEXT, 0, -1, 1}, {"TEXT", CT_TEXT, 0, -1, 1}, {"MEMO", CT_TEXT, 0, -1, 0},
    {"LONGTEXT", CT_TEXT, 0, -1, 0}, {"MEDIUMTEXT", CT_TEXT, 0, -1, 0}, {"NTEXT", CT_TEXT, 0, -1, 0},
    {"LONGCHAR", CT_TEXT, 0, -1, 0}, {"CLOB", CT_TEXT, 0, -1, 0}, {"HYPERLINK", CT_TEXT, 0, -1, 0},
    {"FLOAT", CT_FLOAT, 0, -1, 0}, {"DOUBLE", CT_FLOAT, 0, -1, 0}, {"REAL", CT_FLOAT, 0, -1, 0},
    {"SINGLE", CT_FLOAT, 0, -1, 0}, {"NUMERIC", CT_FLOAT, 0, -1, 2}, {"DECIMAL", CT_FLOAT, 0, -1, 2},
    {"DEC", CT_FLOAT, 0, -1, 2}, {"NUMBER", CT_FLOAT, 0, -1, 2},
    {"MONEY", CT_FLOAT, 0, 4, 0}, {"CURRENCY", CT_FLOAT, 0, 4, 0}, {"SMALLMONEY", CT_FLOAT, 0, 4, 0},
    {"DATE", CT_DATE, 0, -1, 0}, {"DATETIME", CT_DATE, 0, -1, 0}, {"TIME", CT_DATE, 0, -1, 0},
    {"TIMESTAMP", CT_DATE, 0, -1, 0}, {"SMALLDATETIME", CT_DATE, 0, -1, 0},
    {"BIT", CT_BIT, 0, -1, 0}, {"YESNO", CT_BIT, 0, -1, 0}, {"BOOLEAN", CT_BIT, 0, -1, 0},
    {"BOOL", CT_BIT, 0, -1, 0}, {"LOGICAL", CT_BIT, 0, -1, 0},
};

/* Fill ct/size/scale (and autoinc for COUNTER-like types) from a declared
 * type string such as "VARCHAR(50)" or "NUMERIC(10,2)". 0 if unknown. */
static int coldef_set_type(ColDef *cd, const char *tname) {
    char base[32]; int i = 0;
    while (tname[i] && (isalnum((unsigned char)tname[i]) || tname[i] == '_') && i < 31) {
        base[i] = (char)toupper((unsigned char)tname[i]); i++;
    }
    base[i] = 0;
    for (size_t k = 0; k < sizeof TYPES / sizeof TYPES[0]; k++) {
        if (strcmp(TYPES[k].name, base)) continue;
        cd->ct = TYPES[k].ct;
        if (TYPES[k].autoinc) cd->autoinc = 1;
        cd->scale = TYPES[k].scale;
        cd->size = 0;
        const char *p = strchr(tname, '(');
        if (p) {
            char *e;
            long a = strtol(p + 1, &e, 10);
            if (TYPES[k].kind == 1 && a > 0) cd->size = (int)a;
            if (TYPES[k].kind == 2) cd->scale = (*e == ',') ? (int)strtol(e + 1, NULL, 10) : 0;
        }
        cd->tname = (char *)tname;
        return 1;
    }
    return 0;
}

/* ========================================================== value helpers */
static int is_null(Val v) { return v.t == VT_NULL; }
static Val vbool(int b) { return v_num(b ? 1 : 0); }       /* SQL booleans are 1/0 */

static char *fmt_date(double d) {
    int y, mo, dd, h, mi, s;
    date_to_parts(d, &y, &mo, &dd, &h, &mi, &s);
    return kprintf("%04d-%02d-%02d %02d:%02d:%02d", y, mo, dd, h, mi, s);
}

/* text form of a value (NULL -> "") */
static const char *sv_str(Val v) {
    switch (v.t) {
    case VT_NULL: return "";
    case VT_STR:  return v.u.str.s;
    case VT_NUM:  return fmt_number(v.u.n);
    case VT_BOOL: return v.u.b ? "1" : "0";
    case VT_DATE: return fmt_date(v.u.n);
    default:      return "";
    }
}

/* lenient numeric view: numbers, dates, bools, numeric text, yes/no/true/false */
static int sv_num(Val v, double *out) {
    switch (v.t) {
    case VT_NUM: case VT_DATE: *out = v.u.n; return 1;
    case VT_BOOL: *out = v.u.b; return 1;
    case VT_STR: return v_tonum(v, out);
    default: return 0;
    }
}

/* strict numeric view for arithmetic: text must look like a number */
static int num_of(Val v, double *out) {
    switch (v.t) {
    case VT_NUM: case VT_DATE: *out = v.u.n; return 1;
    case VT_BOOL: *out = v.u.b; return 1;
    case VT_STR: return v_isnumeric_str(v.u.str.s, out);
    default: return 0;
    }
}

static int sv_date(Val v, double *out) {
    switch (v.t) {
    case VT_DATE: case VT_NUM: *out = v.u.n; return 1;
    case VT_STR: return date_parse(v.u.str.s, out);
    default: return 0;
    }
}

static int truthy(Val v) {
    double d; int b;
    if (v.t == VT_NULL) return 0;
    if (v.t == VT_STR) return v_tobool(v, &b) ? b : 0;
    return sv_num(v, &d) && d != 0;
}

static int is_blank(const char *s) { while (*s == ' ' || *s == '\t') s++; return *s == 0; }

/* case-insensitive compare ignoring trailing blanks (CHAR padding rules) */
static int str_cmp_ci(const char *a, const char *b) {
    size_t la = strlen(a), lb = strlen(b);
    while (la && a[la - 1] == ' ') la--;
    while (lb && b[lb - 1] == ' ') lb--;
    size_t n = la < lb ? la : lb;
    for (size_t i = 0; i < n; i++) {
        int ca = tolower((unsigned char)a[i]), cb = tolower((unsigned char)b[i]);
        if (ca != cb) return ca - cb;
    }
    return la < lb ? -1 : la > lb ? 1 : 0;
}

#define CMP3(x, y) ((x) < (y) ? -1 : (x) > (y) ? 1 : 0)

/* SQL comparison of two non-NULL values: numbers numerically, dates as
 * dates (text is parsed), numeric text against numbers numerically,
 * everything else as case-insensitive text. */
static int sql_cmp(Val a, Val b) {
    double x, y;
    int an = a.t == VT_NUM || a.t == VT_BOOL, bn = b.t == VT_NUM || b.t == VT_BOOL;
    if (an && bn) { sv_num(a, &x); sv_num(b, &y); return CMP3(x, y); }
    if ((a.t == VT_DATE || b.t == VT_DATE) && sv_date(a, &x) && sv_date(b, &y)) return CMP3(x, y);
    if (an && b.t == VT_STR && sv_num(b, &y)) { sv_num(a, &x); return CMP3(x, y); }
    if (bn && a.t == VT_STR && sv_num(a, &x)) { sv_num(b, &y); return CMP3(x, y); }
    return str_cmp_ci(sv_str(a), sv_str(b));
}

/* ordering with NULLs first (Jet / SQL Server behaviour) */
static int order_cmp(Val a, Val b) {
    if (is_null(a)) return is_null(b) ? 0 : -1;
    if (is_null(b)) return 1;
    return sql_cmp(a, b);
}

static long u8_len(const char *s) { long n = 0; for (; *s; s++) if ((*s & 0xC0) != 0x80) n++; return n; }
static size_t u8_off(const char *s, long n) {        /* byte offset of character n */
    size_t i = 0;
    while (s[i] && n > 0) { i++; while ((s[i] & 0xC0) == 0x80) i++; n--; }
    return i;
}

static double round_places(double d, int places) {
    double p = pow(10, places);
    double v = floor(fabs(d) * p + 0.5 + 1e-9) / p;
    return d < 0 ? -v : v;
}

/* ================================================================ sorting */
/* stable merge sort over elements of size sz; never misbehaves with an
 * inconsistent comparator (mixed-type columns), unlike some qsorts */
typedef int (*CmpFn)(const void *a, const void *b, void *ctx);

static void msort_rec(char *v, char *tmp, int n, size_t sz, CmpFn f, void *ctx) {
    if (n < 2) return;
    int h = n / 2;
    msort_rec(v, tmp, h, sz, f, ctx);
    msort_rec(v + h * sz, tmp, n - h, sz, f, ctx);
    int i = 0, j = h, k = 0;
    while (i < h && j < n) {
        if (f(v + j * sz, v + i * sz, ctx) < 0) memcpy(tmp + (k++) * sz, v + (j++) * sz, sz);
        else memcpy(tmp + (k++) * sz, v + (i++) * sz, sz);
    }
    while (i < h) memcpy(tmp + (k++) * sz, v + (i++) * sz, sz);
    while (j < n) memcpy(tmp + (k++) * sz, v + (j++) * sz, sz);
    memcpy(v, tmp, n * sz);
}
static void msort(void *base, int n, size_t sz, CmpFn f, void *ctx) {
    if (n < 2) return;
    char *tmp = kmalloc(sz * n);
    msort_rec(base, tmp, n, sz, f, ctx);
}

/* ================================================================== lexer */
enum { TK_EOF, TK_ID, TK_NUM, TK_STR, TK_DATE, TK_OP, TK_VAR };

typedef struct Tok {
    int    t;
    int    quoted;            /* TK_ID: 0 bare, 1 [bracketed]/`backtick`, 2 "double quoted" */
    int    pos, end;          /* byte span in the statement */
    char  *text;              /* identifier, string contents, operator, @@name */
    double num;               /* TK_NUM value / TK_DATE OLE date */
} Tok;

typedef struct Lexer { Tok *v; int n; } Lexer;

static Tok *lx_push(Lexer *L, int t, int pos, int end, char *text) {
    Tok k; memset(&k, 0, sizeof k);
    k.t = t; k.pos = pos; k.end = end; k.text = text;
    VPUSH(L->v, L->n, k);
    return &L->v[L->n - 1];
}

static int lex(Exec *x, const char *s, Tok **out, int *nout) {
    Lexer L = {NULL, 0};
    int n = (int)strlen(s), i = 0, fnskip = 0;
    for (;;) {
        while (i < n && isspace((unsigned char)s[i])) i++;
        if (i >= n) break;
        char c = s[i];
        int st = i;
        if (c == '-' && s[i + 1] == '-') { while (i < n && s[i] != '\n') i++; continue; }
        if (c == '/' && s[i + 1] == '*') {
            const char *e = strstr(s + i + 2, "*/");
            i = e ? (int)(e - s) + 2 : n;
            continue;
        }
        if (isalpha((unsigned char)c) || c == '_' || (unsigned char)c >= 0x80) {
            while (i < n && (isalnum((unsigned char)s[i]) || s[i] == '_' || s[i] == '$' || (unsigned char)s[i] >= 0x80)) i++;
            lx_push(&L, TK_ID, st, i, kstrndup(s + st, i - st));
        } else if (c == '[' || c == '`' || c == '"') {
            char close = c == '[' ? ']' : c;
            Buf b; buf_init(&b); i++;
            for (;;) {
                if (i >= n) { xerr(x, "Unterminated quoted name starting at '%.20s'.", s + st); return 0; }
                if (s[i] == close) {
                    if (c != '[' && s[i + 1] == close) { buf_putc(&b, close); i += 2; continue; }
                    i++; break;
                }
                buf_putc(&b, s[i++]);
            }
            Tok *k = lx_push(&L, TK_ID, st, i, buf_cstr(&b));
            k->quoted = c == '"' ? 2 : 1;
        } else if (c == '\'') {
            Buf b; buf_init(&b); i++;
            for (;;) {
                if (i >= n) { xerr(x, "Unterminated string in query expression '%.30s'.", s + st); return 0; }
                if (s[i] == '\'') {
                    if (s[i + 1] == '\'') { buf_putc(&b, '\''); i += 2; continue; }
                    i++; break;
                }
                buf_putc(&b, s[i++]);
            }
            lx_push(&L, TK_STR, st, i, buf_cstr(&b));
        } else if (isdigit((unsigned char)c) ||
                   (c == '.' && isdigit((unsigned char)s[i + 1]) &&
                    !(L.n && (L.v[L.n - 1].t == TK_ID || (L.v[L.n - 1].t == TK_OP && !strcmp(L.v[L.n - 1].text, ")")))))) {
            /* plain decimal number (no hex, no inf/nan) */
            while (i < n && isdigit((unsigned char)s[i])) i++;
            if (s[i] == '.') { i++; while (i < n && isdigit((unsigned char)s[i])) i++; }
            if ((s[i] == 'e' || s[i] == 'E') &&
                (isdigit((unsigned char)s[i + 1]) || ((s[i + 1] == '+' || s[i + 1] == '-') && isdigit((unsigned char)s[i + 2])))) {
                i += 2;
                while (i < n && isdigit((unsigned char)s[i])) i++;
            }
            char *txt = kstrndup(s + st, i - st);
            Tok *k = lx_push(&L, TK_NUM, st, i, txt);
            k->num = strtod(txt, NULL);
        } else if (c == '#') {
            /* Access date literal #10/22/1999# */
            const char *e = memchr(s + i + 1, '#', n - i - 1);
            double d;
            if (!e || e - (s + i) > 64 || !date_parse(kstrndup(s + i + 1, e - (s + i) - 1), &d)) {
                xerr(x, "Syntax error in date in query expression '%.30s'.", s + i);
                return 0;
            }
            i = (int)(e - s) + 1;
            lx_push(&L, TK_DATE, st, i, kstrndup(s + st, i - st))->num = d;
        } else if (c == '{') {
            /* ODBC escapes: {d '...'} {ts '...'} {t '...'} literals; {fn ...} and {oj ...} are unwrapped */
            int j = i + 1;
            while (j < n && isspace((unsigned char)s[j])) j++;
            int ws = j;
            while (j < n && isalpha((unsigned char)s[j])) j++;
            int wl = j - ws;
            if (wl == 2 && (!kf_strnicmp(s + ws, "fn", 2) || !kf_strnicmp(s + ws, "oj", 2))) {
                fnskip++; i = j; continue;
            }
            if ((wl == 1 && strchr("dDtT", s[ws])) || (wl == 2 && !kf_strnicmp(s + ws, "ts", 2))) {
                while (j < n && isspace((unsigned char)s[j])) j++;
                if (s[j] == '\'') {
                    int q0 = ++j;
                    while (j < n && s[j] != '\'') j++;
                    if (j < n) {
                        char *txt = kstrndup(s + q0, j - q0);
                        j++;
                        while (j < n && isspace((unsigned char)s[j])) j++;
                        double d;
                        if (s[j] == '}' && date_parse(txt, &d)) {
                            i = j + 1;
                            lx_push(&L, TK_DATE, st, i, kstrndup(s + st, i - st))->num = d;
                            continue;
                        }
                    }
                }
            }
            xerr(x, "Syntax error in SQL statement near '%.20s'.", s + i);
            return 0;
        } else if (c == '}' && fnskip > 0) {
            fnskip--; i++;
        } else if (c == '@' && s[i + 1] == '@') {
            i += 2;
            int b0 = i;
            while (i < n && (isalnum((unsigned char)s[i]) || s[i] == '_')) i++;
            lx_push(&L, TK_VAR, st, i, kstrndup(s + b0, i - b0));
        } else {
            static const char *two[] = {"<=", ">=", "<>", "!=", "||", "==", NULL};
            int done = 0;
            for (int k = 0; two[k]; k++) if (s[i] == two[k][0] && s[i + 1] == two[k][1]) {
                i += 2;
                lx_push(&L, TK_OP, st, i, kstrdup(!strcmp(two[k], "==") ? "=" : !strcmp(two[k], "!=") ? "<>" : two[k]));
                done = 1;
                break;
            }
            if (done) continue;
            if (!strchr("(),.*+-/%=<>&;\\", c)) {
                xerr(x, "Invalid character '%c' in SQL statement.", c);
                return 0;
            }
            i++;
            lx_push(&L, TK_OP, st, i, kstrndup(&c, 1));
        }
    }
    lx_push(&L, TK_EOF, n, n, "");
    *out = L.v; *nout = L.n;
    return 1;
}

/* ==================================================================== AST */
typedef struct Expr Expr;
typedef struct Select Select;

enum {
    E_LIT, E_COL, E_IDENTITY, E_NEG, E_NOT, E_ARITH, E_CONCAT, E_CMP, E_AND, E_OR,
    E_LIKE, E_INLIST, E_INSUB, E_EXISTS, E_SUBQ, E_BETWEEN, E_ISNULL, E_FUNC, E_AGG,
    E_CASE, E_CAST
};
enum { C_EQ = 1, C_NE, C_LT, C_LE, C_GT, C_GE };
enum { A_COUNT = 1, A_SUM, A_AVG, A_MIN, A_MAX, A_FIRST, A_LAST };

struct Expr {
    int     k;                /* E_* */
    int     op;               /* operator, comparison, aggregate or function id */
    int     neg;              /* NOT LIKE / NOT IN / NOT BETWEEN / IS NOT NULL / NOT EXISTS */
    int     distinct, star;   /* aggregates: COUNT(DISTINCT x), COUNT(*) */
    int     dq;               /* E_COL written "like this": falls back to a string literal */
    int     bound;
    Val     v;                /* E_LIT */
    char   *name, *qual;      /* column name/qualifier, function name */
    Expr   *a, *b, *c;
    Expr  **args; int nargs;
    Select *sub;
    ColDef *cd;               /* E_CAST target type */
    int     depth, src, col;  /* bound column: scope depth, source, column */
};

typedef struct SelItem { Expr *e; char *alias; int star; char *starqual; } SelItem;
typedef struct OrderItem { Expr *e; int desc; int outcol; } OrderItem;

typedef struct Src {
    char   *name, *alias;
    Table  *tab;              /* base table, or */
    Select *sub;              /* derived table (subquery in FROM) */
    int     ncols;
    char  **colnames;
    int     nrows;
    Val   **rows;             /* rows being scanned (set at execution time) */
} Src;

enum { J_LEAF, J_CROSS, J_INNER, J_LEFT, J_RIGHT };
typedef struct JoinNode { int kind; struct JoinNode *l, *r; Expr *on; int src; } JoinNode;

typedef struct ResultSet { int ncols; char **names; int nrows; Val **rows; } ResultSet;

struct Select {
    int         distinct, top_percent;
    double      top;                      /* -1 = none */
    SelItem   **items; int nitems;
    JoinNode  **from;  int nfrom;         /* comma separated join expressions */
    Src       **srcs;  int nsrc;
    Expr       *where, *having;
    Expr      **group; int ngroup;
    OrderItem **order; int norder;
    long        limit, offset;            /* -1 = none */
    Select     *parent;                   /* enclosing scope (correlated refs) */
    Select     *next; int union_all;      /* UNION chain */
    char      **outnames;
    int         has_agg, correlated, bound;
    ResultSet  *cache;                    /* result of an uncorrelated subquery */
    Expr      **conj; int nconj;          /* WHERE split on AND, for pushdown */
    uint64_t   *conjmask;
};

typedef struct ValRow { Expr **e; int n; } ValRow;

enum { ST_SELECT = 1, ST_INSERT, ST_UPDATE, ST_DELETE, ST_CREATE, ST_DROP, ST_ADDCOL, ST_DROPCOL, ST_NOOP };

typedef struct Stmt {
    int      kind;
    char    *table;
    int      ifx;                         /* IF [NOT] EXISTS */
    Select  *sel;                         /* SELECT / INSERT..SELECT / UPDATE+DELETE scope */
    Select  *scope;                       /* empty scope for INSERT VALUES */
    char   **cols; int ncols;             /* INSERT column list, UPDATE targets, DROP COLUMN */
    ValRow **vals; int nvals;             /* INSERT VALUES rows */
    Expr   **set;  int nset;              /* UPDATE expressions */
    ColDef **defs; int ndefs;             /* CREATE TABLE / ADD COLUMN */
    double   seed;                        /* IDENTITY(seed, inc) */
} Stmt;

/* ================================================================= parser */
typedef struct P { Exec *x; const char *sql; Tok *t; int n, i; } P;
#define CUR(p) (&(p)->t[(p)->i])

static const char *RESERVED[] = {
    "SELECT", "FROM", "WHERE", "GROUP", "HAVING", "ORDER", "BY", "UNION", "ALL", "DISTINCT",
    "INNER", "LEFT", "RIGHT", "OUTER", "CROSS", "JOIN", "ON", "AS", "AND", "OR",
    "NOT", "IN", "IS", "NULL", "LIKE", "BETWEEN", "EXISTS", "INTO", "VALUES", "SET",
    "LIMIT", "OFFSET", "CASE", "WHEN", "THEN", "ELSE", "END", "ASC", "DESC", "TOP", NULL
};
static int is_reserved(const char *s) {
    for (int i = 0; RESERVED[i]; i++) if (!kf_stricmp(RESERVED[i], s)) return 1;
    return 0;
}

static int is_kw(Tok *t, const char *kw) { return t->t == TK_ID && !t->quoted && !kf_stricmp(t->text, kw); }
static int at_kw(P *p, const char *kw) { return is_kw(CUR(p), kw); }
static int peek_kw(P *p, int ahead, const char *kw) { return p->i + ahead < p->n && is_kw(&p->t[p->i + ahead], kw); }
static int accept_kw(P *p, const char *kw) { if (at_kw(p, kw)) { p->i++; return 1; } return 0; }
static int is_op(Tok *t, const char *op) { return t->t == TK_OP && !strcmp(t->text, op); }
static int at_op(P *p, const char *op) { return is_op(CUR(p), op); }
static int accept_op(P *p, const char *op) { if (at_op(p, op)) { p->i++; return 1; } return 0; }

static void syntax_error(P *p) {
    Tok *k = CUR(p);
    if (k->t == TK_EOF) xerr(p->x, "Syntax error in SQL statement (unexpected end of statement).");
    else {
        int len = k->end - k->pos;
        xerr(p->x, "Syntax error in SQL statement near '%.*s'.", len > 40 ? 40 : len, p->sql + k->pos);
    }
}
static int expect_kw(P *p, const char *kw) { if (accept_kw(p, kw)) return 1; syntax_error(p); return 0; }
static int expect_op(P *p, const char *op) { if (accept_op(p, op)) return 1; syntax_error(p); return 0; }

/* identifier (bare non-reserved, or [quoted]) */
static char *parse_name(P *p) {
    Tok *k = CUR(p);
    if (k->t == TK_ID && (k->quoted || !is_reserved(k->text))) { p->i++; return k->text; }
    syntax_error(p);
    return NULL;
}
/* table name, allowing owner.table / db..table prefixes (the last part wins) */
static char *parse_table_name(P *p) {
    char *n = parse_name(p);
    while (n && at_op(p, ".")) {
        p->i++;
        if (at_op(p, ".")) p->i++;
        n = parse_name(p);
    }
    return n;
}
/* optional [AS] alias */
static char *parse_alias(P *p) {
    if (accept_kw(p, "AS")) {
        if (CUR(p)->t == TK_STR && CUR(p)->text[0]) { p->i++; return p->t[p->i - 1].text; }   /* AS 'Alias' */
        return parse_name(p);
    }
    Tok *k = CUR(p);
    if (is_kw(k, "FULL") && (peek_kw(p, 1, "JOIN") || peek_kw(p, 1, "OUTER"))) return NULL;
    if (k->t == TK_ID && (k->quoted || !is_reserved(k->text))) { p->i++; return k->text; }
    return NULL;
}
static int parse_int(P *p, long *out) {
    Tok *k = CUR(p);
    if (k->t != TK_NUM || k->num < 0) { syntax_error(p); return 0; }
    *out = (long)k->num; p->i++;
    return 1;
}

static Expr *ex_new(int k) { Expr *e = kmalloc(sizeof(Expr)); e->k = k; e->src = e->col = -1; return e; }
static Expr *ex_bin(int k, int op, Expr *a, Expr *b) { Expr *e = ex_new(k); e->op = op; e->a = a; e->b = b; return e; }
static Select *sel_new(void) { Select *s = kmalloc(sizeof(Select)); s->top = -1; s->limit = s->offset = -1; return s; }

static Expr *parse_expr(P *p);
static Select *parse_select_full(P *p);
static int parse_type(P *p, ColDef *cd, double *arg1, int *nargs);

static const struct { const char *name; int id; } AGGS[] = {
    {"COUNT", A_COUNT}, {"SUM", A_SUM}, {"AVG", A_AVG}, {"MIN", A_MIN}, {"MAX", A_MAX},
    {"FIRST", A_FIRST}, {"LAST", A_LAST}, {NULL, 0}
};

static Expr *parse_case(P *p) {
    Expr *e = ex_new(E_CASE);
    if (!at_kw(p, "WHEN")) { if (!(e->a = parse_expr(p))) return NULL; }
    while (accept_kw(p, "WHEN")) {
        Expr *w = parse_expr(p);
        if (!w || !expect_kw(p, "THEN")) return NULL;
        Expr *t = parse_expr(p);
        if (!t) return NULL;
        VPUSH(e->args, e->nargs, w);
        VPUSH(e->args, e->nargs, t);
    }
    if (!e->nargs) { syntax_error(p); return NULL; }
    if (accept_kw(p, "ELSE") && !(e->b = parse_expr(p))) return NULL;
    if (!expect_kw(p, "END")) return NULL;
    return e;
}

static Expr *parse_primary(P *p) {
    Tok *k = CUR(p);
    Expr *e;
    switch (k->t) {
    case TK_NUM:  p->i++; e = ex_new(E_LIT); e->v = v_num(k->num); return e;
    case TK_STR:  p->i++; e = ex_new(E_LIT); e->v = v_str(k->text); return e;
    case TK_DATE: p->i++; e = ex_new(E_LIT); e->v = v_date(k->num); return e;
    case TK_VAR:
        p->i++;
        if (!kf_stricmp(k->text, "IDENTITY")) return ex_new(E_IDENTITY);
        if (!kf_stricmp(k->text, "ROWCOUNT") || !kf_stricmp(k->text, "ERROR")) { e = ex_new(E_LIT); e->v = v_num(0); return e; }
        if (!kf_stricmp(k->text, "VERSION")) { e = ex_new(E_LIT); e->v = v_str(KF_PRODUCT " Flat-File Driver " KF_VERSION_STR); return e; }
        xerr(p->x, "Unknown global variable '@@%s'.", k->text);
        return NULL;
    case TK_OP:
        if (is_op(k, "(")) {
            p->i++;
            if (at_kw(p, "SELECT")) {
                e = ex_new(E_SUBQ);
                if (!(e->sub = parse_select_full(p))) return NULL;
            } else if (!(e = parse_expr(p))) return NULL;
            if (!expect_op(p, ")")) return NULL;
            return e;
        }
        syntax_error(p);
        return NULL;
    case TK_ID:
        break;
    default:
        syntax_error(p);
        return NULL;
    }
    /* identifiers: keywords, function calls, column references */
    if (!k->quoted) {
        if (is_kw(k, "NULL")) { p->i++; return ex_new(E_LIT); }
        if (is_kw(k, "TRUE")) { p->i++; e = ex_new(E_LIT); e->v = v_num(1); return e; }
        if (is_kw(k, "FALSE")) { p->i++; e = ex_new(E_LIT); e->v = v_num(0); return e; }
        if (is_kw(k, "EXISTS")) {
            p->i++;
            if (!expect_op(p, "(")) return NULL;
            e = ex_new(E_EXISTS);
            if (!(e->sub = parse_select_full(p)) || !expect_op(p, ")")) return NULL;
            return e;
        }
        if (is_kw(k, "CASE")) { p->i++; return parse_case(p); }
        if ((is_kw(k, "CAST") || is_kw(k, "CONVERT")) && is_op(&p->t[p->i + 1], "(")) {
            int conv = is_kw(k, "CONVERT");
            p->i += 2;
            e = ex_new(E_CAST);
            e->cd = kmalloc(sizeof(ColDef));
            double a; int na;
            if (conv) {              /* CONVERT(type, expr) - SQL Server order */
                if (!parse_type(p, e->cd, &a, &na) || !expect_op(p, ",") || !(e->a = parse_expr(p))) return NULL;
                if (accept_op(p, ",") && !parse_expr(p)) return NULL;   /* style: ignored */
            } else {
                if (!(e->a = parse_expr(p)) || !expect_kw(p, "AS") || !parse_type(p, e->cd, &a, &na)) return NULL;
            }
            if (!expect_op(p, ")")) return NULL;
            return e;
        }
        if ((is_kw(k, "CURRENT_TIMESTAMP") || is_kw(k, "CURRENT_DATE")) && !is_op(&p->t[p->i + 1], "(")) {
            p->i++;
            e = ex_new(E_FUNC);
            e->name = is_kw(k, "CURRENT_DATE") ? "DATE" : "NOW";
            return e;
        }
        if (is_op(&p->t[p->i + 1], "(")) {
            char *fname = kf_upper(k->text);
            p->i += 2;
            for (int a = 0; AGGS[a].name; a++) {
                if (strcmp(AGGS[a].name, fname)) continue;
                e = ex_new(E_AGG);
                e->op = AGGS[a].id;
                e->name = fname;
                if (accept_kw(p, "DISTINCT")) e->distinct = 1;
                else accept_kw(p, "ALL");
                if (e->op == A_COUNT && !e->distinct && accept_op(p, "*")) e->star = 1;
                else if (!(e->a = parse_expr(p))) return NULL;
                if (!expect_op(p, ")")) return NULL;
                return e;
            }
            e = ex_new(E_FUNC);
            e->name = fname;
            if (!at_op(p, ")")) {
                do {
                    Expr *a = parse_expr(p);
                    if (!a) return NULL;
                    VPUSH(e->args, e->nargs, a);
                } while (accept_op(p, ","));
            }
            if (!expect_op(p, ")")) return NULL;
            return e;
        }
        if (is_reserved(k->text)) { syntax_error(p); return NULL; }
    }
    p->i++;
    e = ex_new(E_COL);
    e->name = k->text;
    e->dq = k->quoted == 2;
    if (at_op(p, ".") && p->t[p->i + 1].t == TK_ID) {
        p->i++;
        e->qual = e->name;
        e->name = p->t[p->i].text;
        e->dq = 0;
        p->i++;
    }
    return e;
}

static Expr *parse_unary(P *p) {
    if (accept_op(p, "-")) {
        Expr *a = parse_unary(p);
        if (!a) return NULL;
        if (a->k == E_LIT && a->v.t == VT_NUM) { a->v.u.n = -a->v.u.n; return a; }
        Expr *e = ex_new(E_NEG); e->a = a;
        return e;
    }
    if (accept_op(p, "+")) return parse_unary(p);
    return parse_primary(p);
}

static Expr *parse_mul(P *p) {
    Expr *l = parse_unary(p);
    while (l) {
        int op;
        if (at_op(p, "*")) op = '*';
        else if (at_op(p, "/")) op = '/';
        else if (at_op(p, "%") || at_kw(p, "MOD")) op = '%';
        else if (at_op(p, "\\")) op = '\\';
        else break;
        p->i++;
        Expr *r = parse_unary(p);
        if (!r) return NULL;
        l = ex_bin(E_ARITH, op, l, r);
    }
    return l;
}

static Expr *parse_add(P *p) {
    Expr *l = parse_mul(p);
    while (l) {
        int op;
        if (at_op(p, "+")) op = '+';
        else if (at_op(p, "-")) op = '-';
        else break;
        p->i++;
        Expr *r = parse_mul(p);
        if (!r) return NULL;
        l = ex_bin(E_ARITH, op, l, r);
    }
    return l;
}

static Expr *parse_concat(P *p) {
    Expr *l = parse_add(p);
    while (l && (at_op(p, "&") || at_op(p, "||"))) {
        p->i++;
        Expr *r = parse_add(p);
        if (!r) return NULL;
        l = ex_bin(E_CONCAT, '&', l, r);
    }
    return l;
}

static Expr *parse_pred(P *p) {
    Expr *l = parse_concat(p);
    if (!l) return NULL;
    static const struct { const char *op; int c; } CMPS[] = {
        {"=", C_EQ}, {"<>", C_NE}, {"<", C_LT}, {"<=", C_LE}, {">", C_GT}, {">=", C_GE}, {NULL, 0}
    };
    for (int i = 0; CMPS[i].op; i++) if (at_op(p, CMPS[i].op)) {
        p->i++;
        Expr *r = parse_concat(p);
        if (!r) return NULL;
        return ex_bin(E_CMP, CMPS[i].c, l, r);
    }
    int neg = 0;
    if (at_kw(p, "NOT") && (peek_kw(p, 1, "LIKE") || peek_kw(p, 1, "IN") || peek_kw(p, 1, "BETWEEN"))) { neg = 1; p->i++; }
    if (accept_kw(p, "LIKE")) {
        Expr *r = parse_concat(p);
        if (!r) return NULL;
        Expr *e = ex_bin(E_LIKE, 0, l, r); e->neg = neg;
        return e;
    }
    if (accept_kw(p, "IN")) {
        if (!expect_op(p, "(")) return NULL;
        Expr *e;
        if (at_kw(p, "SELECT")) {
            e = ex_new(E_INSUB);
            if (!(e->sub = parse_select_full(p))) return NULL;
        } else {
            e = ex_new(E_INLIST);
            do {
                Expr *a = parse_expr(p);
                if (!a) return NULL;
                VPUSH(e->args, e->nargs, a);
            } while (accept_op(p, ","));
        }
        if (!expect_op(p, ")")) return NULL;
        e->a = l; e->neg = neg;
        return e;
    }
    if (accept_kw(p, "BETWEEN")) {
        Expr *lo = parse_concat(p);
        if (!lo || !expect_kw(p, "AND")) return NULL;
        Expr *hi = parse_concat(p);
        if (!hi) return NULL;
        Expr *e = ex_new(E_BETWEEN); e->a = l; e->b = lo; e->c = hi; e->neg = neg;
        return e;
    }
    if (accept_kw(p, "IS")) {
        Expr *e = ex_new(E_ISNULL); e->a = l;
        e->neg = accept_kw(p, "NOT");
        if (!expect_kw(p, "NULL")) return NULL;
        return e;
    }
    return l;
}

static Expr *parse_not(P *p) {
    if (accept_kw(p, "NOT")) {
        Expr *a = parse_not(p);
        if (!a) return NULL;
        Expr *e = ex_new(E_NOT); e->a = a;
        return e;
    }
    return parse_pred(p);
}

static Expr *parse_and(P *p) {
    Expr *l = parse_not(p);
    while (l && accept_kw(p, "AND")) {
        Expr *r = parse_not(p);
        if (!r) return NULL;
        l = ex_bin(E_AND, 0, l, r);
    }
    return l;
}

static Expr *parse_expr(P *p) {
    Expr *l = parse_and(p);
    while (l && accept_kw(p, "OR")) {
        Expr *r = parse_and(p);
        if (!r) return NULL;
        l = ex_bin(E_OR, 0, l, r);
    }
    return l;
}

/* ------------------------------------------------------------ FROM clause */
static JoinNode *add_src(P *p, Select *s, char *name, char *alias, Select *sub) {
    if (s->nsrc >= MAX_SRC) { xerr(p->x, "Query is too complex (more than %d tables).", MAX_SRC); return NULL; }
    Src *src = kmalloc(sizeof(Src));
    src->name = name; src->alias = alias; src->sub = sub;
    VPUSH(s->srcs, s->nsrc, src);
    JoinNode *j = kmalloc(sizeof(JoinNode));
    j->kind = J_LEAF; j->src = s->nsrc - 1;
    return j;
}

static JoinNode *parse_join_expr(P *p, Select *s);

static JoinNode *parse_table_primary(P *p, Select *s) {
    if (accept_op(p, "(")) {
        if (at_kw(p, "SELECT")) {
            Select *sub = parse_select_full(p);
            if (!sub || !expect_op(p, ")")) return NULL;
            char *alias = parse_alias(p);
            if (p->x->failed) return NULL;
            if (!alias) alias = kprintf("DERIVED%d", s->nsrc + 1);
            return add_src(p, s, alias, alias, sub);
        }
        JoinNode *j = parse_join_expr(p, s);         /* Access-style (a INNER JOIN b ON ..) */
        if (!j || !expect_op(p, ")")) return NULL;
        return j;
    }
    char *name = parse_table_name(p);
    if (!name) return NULL;
    char *alias = parse_alias(p);
    if (p->x->failed) return NULL;
    return add_src(p, s, name, alias, NULL);
}

static JoinNode *parse_join_expr(P *p, Select *s) {
    JoinNode *l = parse_table_primary(p, s);
    while (l) {
        int kind;
        if (accept_kw(p, "INNER")) { if (!expect_kw(p, "JOIN")) return NULL; kind = J_INNER; }
        else if (accept_kw(p, "JOIN")) kind = J_INNER;
        else if (accept_kw(p, "LEFT")) { accept_kw(p, "OUTER"); if (!expect_kw(p, "JOIN")) return NULL; kind = J_LEFT; }
        else if (accept_kw(p, "RIGHT")) { accept_kw(p, "OUTER"); if (!expect_kw(p, "JOIN")) return NULL; kind = J_RIGHT; }
        else if (accept_kw(p, "CROSS")) { if (!expect_kw(p, "JOIN")) return NULL; kind = J_CROSS; }
        else if (at_kw(p, "FULL")) { xerr(p->x, "FULL OUTER JOIN is not supported by this driver."); return NULL; }
        else break;
        JoinNode *r = parse_table_primary(p, s);
        if (!r) return NULL;
        JoinNode *j = kmalloc(sizeof(JoinNode));
        j->kind = kind; j->l = l; j->r = r; j->src = -1;
        if (kind != J_CROSS) {
            if (!expect_kw(p, "ON")) return NULL;
            if (!(j->on = parse_expr(p))) return NULL;
        }
        l = j;
    }
    return l;
}

/* --------------------------------------------------------------- SELECT */
static Select *parse_select_core(P *p) {
    if (!expect_kw(p, "SELECT")) return NULL;
    Select *s = sel_new();
    for (;;) {
        if (accept_kw(p, "DISTINCT") || accept_kw(p, "DISTINCTROW")) s->distinct = 1;
        else if (accept_kw(p, "ALL")) ;
        else if (accept_kw(p, "TOP")) {
            int paren = accept_op(p, "(");
            if (CUR(p)->t != TK_NUM) { syntax_error(p); return NULL; }
            s->top = CUR(p)->num; p->i++;
            if (paren && !expect_op(p, ")")) return NULL;
            if (accept_kw(p, "PERCENT")) s->top_percent = 1;
        } else break;
    }
    do {
        SelItem *it = kmalloc(sizeof(SelItem));
        if (accept_op(p, "*")) it->star = 1;
        else if (CUR(p)->t == TK_ID && is_op(&p->t[p->i + 1], ".") && is_op(&p->t[p->i + 2], "*")) {
            it->star = 1; it->starqual = CUR(p)->text; p->i += 3;
        } else {
            if (!(it->e = parse_expr(p))) return NULL;
            it->alias = parse_alias(p);
            if (p->x->failed) return NULL;
        }
        VPUSH(s->items, s->nitems, it);
    } while (accept_op(p, ","));
    if (accept_kw(p, "FROM")) {
        do {
            JoinNode *j = parse_join_expr(p, s);
            if (!j) return NULL;
            VPUSH(s->from, s->nfrom, j);
        } while (accept_op(p, ","));
    }
    if (accept_kw(p, "WHERE") && !(s->where = parse_expr(p))) return NULL;
    if (accept_kw(p, "GROUP")) {
        if (!expect_kw(p, "BY")) return NULL;
        do {
            Expr *g = parse_expr(p);
            if (!g) return NULL;
            VPUSH(s->group, s->ngroup, g);
        } while (accept_op(p, ","));
    }
    if (accept_kw(p, "HAVING") && !(s->having = parse_expr(p))) return NULL;
    return s;
}

static Select *parse_select_full(P *p) {
    Select *s = parse_select_core(p);
    if (!s) return NULL;
    Select *tail = s;
    while (accept_kw(p, "UNION")) {
        int all = accept_kw(p, "ALL");
        Select *n = parse_select_core(p);
        if (!n) return NULL;
        n->union_all = all;
        tail->next = n; tail = n;
    }
    if (accept_kw(p, "ORDER")) {
        if (!expect_kw(p, "BY")) return NULL;
        do {
            OrderItem *o = kmalloc(sizeof(OrderItem));
            o->outcol = -1;
            if (!(o->e = parse_expr(p))) return NULL;
            if (accept_kw(p, "DESC")) o->desc = 1;
            else accept_kw(p, "ASC");
            VPUSH(s->order, s->norder, o);
        } while (accept_op(p, ","));
    }
    if (accept_kw(p, "LIMIT")) {
        long a;
        if (!parse_int(p, &a)) return NULL;
        s->limit = a;
        if (accept_op(p, ",")) { s->offset = a; if (!parse_int(p, &s->limit)) return NULL; }
        else if (accept_kw(p, "OFFSET") && !parse_int(p, &s->offset)) return NULL;
    } else if (accept_kw(p, "OFFSET")) {
        if (!parse_int(p, &s->offset)) return NULL;
        if (!accept_kw(p, "ROWS")) accept_kw(p, "ROW");
    }
    return s;
}

/* ---------------------------------------------------------- DDL helpers */
static int valid_col_name(const char *n) {
    size_t l = strlen(n);
    if (!l || l > 64) return 0;
    for (const unsigned char *c = (const unsigned char *)n; *c; c++)
        if (*c < 32 || *c == ':' || *c == '\\' || *c == 127) return 0;
    return 1;
}

int sql_valid_table_name(const char *n) {
    size_t l = n ? strlen(n) : 0;
    if (!l || l > 64 || n[0] == ' ' || n[l - 1] == ' ' || n[0] == '-') return 0;
    for (const unsigned char *c = (const unsigned char *)n; *c; c++)
        if (!(isalnum(*c) || *c == '_' || *c == ' ' || *c == '-' || *c == '$' || *c >= 0x80)) return 0;
    return 1;
}

static int parse_type(P *p, ColDef *cd, double *arg1, int *nargs) {
    Tok *k = CUR(p);
    if (k->t != TK_ID) { syntax_error(p); return 0; }
    char *base = kf_upper(k->text);
    p->i++;
    if (!strcmp(base, "DOUBLE")) accept_kw(p, "PRECISION");
    else if (!strcmp(base, "CHARACTER") && accept_kw(p, "VARYING")) base = "VARCHAR";
    else if (!strcmp(base, "LONG") && (accept_kw(p, "TEXT") || accept_kw(p, "VARCHAR"))) base = "LONGTEXT";
    else if (!strcmp(base, "UNSIGNED") || !strcmp(base, "SIGNED")) { if (CUR(p)->t == TK_ID) { base = kf_upper(CUR(p)->text); p->i++; } }
    double a = 0, b = 0; int na = 0;
    if (accept_op(p, "(")) {
        if (accept_kw(p, "MAX")) na = 1;
        else {
            if (CUR(p)->t != TK_NUM) { syntax_error(p); return 0; }
            a = CUR(p)->num; p->i++; na = 1;
        }
        if (accept_op(p, ",")) {
            if (CUR(p)->t != TK_NUM) { syntax_error(p); return 0; }
            b = CUR(p)->num; p->i++; na = 2;
        }
        if (!expect_op(p, ")")) return 0;
    }
    char *tname = na == 0 || (na == 1 && a == 0) ? base
                : na == 1 ? kprintf("%s(%g)", base, a) : kprintf("%s(%g,%g)", base, a, b);
    if (!coldef_set_type(cd, tname)) {
        xerr(p->x, "Syntax error in field definition: unknown data type '%s'.", base);
        return 0;
    }
    if (cd->autoinc) cd->tname = base;              /* COUNTER(100,1): the numbers are the seed */
    if (arg1) *arg1 = a;
    if (nargs) *nargs = na;
    return 1;
}

/* skip a clause we accept but do not enforce (CHECK, FOREIGN KEY, ...) up to
 * the next ',' or ')' at nesting level 0 */
static void skip_clause(P *p) {
    int depth = 0;
    while (CUR(p)->t != TK_EOF) {
        if (at_op(p, "(")) depth++;
        else if (at_op(p, ")")) { if (!depth) return; depth--; }
        else if (at_op(p, ",") && !depth) return;
        p->i++;
    }
}

static ColDef *parse_coldef(P *p, Stmt *st) {
    ColDef *cd = kmalloc(sizeof(ColDef));
    if (!(cd->name = parse_name(p))) return NULL;
    if (!valid_col_name(cd->name)) { xerr(p->x, "Invalid field name '%s'.", cd->name); return NULL; }
    double a; int na;
    if (!parse_type(p, cd, &a, &na)) return NULL;
    if (cd->autoinc && na >= 1) st->seed = a;
    for (;;) {
        if (at_kw(p, "PRIMARY")) {
            p->i++;
            if (!expect_kw(p, "KEY")) return NULL;
            cd->pk = cd->notnull = 1;
            if (!accept_kw(p, "ASC")) accept_kw(p, "DESC");
        } else if (at_kw(p, "NOT")) {
            p->i++;
            if (!expect_kw(p, "NULL")) return NULL;
            cd->notnull = 1;
        } else if (accept_kw(p, "NULL")) {
        } else if (accept_kw(p, "UNIQUE")) {
            cd->unique = 1;
        } else if (accept_kw(p, "DEFAULT")) {
            int start = p->i;
            if (!parse_expr(p)) return NULL;
            cd->defexpr = kstrndup(p->sql + p->t[start].pos, p->t[p->i - 1].end - p->t[start].pos);
        } else if (accept_kw(p, "IDENTITY") || accept_kw(p, "AUTOINCREMENT") || accept_kw(p, "AUTO_INCREMENT")) {
            cd->autoinc = 1;
            if (cd->ct != CT_INT) { cd->ct = CT_INT; cd->tname = "INTEGER"; cd->scale = -1; cd->size = 0; }
            if (accept_op(p, "(")) {
                if (CUR(p)->t == TK_NUM) { st->seed = CUR(p)->num; p->i++; }
                if (accept_op(p, ",") && CUR(p)->t == TK_NUM) p->i++;
                if (!expect_op(p, ")")) return NULL;
            }
        } else if (accept_kw(p, "CONSTRAINT")) {
            if (!parse_name(p)) return NULL;
        } else if (at_kw(p, "REFERENCES") || at_kw(p, "CHECK") || at_kw(p, "COLLATE")) {
            skip_clause(p);
        } else break;
    }
    return cd;
}

static int parse_name_list(P *p, char ***names, int *n) {
    if (!expect_op(p, "(")) return 0;
    do {
        char *nm = parse_name(p);
        if (!nm) return 0;
        if (!accept_kw(p, "ASC")) accept_kw(p, "DESC");
        VPUSH(*names, *n, nm);
    } while (accept_op(p, ","));
    return expect_op(p, ")");
}

static int parse_create(P *p, Stmt *st) {
    if (accept_kw(p, "UNIQUE") || accept_kw(p, "INDEX") || accept_kw(p, "VIEW") || accept_kw(p, "CLUSTERED")) {
        /* indexes are accepted and ignored: every scan is a full scan anyway */
        while (CUR(p)->t != TK_EOF) p->i++;
        st->kind = ST_NOOP;
        return 1;
    }
    if (!expect_kw(p, "TABLE")) return 0;
    st->kind = ST_CREATE;
    st->seed = 1;
    if (at_kw(p, "IF")) {
        p->i++;
        if (!expect_kw(p, "NOT") || !expect_kw(p, "EXISTS")) return 0;
        st->ifx = 1;
    }
    if (!(st->table = parse_table_name(p))) return 0;
    if (!expect_op(p, "(")) return 0;
    char **pkcols = NULL; int npk = 0;
    char **uqcols = NULL; int nuq = 0;
    do {
        if (accept_kw(p, "CONSTRAINT") && !parse_name(p)) return 0;
        if (at_kw(p, "PRIMARY") && peek_kw(p, 1, "KEY")) {
            p->i += 2;
            if (!parse_name_list(p, &pkcols, &npk)) return 0;
        } else if (at_kw(p, "UNIQUE") && is_op(&p->t[p->i + 1], "(")) {
            p->i++;
            char **u = NULL; int nu = 0;
            if (!parse_name_list(p, &u, &nu)) return 0;
            if (nu == 1) VPUSH(uqcols, nuq, u[0]);        /* multi-column UNIQUE: not enforced */
        } else if ((at_kw(p, "FOREIGN") && peek_kw(p, 1, "KEY")) || (at_kw(p, "CHECK") && is_op(&p->t[p->i + 1], "("))) {
            skip_clause(p);
        } else {
            ColDef *cd = parse_coldef(p, st);
            if (!cd) return 0;
            VPUSH(st->defs, st->ndefs, cd);
        }
    } while (accept_op(p, ","));
    if (!expect_op(p, ")")) return 0;
    for (int i = 0; i < npk + nuq; i++) {
        const char *nm = i < npk ? pkcols[i] : uqcols[i - npk];
        int hit = 0;
        for (int c = 0; c < st->ndefs; c++) if (!kf_stricmp(st->defs[c]->name, nm)) {
            if (i < npk) st->defs[c]->pk = st->defs[c]->notnull = 1;
            else st->defs[c]->unique = 1;
            hit = 1;
        }
        if (!hit) { xerr(p->x, "Column '%s' named in a key constraint does not exist.", nm); return 0; }
    }
    while (accept_kw(p, "WITH") || accept_kw(p, "ENGINE") || accept_kw(p, "TYPE")) {
        while (CUR(p)->t != TK_EOF && !at_op(p, ";")) p->i++;   /* MySQL table options */
    }
    return 1;
}

static int parse_insert(P *p, Stmt *st) {
    st->kind = ST_INSERT;
    accept_kw(p, "INTO");
    if (!(st->table = parse_table_name(p))) return 0;
    if (at_op(p, "(") && !peek_kw(p, 1, "SELECT")) {
        p->i++;
        do {
            char *c = parse_name(p);
            if (!c) return 0;
            if (accept_op(p, ".") && !(c = parse_name(p))) return 0;
            VPUSH(st->cols, st->ncols, c);
        } while (accept_op(p, ","));
        if (!expect_op(p, ")")) return 0;
    }
    if (accept_kw(p, "VALUES")) {
        st->scope = sel_new();
        do {
            if (!expect_op(p, "(")) return 0;
            ValRow *vr = kmalloc(sizeof(ValRow));
            do {
                Expr *e = parse_expr(p);
                if (!e) return 0;
                VPUSH(vr->e, vr->n, e);
            } while (accept_op(p, ","));
            if (!expect_op(p, ")")) return 0;
            VPUSH(st->vals, st->nvals, vr);
        } while (accept_op(p, ","));
        return 1;
    }
    int paren = accept_op(p, "(");
    if (!at_kw(p, "SELECT")) { syntax_error(p); return 0; }
    if (!(st->sel = parse_select_full(p))) return 0;
    return !paren || expect_op(p, ")");
}

static int parse_update(P *p, Stmt *st) {
    st->kind = ST_UPDATE;
    if (!(st->table = parse_table_name(p))) return 0;
    char *alias = parse_alias(p);
    if (p->x->failed || !expect_kw(p, "SET")) return 0;
    st->sel = sel_new();
    JoinNode *j = add_src(p, st->sel, st->table, alias, NULL);
    if (!j) return 0;
    VPUSH(st->sel->from, st->sel->nfrom, j);
    do {
        char *c = parse_name(p);
        if (!c) return 0;
        if (accept_op(p, ".") && !(c = parse_name(p))) return 0;
        if (!expect_op(p, "=")) return 0;
        Expr *e = parse_expr(p);
        if (!e) return 0;
        VPUSH(st->cols, st->ncols, c);
        VPUSH(st->set, st->nset, e);
    } while (accept_op(p, ","));
    if (accept_kw(p, "WHERE") && !(st->sel->where = parse_expr(p))) return 0;
    return 1;
}

static int parse_delete(P *p, Stmt *st) {
    st->kind = ST_DELETE;
    if (!accept_op(p, "*") && CUR(p)->t == TK_ID && is_op(&p->t[p->i + 1], ".") && is_op(&p->t[p->i + 2], "*"))
        p->i += 3;                                    /* Access: DELETE Employees.* FROM ... */
    if (!accept_kw(p, "FROM") && !(CUR(p)->t == TK_ID)) { syntax_error(p); return 0; }
    if (!(st->table = parse_table_name(p))) return 0;
    char *alias = parse_alias(p);
    if (p->x->failed) return 0;
    st->sel = sel_new();
    JoinNode *j = add_src(p, st->sel, st->table, alias, NULL);
    if (!j) return 0;
    VPUSH(st->sel->from, st->sel->nfrom, j);
    if (accept_kw(p, "WHERE") && !(st->sel->where = parse_expr(p))) return 0;
    return 1;
}

static int parse_drop(P *p, Stmt *st) {
    if (!accept_kw(p, "TABLE")) {
        if (accept_kw(p, "INDEX") || accept_kw(p, "VIEW")) {
            while (CUR(p)->t != TK_EOF) p->i++;
            st->kind = ST_NOOP;
            return 1;
        }
        syntax_error(p);
        return 0;
    }
    st->kind = ST_DROP;
    if (at_kw(p, "IF") && peek_kw(p, 1, "EXISTS")) { p->i += 2; st->ifx = 1; }
    return (st->table = parse_table_name(p)) != NULL;
}

static int parse_alter(P *p, Stmt *st) {
    if (!expect_kw(p, "TABLE")) return 0;
    if (!(st->table = parse_table_name(p))) return 0;
    st->seed = 1;
    if (accept_kw(p, "ADD")) {
        accept_kw(p, "COLUMN");
        if (at_kw(p, "CONSTRAINT") || at_kw(p, "PRIMARY") || at_kw(p, "FOREIGN") || at_kw(p, "UNIQUE")) {
            xerr(p->x, "ALTER TABLE ... ADD CONSTRAINT is not supported by this driver; declare keys in CREATE TABLE.");
            return 0;
        }
        st->kind = ST_ADDCOL;
        ColDef *cd = parse_coldef(p, st);
        if (!cd) return 0;
        VPUSH(st->defs, st->ndefs, cd);
        return 1;
    }
    if (accept_kw(p, "DROP")) {
        accept_kw(p, "COLUMN");
        st->kind = ST_DROPCOL;
        char *c = parse_name(p);
        if (!c) return 0;
        VPUSH(st->cols, st->ncols, c);
        return 1;
    }
    syntax_error(p);
    return 0;
}

static Stmt *parse_sql(Exec *x, const char *sql) {
    P p; memset(&p, 0, sizeof p);
    p.x = x; p.sql = sql;
    if (!lex(x, sql, &p.t, &p.n)) return NULL;
    if (p.t[0].t == TK_EOF) { xerr(x, "Invalid SQL statement; the statement is empty."); return NULL; }
    Stmt *st = kmalloc(sizeof(Stmt));
    int ok;
    if (at_kw(&p, "SELECT")) {
        st->kind = ST_SELECT;
        ok = (st->sel = parse_select_full(&p)) != NULL;
    } else if (accept_kw(&p, "INSERT")) ok = parse_insert(&p, st);
    else if (accept_kw(&p, "UPDATE")) ok = parse_update(&p, st);
    else if (accept_kw(&p, "DELETE")) ok = parse_delete(&p, st);
    else if (accept_kw(&p, "CREATE")) ok = parse_create(&p, st);
    else if (accept_kw(&p, "DROP")) ok = parse_drop(&p, st);
    else if (accept_kw(&p, "ALTER")) ok = parse_alter(&p, st);
    else {
        xerr(x, "Invalid SQL statement; expected 'DELETE', 'INSERT', 'PROCEDURE', 'SELECT', or 'UPDATE'.");
        return NULL;
    }
    if (!ok || x->failed) return NULL;
    accept_op(&p, ";");
    if (CUR(&p)->t != TK_EOF) {
        if (st->kind == ST_SELECT && at_kw(&p, "INTO"))
            xerr(x, "SELECT ... INTO is not supported by this driver; use INSERT INTO ... SELECT.");
        else syntax_error(&p);
        return NULL;
    }
    return st;
}

/* parse a stand-alone expression (column DEFAULTs stored in table files) */
static Expr *parse_expr_text(Exec *x, const char *text) {
    P p; memset(&p, 0, sizeof p);
    p.x = x; p.sql = text;
    if (!lex(x, text, &p.t, &p.n)) return NULL;
    Expr *e = parse_expr(&p);
    if (e && CUR(&p)->t != TK_EOF) { syntax_error(&p); return NULL; }
    return e;
}

/* ================================================================ storage */
static void put_escaped(Buf *b, const char *s) {
    for (; *s; s++) {
        switch (*s) {
        case '\\': buf_put(b, "\\\\", 2); break;
        case '\t': buf_put(b, "\\t", 2); break;
        case '\n': buf_put(b, "\\n", 2); break;
        case '\r': buf_put(b, "\\r", 2); break;
        default: buf_putc(b, *s);
        }
    }
}

/* shortest text that reads back as exactly the same double */
static void put_number(Buf *b, double d) {
    char tmp[64];
    if (d == floor(d) && fabs(d) < 1e15) snprintf(tmp, sizeof tmp, "%.0f", d);
    else {
        for (int prec = 1; prec <= 17; prec++) {
            snprintf(tmp, sizeof tmp, "%.*g", prec, d);
            if (strtod(tmp, NULL) == d) break;
        }
    }
    buf_puts(b, tmp);
}

static void put_cell(Buf *b, Val v) {
    switch (v.t) {
    case VT_NULL: buf_put(b, "\\N", 2); break;
    case VT_NUM:  put_number(b, v.u.n); break;
    case VT_BOOL: buf_putc(b, v.u.b ? '1' : '0'); break;
    case VT_DATE: {
        int y, mo, d, h, mi, s;
        date_to_parts(v.u.n, &y, &mo, &d, &h, &mi, &s);
        if (h || mi || s) buf_printf(b, "%04d-%02d-%02d %02d:%02d:%02d", y, mo, d, h, mi, s);
        else buf_printf(b, "%04d-%02d-%02d", y, mo, d);
        break;
    }
    default: put_escaped(b, sv_str(v));
    }
}

/* unescape one field; *isnull set for \N */
static char *unescape_field(const char *s, size_t n, int *isnull) {
    *isnull = n == 2 && s[0] == '\\' && s[1] == 'N';
    if (*isnull) return NULL;
    char *out = kmalloc(n + 1), *o = out;
    for (size_t i = 0; i < n; i++) {
        if (s[i] == '\\' && i + 1 < n) {
            i++;
            switch (s[i]) {
            case 't': *o++ = '\t'; break;
            case 'n': *o++ = '\n'; break;
            case 'r': *o++ = '\r'; break;
            default:  *o++ = s[i];
            }
        } else *o++ = s[i];
    }
    *o = 0;
    return out;
}

static Val cell_from_text(const char *s, size_t n, ColDef *cd) {
    int isnull;
    char *t = unescape_field(s, n, &isnull);
    if (isnull) return v_null();
    double d;
    switch (cd->ct) {
    case CT_INT: case CT_FLOAT:
        if (v_isnumeric_str(t, &d)) return v_num(d);
        if (is_blank(t)) return v_null();
        break;
    case CT_DATE:
        if (date_parse(t, &d)) return v_date(d);
        if (is_blank(t)) return v_null();
        break;
    case CT_BIT: {
        int b;
        if (v_tobool(v_str(t), &b)) return v_num(b ? 1 : 0);
        if (is_blank(t)) return v_null();
        break;
    }
    }
    return v_str(t);              /* text, or a hand-edited value we keep verbatim */
}

static int next_line(const char **pp, const char *end, const char **ls, const char **le) {
    const char *p = *pp;
    if (p >= end) return 0;
    const char *nl = memchr(p, '\n', end - p);
    *ls = p;
    *le = nl ? nl : end;
    *pp = nl ? nl + 1 : end;
    if (*le > *ls && (*le)[-1] == '\r') (*le)--;
    return 1;
}

static void table_append(Table *t, Val *row) {
    if (t->nrows == t->rowcap) {
        int nc = t->rowcap ? t->rowcap * 2 : 16;
        Val **nr = kmalloc(sizeof(Val *) * nc);
        if (t->nrows) memcpy(nr, t->rows, sizeof(Val *) * t->nrows);
        t->rows = nr; t->rowcap = nc;
    }
    t->rows[t->nrows++] = row;
}

/* parse a .tbl file (allocations go to the current g_arena) */
static Table *table_parse(Exec *x, const char *path, const char *name, const char *data, size_t len) {
    const char *p = data, *end = data + len, *ls, *le;
    if (!next_line(&p, end, &ls, &le) || le - ls < 8 || strncmp(ls, "#KFTABLE", 8)) {
        xerr(x, "Table file '%s' is corrupt (missing #KFTABLE header).", path);
        return NULL;
    }
    Table *t = kmalloc(sizeof(Table));
    t->name = kstrdup(name);
    t->path = kstrdup(path);
    t->nextid = 1;
    if (!next_line(&p, end, &ls, &le) || le == ls) {
        xerr(x, "Table file '%s' is corrupt (no column definitions).", path);
        return NULL;
    }
    /* column definitions: Name:TYPE[:AUTOINC][:PK][:NOTNULL][:UNIQUE][:DEFAULT=expr] */
    ColDef *cols = NULL; int ncols = 0;
    for (const char *q = ls; q <= le; ) {
        const char *fs = q;
        while (q < le && *q != '\t') q++;
        int isnull;
        char *f = unescape_field(fs, q - fs, &isnull);
        q++;
        if (!f || !*f) continue;
        ColDef cd; memset(&cd, 0, sizeof cd);
        char *c1 = strchr(f, ':');
        if (!c1) { xerr(x, "Table file '%s' is corrupt (bad column definition '%s').", path, f); return NULL; }
        *c1 = 0;
        cd.name = f;
        char *ty = c1 + 1, *rest = strchr(ty, ':');
        if (rest) *rest++ = 0;
        if (!coldef_set_type(&cd, ty)) { xerr(x, "Table file '%s' has unknown data type '%s'.", path, ty); return NULL; }
        while (rest && *rest) {
            if (!strncmp(rest, "DEFAULT=", 8)) { cd.defexpr = rest + 8; break; }
            char *nx = strchr(rest, ':');
            if (nx) *nx++ = 0;
            if (!strcmp(rest, "AUTOINC")) cd.autoinc = 1;
            else if (!strcmp(rest, "PK")) cd.pk = cd.notnull = 1;
            else if (!strcmp(rest, "NOTNULL")) cd.notnull = 1;
            else if (!strcmp(rest, "UNIQUE")) cd.unique = 1;
            rest = nx;
        }
        VPUSH(cols, ncols, cd);
    }
    if (!ncols) { xerr(x, "Table file '%s' is corrupt (no columns).", path); return NULL; }
    t->cols = cols; t->ncols = ncols;
    if (next_line(&p, end, &ls, &le)) {
        const char *q = ls;
        while (q < le && !isdigit((unsigned char)*q) && *q != '-') q++;
        double d = strtod(q, NULL);
        if (d >= 1) t->nextid = floor(d);
    }
    while (next_line(&p, end, &ls, &le)) {
        if (le == ls && ncols > 1) continue;            /* stray blank line */
        Val *row = kmalloc(sizeof(Val) * ncols);       /* zeroed = all NULL */
        const char *q = ls;
        for (int c = 0; c < ncols; c++) {
            const char *fs = q;
            while (q < le && *q != '\t') q++;
            row[c] = cell_from_text(fs, q - fs, &cols[c]);
            if (q >= le) break;
            q++;
        }
        table_append(t, row);
    }
    /* keep the counter ahead of hand-edited ids */
    for (int c = 0; c < ncols; c++) if (cols[c].autoinc)
        for (int r = 0; r < t->nrows; r++)
            if (t->rows[r][c].t == VT_NUM && t->rows[r][c].u.n >= t->nextid) t->nextid = floor(t->rows[r][c].u.n) + 1;
    return t;
}

static int write_atomic(Exec *x, const char *path, const char *data, size_t len) {
    static unsigned long counter;                       /* protected by g_lock */
    char *tmp = kprintf("%s.tmp%ld.%lu", path, (long)getpid(), ++counter);
    int fd = open(tmp, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) { xerr(x, "Could not write table file '%s' (%s).", path, strerror(errno)); return 0; }
    size_t off = 0;
    while (off < len) {
        ssize_t w = write(fd, data + off, len - off);
        if (w < 0) { if (errno == EINTR) continue; goto fail; }
        off += (size_t)w;
    }
#if KF_SQL_FSYNC
    if (fsync(fd) != 0) goto fail;
#endif
    if (close(fd) != 0) { fd = -1; goto fail; }
    fd = -1;
    if (rename(tmp, path) != 0) goto fail;
    return 1;
fail:;
    int e = errno;
    if (fd >= 0) close(fd);
    unlink(tmp);
    xerr(x, "Could not write table file '%s' (%s).", path, strerror(e));
    return 0;
}

static int table_save(Exec *x, Table *t) {
    Buf b; buf_init(&b);
    buf_puts(&b, "#KFTABLE 1\n");
    for (int c = 0; c < t->ncols; c++) {
        ColDef *cd = &t->cols[c];
        Buf f; buf_init(&f);
        buf_printf(&f, "%s:%s", cd->name, cd->tname);
        if (cd->autoinc) buf_puts(&f, ":AUTOINC");
        if (cd->pk) buf_puts(&f, ":PK");
        else if (cd->notnull) buf_puts(&f, ":NOTNULL");
        if (cd->unique) buf_puts(&f, ":UNIQUE");
        if (cd->defexpr) buf_printf(&f, ":DEFAULT=%s", cd->defexpr);
        if (c) buf_putc(&b, '\t');
        put_escaped(&b, buf_cstr(&f));
    }
    buf_putc(&b, '\n');
    put_number(&b, t->nextid);
    buf_putc(&b, '\n');
    for (int r = 0; r < t->nrows; r++) {
        for (int c = 0; c < t->ncols; c++) {
            if (c) buf_putc(&b, '\t');
            put_cell(&b, t->rows[r][c]);
        }
        buf_putc(&b, '\n');
    }
    return write_atomic(x, t->path, buf_cstr(&b), b.len);
}

/* ------------------------------------------------------------ table cache */
typedef struct CEnt {
    struct CEnt *next;
    char  *path;
    dev_t  dev; ino_t ino; off_t size;
    long   msec, mnsec;
    Arena *arena;
    Table *t;
    unsigned long used;           /* g_serial of the last statement that used it */
} CEnt;
static CEnt *g_cache;
static int   g_ncache;

static void cent_free(CEnt *c) { arena_free(c->arena); free(c->path); free(c); }

static void cache_drop(const char *path) {
    for (CEnt **pp = &g_cache; *pp; pp = &(*pp)->next) {
        if (strcmp((*pp)->path, path)) continue;
        CEnt *c = *pp;
        *pp = c->next;
        cent_free(c);
        g_ncache--;
        return;
    }
}

void sql_cache_flush(void) {
    pthread_mutex_lock(&g_lock);
    while (g_cache) { CEnt *c = g_cache; g_cache = c->next; cent_free(c); }
    g_ncache = 0;
    pthread_mutex_unlock(&g_lock);
}

static char *read_whole(const char *path, size_t *len, struct stat *st) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) return NULL;
    if (fstat(fd, st) != 0 || !S_ISREG(st->st_mode)) { close(fd); return NULL; }
    size_t cap = (size_t)st->st_size + 2, n = 0;
    char *buf = malloc(cap);
    if (!buf) { close(fd); return NULL; }
    for (;;) {
        if (n + 1 >= cap) {
            char *nb = realloc(buf, cap * 2);
            if (!nb) { free(buf); close(fd); return NULL; }
            buf = nb; cap *= 2;
        }
        ssize_t r = read(fd, buf + n, cap - n - 1);
        if (r < 0) { if (errno == EINTR) continue; free(buf); close(fd); return NULL; }
        if (r == 0) break;
        n += (size_t)r;
    }
    close(fd);
    buf[n] = 0;
    *len = n;
    return buf;
}

/* load (or fetch from cache) the parsed table at path. Caller holds g_lock. */
static Table *table_load(Exec *x, const char *path, const char *name) {
    struct stat st;
    if (stat(path, &st) != 0) { xerr(x, "Table '%s' not found.", name); return NULL; }
    for (CEnt **pp = &g_cache; *pp; pp = &(*pp)->next) {
        CEnt *c = *pp;
        if (strcmp(c->path, path)) continue;
        if (c->dev == st.st_dev && c->ino == st.st_ino && c->size == st.st_size &&
            c->msec == (long)st.st_mtim.tv_sec && c->mnsec == st.st_mtim.tv_nsec) {
            c->used = g_serial;
            return c->t;
        }
        *pp = c->next;                                  /* stale: changed on disk */
        cent_free(c);
        g_ncache--;
        break;
    }
    size_t len;
    struct stat st2;
    char *data = read_whole(path, &len, &st2);
    if (!data) { xerr(x, "Could not read table file '%s' (%s).", path, strerror(errno)); return NULL; }
    Arena *a = arena_new(), *saved = g_arena;
    g_arena = a;
    Table *t = table_parse(x, path, name, data, len);
    g_arena = saved;
    free(data);
    if (!t) { arena_free(a); return NULL; }
    if (g_ncache >= CACHE_MAX) {                        /* evict the least recently used */
        CEnt **victim = NULL;
        for (CEnt **pp = &g_cache; *pp; pp = &(*pp)->next)
            if ((*pp)->used != g_serial && (!victim || (*pp)->used < (*victim)->used)) victim = pp;
        if (victim) { CEnt *c = *victim; *victim = c->next; cent_free(c); g_ncache--; }
    }
    CEnt *c = calloc(1, sizeof(CEnt));
    if (!c || !(c->path = strdup(path))) { free(c); arena_free(a); xerr(x, "Out of memory loading table '%s'.", name); return NULL; }
    c->dev = st2.st_dev; c->ino = st2.st_ino; c->size = st2.st_size;
    c->msec = (long)st2.st_mtim.tv_sec; c->mnsec = st2.st_mtim.tv_nsec;
    c->arena = a; c->t = t; c->used = g_serial;
    c->next = g_cache; g_cache = c;
    g_ncache++;
    return t;
}

/* find <dbdir>/<name>.tbl case-insensitively; returns the path (and the
 * table name as stored on disk) or NULL */
static char *table_path(Exec *x, const char *name, char **realname) {
    DIR *d = opendir(x->dbdir);
    if (!d) return NULL;
    size_t nl = strlen(name);
    char *found = NULL;
    struct dirent *de;
    while ((de = readdir(d))) {
        size_t l = strlen(de->d_name);
        if (l != nl + 4 || strcmp(de->d_name + nl, ".tbl") || kf_strnicmp(de->d_name, name, nl)) continue;
        if (!found || !strncmp(de->d_name, name, nl)) found = kstrndup(de->d_name, nl);  /* exact case wins */
    }
    closedir(d);
    if (!found) return NULL;
    if (realname) *realname = found;
    return kf_path_join(x->dbdir, kprintf("%s.tbl", found));
}

static Table *table_get(Exec *x, const char *name, int must) {
    if (!sql_valid_table_name(name)) { xerr(x, "Invalid table name '%s'.", name); return NULL; }
    char *real = NULL;
    char *path = table_path(x, name, &real);
    if (!path) {
        if (must) xerr(x, "Table '%s' not found.", name);
        return NULL;
    }
    return table_load(x, path, real);
}

/* shallow copy for writing: new row pointer array, shared (immutable) rows */
static Table *table_clone(Table *t) {
    Table *w = kmalloc(sizeof(Table));
    *w = *t;
    w->path = kstrdup(t->path);
    w->name = kstrdup(t->name);
    w->cols = kmalloc(sizeof(ColDef) * (t->ncols + 1));
    memcpy(w->cols, t->cols, sizeof(ColDef) * t->ncols);
    w->rowcap = t->nrows + 16;
    w->rows = kmalloc(sizeof(Val *) * w->rowcap);
    if (t->nrows) memcpy(w->rows, t->rows, sizeof(Val *) * t->nrows);
    return w;
}

static int table_col(Table *t, const char *name) {
    for (int c = 0; c < t->ncols; c++) if (!kf_stricmp(t->cols[c].name, name)) return c;
    return -1;
}

/* save w and drop the cached copy (whose memory w may still point into,
 * so the drop happens strictly after the save) */
static int table_commit(Exec *x, Table *w) {
    if (!table_save(x, w)) return 0;
    cache_drop(w->path);
    return 1;
}

/* ================================================================ binding */
static void bind_select(Exec *x, Select *s);
static void bind_expr(Exec *x, Select *s, Expr *e);

enum {
    F_UPPER = 1, F_LOWER, F_LEN, F_TRIM, F_LTRIM, F_RTRIM, F_LEFT, F_RIGHT, F_MID, F_ROUND, F_ABS,
    F_NOW, F_DATE, F_YEAR, F_MONTH, F_DAY, F_HOUR, F_MINUTE, F_SECOND, F_WEEKDAY,
    F_COALESCE, F_ISNULL, F_NZ, F_IIF, F_NULLIF, F_CONCAT, F_REPLACE, F_INSTR, F_CHARINDEX,
    F_INT, F_FIX, F_FLOOR, F_CEILING, F_SQRT, F_POWER, F_SIGN, F_MOD, F_STR, F_VAL, F_CINT,
    F_CDBL, F_CDATE, F_DATEADD, F_DATEDIFF, F_DATEPART, F_DATESERIAL, F_IDENTITY, F_ASCII,
    F_CHR, F_SPACE, F_REPLICATE, F_REVERSE
};
static const struct { const char *name; int id, min, max; } FUNCS[] = {
    {"UPPER", F_UPPER, 1, 1}, {"UCASE", F_UPPER, 1, 1}, {"LOWER", F_LOWER, 1, 1}, {"LCASE", F_LOWER, 1, 1},
    {"LEN", F_LEN, 1, 1}, {"LENGTH", F_LEN, 1, 1}, {"CHAR_LENGTH", F_LEN, 1, 1},
    {"TRIM", F_TRIM, 1, 1}, {"LTRIM", F_LTRIM, 1, 1}, {"RTRIM", F_RTRIM, 1, 1},
    {"LEFT", F_LEFT, 2, 2}, {"RIGHT", F_RIGHT, 2, 2},
    {"MID", F_MID, 2, 3}, {"SUBSTRING", F_MID, 2, 3}, {"SUBSTR", F_MID, 2, 3},
    {"ROUND", F_ROUND, 1, 2}, {"ABS", F_ABS, 1, 1},
    {"NOW", F_NOW, 0, 0}, {"GETDATE", F_NOW, 0, 0}, {"CURRENT_TIMESTAMP", F_NOW, 0, 0}, {"SYSDATE", F_NOW, 0, 0},
    {"DATE", F_DATE, 0, 0}, {"CURDATE", F_DATE, 0, 0}, {"CURRENT_DATE", F_DATE, 0, 0},
    {"YEAR", F_YEAR, 1, 1}, {"MONTH", F_MONTH, 1, 1}, {"DAY", F_DAY, 1, 1},
    {"HOUR", F_HOUR, 1, 1}, {"MINUTE", F_MINUTE, 1, 1}, {"SECOND", F_SECOND, 1, 1}, {"WEEKDAY", F_WEEKDAY, 1, 1},
    {"COALESCE", F_COALESCE, 1, 255}, {"IFNULL", F_COALESCE, 2, 2}, {"NVL", F_COALESCE, 2, 2},
    {"ISNULL", F_ISNULL, 1, 2}, {"NZ", F_NZ, 1, 2}, {"IIF", F_IIF, 3, 3}, {"NULLIF", F_NULLIF, 2, 2},
    {"CONCAT", F_CONCAT, 1, 255}, {"REPLACE", F_REPLACE, 3, 3},
    {"INSTR", F_INSTR, 2, 3}, {"CHARINDEX", F_CHARINDEX, 2, 3},
    {"INT", F_INT, 1, 1}, {"FIX", F_FIX, 1, 1}, {"FLOOR", F_FLOOR, 1, 1}, {"CEILING", F_CEILING, 1, 1},
    {"CEIL", F_CEILING, 1, 1}, {"SQRT", F_SQRT, 1, 1}, {"SQR", F_SQRT, 1, 1}, {"POWER", F_POWER, 2, 2},
    {"POW", F_POWER, 2, 2}, {"SIGN", F_SIGN, 1, 1}, {"SGN", F_SIGN, 1, 1}, {"MOD", F_MOD, 2, 2},
    {"STR", F_STR, 1, 1}, {"CSTR", F_STR, 1, 1}, {"VAL", F_VAL, 1, 1},
    {"CINT", F_CINT, 1, 1}, {"CLNG", F_CINT, 1, 1}, {"CDBL", F_CDBL, 1, 1}, {"CSNG", F_CDBL, 1, 1},
    {"CCUR", F_CDBL, 1, 1}, {"CDATE", F_CDATE, 1, 1}, {"DATEVALUE", F_CDATE, 1, 1},
    {"DATEADD", F_DATEADD, 3, 3}, {"DATEDIFF", F_DATEDIFF, 3, 3}, {"DATEPART", F_DATEPART, 2, 2},
    {"DATESERIAL", F_DATESERIAL, 3, 3},
    {"SCOPE_IDENTITY", F_IDENTITY, 0, 0}, {"LAST_INSERT_ID", F_IDENTITY, 0, 0},
    {"ASCII", F_ASCII, 1, 1}, {"CHR", F_CHR, 1, 1}, {"CHAR", F_CHR, 1, 1},
    {"SPACE", F_SPACE, 1, 1}, {"REPLICATE", F_REPLICATE, 2, 2}, {"STRING", F_REPLICATE, 2, 2},
    {"REVERSE", F_REVERSE, 1, 1}, {"STRREVERSE", F_REVERSE, 1, 1},
    {NULL, 0, 0, 0}
};

/* does qualifier qual name this source? An aliased table answers only to its
 * alias (standard scoping, which correlated subqueries rely on); lenient mode
 * also accepts the table name, for sloppy "SELECT Employees.x FROM Employees e" */
static int src_matches(Src *src, const char *qual, int lenient) {
    if (src->alias && !kf_stricmp(src->alias, qual)) return 1;
    return (!src->alias || lenient) && src->name && !kf_stricmp(src->name, qual);
}

/* resolve a column reference through the scope chain (innermost first) */
static int resolve_col(Exec *x, Select *s, Expr *e, int report) {
    for (int lenient = 0; lenient < (e->qual ? 2 : 1); lenient++) {
        int depth = 0;
        for (Select *sc = s; sc; sc = sc->parent, depth++) {
            int found = 0, qualhit = 0;
            for (int i = 0; i < sc->nsrc; i++) {
                Src *src = sc->srcs[i];
                if (e->qual) {
                    if (!src_matches(src, e->qual, lenient)) continue;
                    qualhit = 1;
                }
                for (int c = 0; c < src->ncols; c++) {
                    if (kf_stricmp(src->colnames[c], e->name)) continue;
                    if (!found) { e->src = i; e->col = c; }
                    found++;
                    break;
                }
            }
            if (found > 1) {
                if (report) xerr(x, "The specified field '%s' could refer to more than one table listed in the FROM clause of your SQL statement.", e->name);
                return 0;
            }
            if (found == 1) {
                e->depth = depth;
                Select *m = s;
                for (int d = 0; d < depth; d++, m = m->parent) m->correlated = 1;
                e->bound = 1;
                return 1;
            }
            if (qualhit) break;
        }
    }
    if (!report) return 0;
    if (e->dq && !e->qual) {                     /* "text" that is not a column: Access string literal */
        e->k = E_LIT;
        e->v = v_str(e->name);
        return 1;
    }
    if (e->qual) xerr(x, "Too few parameters. Expected 1. (Unknown column '%s.%s'.)", e->qual, e->name);
    else xerr(x, "Too few parameters. Expected 1. (Unknown column '%s'.)", e->name);
    return 0;
}

/* does e contain an aggregate belonging to this query level? */
static int expr_has_agg(Expr *e) {
    if (!e) return 0;
    if (e->k == E_AGG) return 1;
    if (e->k == E_SUBQ || e->k == E_EXISTS) return 0;
    if (expr_has_agg(e->a) || expr_has_agg(e->b) || expr_has_agg(e->c)) return 1;
    for (int i = 0; i < e->nargs; i++) if (expr_has_agg(e->args[i])) return 1;
    return 0;
}

/* does e contain a correlated subquery? (such conjuncts are not pushed down) */
static int expr_has_corr_sub(Expr *e) {
    if (!e) return 0;
    if ((e->k == E_SUBQ || e->k == E_EXISTS || e->k == E_INSUB) && e->sub->correlated) return 1;
    if (expr_has_corr_sub(e->a) || expr_has_corr_sub(e->b) || expr_has_corr_sub(e->c)) return 1;
    for (int i = 0; i < e->nargs; i++) if (expr_has_corr_sub(e->args[i])) return 1;
    return 0;
}

/* bitmask of this level's sources referenced by e */
static uint64_t expr_mask(Expr *e) {
    if (!e) return 0;
    uint64_t m = 0;
    if (e->k == E_COL && e->bound && e->depth == 0 && e->src >= 0) m |= (uint64_t)1 << e->src;
    m |= expr_mask(e->a) | expr_mask(e->b) | expr_mask(e->c);
    for (int i = 0; i < e->nargs; i++) m |= expr_mask(e->args[i]);
    return m;
}

static void split_conj(Select *s, Expr *e) {
    if (!e) return;
    if (e->k == E_AND) { split_conj(s, e->a); split_conj(s, e->b); return; }
    VPUSH(s->conj, s->nconj, e);
}

static void bind_join(Exec *x, Select *s, JoinNode *j) {
    if (!j || j->kind == J_LEAF) return;
    bind_join(x, s, j->l);
    bind_join(x, s, j->r);
    if (j->on) {
        bind_expr(x, s, j->on);
        if (!x->failed && expr_has_agg(j->on)) xerr(x, "Cannot have aggregate function in JOIN expression.");
    }
}

static const char *expr_desc(Expr *e) { return e->k == E_AGG || e->k == E_FUNC ? e->name : "expression"; }

static int func_lookup(const char *name) {
    for (int i = 0; FUNCS[i].name; i++) if (!strcmp(FUNCS[i].name, name)) return i;
    return -1;
}

static void bind_expr(Exec *x, Select *s, Expr *e) {
    if (!e || x->failed) return;
    switch (e->k) {
    case E_COL:
        if (!e->bound) resolve_col(x, s, e, 1);
        return;
    case E_SUBQ: case E_EXISTS: case E_INSUB:
        if (e->k == E_INSUB) bind_expr(x, s, e->a);
        e->sub->parent = s;
        bind_select(x, e->sub);
        if (!x->failed && e->k != E_EXISTS && e->sub->nitems != 1)
            xerr(x, "You have written a subquery that can return more than one field without using the EXISTS reserved word in the main query's FROM clause. Revise the SELECT statement of the subquery to request only one field.");
        return;
    case E_FUNC: {
        int f = func_lookup(e->name);
        if (f < 0) { xerr(x, "Undefined function '%s' in expression.", e->name); return; }
        if (e->nargs < FUNCS[f].min || e->nargs > FUNCS[f].max) {
            xerr(x, "Wrong number of arguments used with function '%s' in query expression.", e->name);
            return;
        }
        e->op = FUNCS[f].id;
        /* SQL Server style DATEADD(day, 1, d): the unit is a bare word */
        if ((e->op == F_DATEADD || e->op == F_DATEDIFF || e->op == F_DATEPART) &&
            e->args[0]->k == E_COL && !e->args[0]->qual) {
            e->args[0]->k = E_LIT;
            e->args[0]->v = v_str(e->args[0]->name);
        }
        for (int i = 0; i < e->nargs; i++) bind_expr(x, s, e->args[i]);
        return;
    }
    case E_AGG:
        if (e->a) {
            bind_expr(x, s, e->a);
            if (!x->failed && expr_has_agg(e->a)) xerr(x, "Cannot have aggregate function in expression (%s).", e->name);
        }
        return;
    default:
        bind_expr(x, s, e->a);
        bind_expr(x, s, e->b);
        bind_expr(x, s, e->c);
        for (int i = 0; i < e->nargs; i++) bind_expr(x, s, e->args[i]);
    }
}

/* name a result column: alias, else column name, else EXPRn */
static char *col_name_of(Select *s, Expr *e) {
    Select *sc = s;
    for (int d = 0; d < e->depth && sc; d++) sc = sc->parent;
    if (!sc || e->src < 0) return e->name;
    return sc->srcs[e->src]->colnames[e->col];
}

static void bind_select(Exec *x, Select *s) {
    if (s->bound || x->failed) return;
    s->bound = 1;
    /* 1. sources: load tables, bind derived tables (no lateral references) */
    for (int i = 0; i < s->nsrc; i++) {
        Src *src = s->srcs[i];
        if (src->sub) {
            src->sub->parent = s->parent;
            bind_select(x, src->sub);
            if (x->failed) return;
            if (src->sub->correlated) s->correlated = 1;
            src->ncols = src->sub->nitems;
            src->colnames = src->sub->outnames;
        } else {
            if (!(src->tab = table_get(x, src->name, 1))) return;
            src->ncols = src->tab->ncols;
            src->colnames = kmalloc(sizeof(char *) * src->ncols);
            for (int c = 0; c < src->ncols; c++) src->colnames[c] = src->tab->cols[c].name;
            if (!src->alias) src->name = src->tab->name;
        }
    }
    /* 2. expand * and t.* */
    SelItem **items = NULL; int n = 0;
    for (int i = 0; i < s->nitems; i++) {
        SelItem *it = s->items[i];
        if (!it->star) { VPUSH(items, n, it); continue; }
        int hit = 0, lenient = 0;
        if (it->starqual) {                         /* t.*: strict alias match first */
            for (int k = 0; k < s->nsrc; k++) if (src_matches(s->srcs[k], it->starqual, 0)) hit = 1;
            lenient = !hit;
            hit = 0;
        }
        for (int k = 0; k < s->nsrc; k++) {
            Src *src = s->srcs[k];
            if (it->starqual && !src_matches(src, it->starqual, lenient)) continue;
            hit = 1;
            for (int c = 0; c < src->ncols; c++) {
                SelItem *ni = kmalloc(sizeof(SelItem));
                ni->e = ex_new(E_COL);
                ni->e->name = src->colnames[c];
                ni->e->src = k; ni->e->col = c; ni->e->bound = 1;
                VPUSH(items, n, ni);
            }
        }
        if (!hit) {
            if (it->starqual) xerr(x, "Table or alias '%s' named in '%s.*' is not in the FROM clause.", it->starqual, it->starqual);
            else xerr(x, "SELECT * requires a FROM clause.");
            return;
        }
    }
    s->items = items; s->nitems = n;
    /* 3. bind expressions */
    for (int i = 0; i < s->nitems; i++) bind_expr(x, s, s->items[i]->e);
    for (int i = 0; i < s->nfrom; i++) bind_join(x, s, s->from[i]);
    bind_expr(x, s, s->where);
    if (x->failed) return;
    if (expr_has_agg(s->where)) { xerr(x, "Cannot have aggregate function in WHERE clause (%s).", "WHERE"); return; }
    for (int i = 0; i < s->ngroup; i++) {
        Expr *g = s->group[i];
        if (g->k == E_COL && !g->qual && !g->bound && !resolve_col(x, s, g, 0)) {
            for (int k = 0; k < s->nitems; k++)          /* GROUP BY alias (MySQL style) */
                if (s->items[k]->alias && !kf_stricmp(s->items[k]->alias, g->name)) { s->group[i] = g = s->items[k]->e; break; }
        }
        bind_expr(x, s, g);
        if (!x->failed && expr_has_agg(g)) { xerr(x, "Cannot have aggregate function in GROUP BY clause (%s).", expr_desc(g)); return; }
    }
    bind_expr(x, s, s->having);
    if (x->failed) return;
    if (!s->next) {
        for (int i = 0; i < s->norder; i++) {
            OrderItem *o = s->order[i];
            if (o->e->k == E_LIT && o->e->v.t == VT_NUM) {
                int k = (int)o->e->v.u.n;
                if (k < 1 || k > s->nitems) { xerr(x, "ORDER BY position %d is out of range (the query has %d columns).", k, s->nitems); return; }
                o->outcol = k - 1;
                continue;
            }
            if (o->e->k == E_COL && !o->e->qual)
                for (int k = 0; k < s->nitems; k++)
                    if (s->items[k]->alias && !kf_stricmp(s->items[k]->alias, o->e->name)) { o->outcol = k; break; }
            if (o->outcol < 0) bind_expr(x, s, o->e);
        }
    }
    if (x->failed) return;
    /* 4. output column names (unique, case-insensitively) */
    s->outnames = kmalloc(sizeof(char *) * (s->nitems + 1));
    int exprn = 0;
    for (int i = 0; i < s->nitems; i++) {
        SelItem *it = s->items[i];
        char *nm = it->alias ? it->alias
                 : it->e->k == E_COL ? col_name_of(s, it->e)
                 : kprintf("EXPR%d", ++exprn);
        char *base = nm;
        for (int k = 2;; k++) {
            int clash = 0;
            for (int j = 0; j < i; j++) if (!kf_stricmp(s->outnames[j], nm)) { clash = 1; break; }
            if (!clash) break;
            nm = kprintf("%s_%d", base, k);
        }
        s->outnames[i] = nm;
    }
    /* 5. aggregate query? */
    s->has_agg = s->ngroup > 0 || s->having != NULL;
    for (int i = 0; i < s->nitems; i++) if (expr_has_agg(s->items[i]->e)) s->has_agg = 1;
    if (!s->next) for (int i = 0; i < s->norder; i++) if (s->order[i]->outcol < 0 && expr_has_agg(s->order[i]->e)) s->has_agg = 1;
    /* 6. WHERE conjuncts and the sources each one needs */
    split_conj(s, s->where);
    s->conjmask = kmalloc(sizeof(uint64_t) * (s->nconj + 1));
    uint64_t all = s->nsrc >= 64 ? ~(uint64_t)0 : (((uint64_t)1 << s->nsrc) - 1);
    for (int i = 0; i < s->nconj; i++)
        s->conjmask[i] = expr_has_corr_sub(s->conj[i]) ? all : expr_mask(s->conj[i]);
    /* 7. UNION chain */
    if (s->next) {
        s->next->parent = s->parent;
        bind_select(x, s->next);
        if (x->failed) return;
        if (s->next->nitems != s->nitems) {
            xerr(x, "The number of columns in the two selected tables or queries of a union query do not match.");
            return;
        }
        if (s->next->correlated) s->correlated = 1;
        for (int i = 0; i < s->norder; i++) {
            OrderItem *o = s->order[i];
            if (o->e->k == E_LIT && o->e->v.t == VT_NUM) o->outcol = (int)o->e->v.u.n - 1;
            else if (o->e->k == E_COL)
                for (int k = 0; k < s->nitems; k++) if (!kf_stricmp(s->outnames[k], o->e->name)) { o->outcol = k; break; }
            if (o->outcol < 0 || o->outcol >= s->nitems) {
                xerr(x, "The ORDER BY expression (%s) includes fields that are not selected by the query. Only those fields requested in the first query can be included in an ORDER BY expression.",
                     o->e->k == E_COL ? o->e->name : "expression");
                return;
            }
        }
    }
}

/* ============================================================= evaluation */
typedef struct Ctx {
    struct Ctx *parent;       /* enclosing query's row (correlated references) */
    Val       **tuple;        /* one row pointer per source; NULL = null-extended */
    Val      ***grp;          /* rows of the current group (aggregates) */
    int         ngrp;
    int         grouped;
} Ctx;

static Val eval(Exec *x, Expr *e, Ctx *c);
static ResultSet *exec_select(Exec *x, Select *s, Ctx *outer);

static Val mismatch(Exec *x, const char *what) {
    xerr(x, "Data type mismatch in criteria expression (%s).", what);
    return v_null();
}

/* LIKE with % * (any run), _ ? (one char) and [abc] [a-z] [!x] classes, case-insensitive */
static int like_class(const char **pp, int ch) {
    const char *p = *pp + 1;
    int neg = 0, hit = 0;
    if (*p == '!' || *p == '^') { neg = 1; p++; }
    const char *start = p;
    while (*p && (*p != ']' || p == start)) {
        int lo = tolower((unsigned char)*p), hi = lo;
        if (p[1] == '-' && p[2] && p[2] != ']') { hi = tolower((unsigned char)p[2]); p += 2; }
        if (ch >= lo && ch <= hi) hit = 1;
        p++;
    }
    if (*p != ']') return -1;                           /* no closing bracket: literal '[' */
    *pp = p + 1;
    return hit != neg;
}

static int like_match(const char *s, const char *p) {
    const char *star_p = NULL, *star_s = NULL;
    while (*s) {
        if (*p == '%' || *p == '*') { while (*p == '%' || *p == '*') p++; star_p = p; star_s = s; continue; }
        int ch = tolower((unsigned char)*s), ok = 0;
        const char *np = p;
        if (*p == '_' || *p == '?') { ok = 1; np = p + 1; }
        else if (*p == '[') {
            int r = like_class(&np, ch);
            if (r < 0) { ok = ch == '['; np = p + 1; }
            else ok = r;
        } else if (*p) { ok = tolower((unsigned char)*p) == ch; np = p + 1; }
        if (ok) { p = np; s++; continue; }
        if (star_p) { p = star_p; s = ++star_s; continue; }
        return 0;
    }
    while (*p == '%' || *p == '*') p++;
    return *p == 0;
}

static Val arith(Exec *x, int op, Val a, Val b) {
    if (is_null(a) || is_null(b)) return v_null();
    double p, q;
    int an = num_of(a, &p), bn = num_of(b, &q);
    if (op == '+') {
        if (a.t == VT_DATE && b.t != VT_DATE && bn) return v_date(p + q);
        if (b.t == VT_DATE && a.t != VT_DATE && an) return v_date(p + q);
        if (an && bn) return v_num(p + q);
        const char *sa = sv_str(a), *sb = sv_str(b);
        return v_str(kprintf("%s%s", sa, sb));
    }
    if (!an || !bn) return mismatch(x, "arithmetic on a non-numeric value");
    switch (op) {
    case '-':
        if (a.t == VT_DATE && b.t != VT_DATE) return v_date(p - q);
        return v_num(p - q);
    case '*': return v_num(p * q);
    case '/':
        if (q == 0) { xerr(x, "Division by zero."); return v_null(); }
        return v_num(p / q);
    case '\\': {
        double ip = trunc(round(p)), iq = trunc(round(q));
        if (iq == 0) { xerr(x, "Division by zero."); return v_null(); }
        return v_num(trunc(ip / iq));
    }
    case '%':
        if (q == 0) { xerr(x, "Division by zero."); return v_null(); }
        return v_num(fmod(p, q));
    }
    return v_null();
}

static Val cmp_op(int op, Val a, Val b) {
    if (is_null(a) || is_null(b)) return v_null();
    int r = sql_cmp(a, b);
    switch (op) {
    case C_EQ: return vbool(r == 0);
    case C_NE: return vbool(r != 0);
    case C_LT: return vbool(r < 0);
    case C_LE: return vbool(r <= 0);
    case C_GT: return vbool(r > 0);
    case C_GE: return vbool(r >= 0);
    }
    return v_null();
}

/* run a subquery, reusing the result when it does not depend on the outer row */
static ResultSet *run_sub(Exec *x, Select *sub, Ctx *c) {
    return exec_select(x, sub, c);
}

/* ---------------------------------------------------------- aggregates */
static int val_ptr_cmp(const void *pa, const void *pb, void *ctx) {
    (void)ctx;
    return order_cmp(*(const Val *)pa, *(const Val *)pb);
}

static Val eval_agg(Exec *x, Expr *e, Ctx *c) {
    if (!c || !c->grouped) { xerr(x, "Aggregate function %s used outside of an aggregate query.", e->name); return v_null(); }
    if (e->star) return v_num(c->ngrp);
    Val *vals = NULL; int nv = 0;
    for (int g = 0; g < c->ngrp; g++) {
        Ctx t; memset(&t, 0, sizeof t);
        t.parent = c->parent; t.tuple = c->grp[g];
        Val v = eval(x, e->a, &t);
        if (x->failed) return v_null();
        if (is_null(v) && e->op != A_FIRST && e->op != A_LAST) continue;
        VPUSH(vals, nv, v);
    }
    if (e->distinct && nv > 1) {
        msort(vals, nv, sizeof(Val), val_ptr_cmp, NULL);
        int m = 1;
        for (int i = 1; i < nv; i++) if (order_cmp(vals[i], vals[m - 1]) != 0) vals[m++] = vals[i];
        nv = m;
    }
    switch (e->op) {
    case A_COUNT: return v_num(nv);
    case A_FIRST: return nv ? vals[0] : v_null();
    case A_LAST:  return nv ? vals[nv - 1] : v_null();
    case A_SUM: case A_AVG: {
        if (!nv) return v_null();
        double sum = 0, d;
        for (int i = 0; i < nv; i++) {
            if (!sv_num(vals[i], &d)) return mismatch(x, e->name);
            sum += d;
        }
        return v_num(e->op == A_SUM ? sum : sum / nv);
    }
    case A_MIN: case A_MAX: {
        if (!nv) return v_null();
        Val best = vals[0];
        for (int i = 1; i < nv; i++) {
            int r = sql_cmp(vals[i], best);
            if ((e->op == A_MIN && r < 0) || (e->op == A_MAX && r > 0)) best = vals[i];
        }
        return best;
    }
    }
    return v_null();
}

/* ------------------------------------------------------------ functions */
enum { U_YEAR = 1, U_QUARTER, U_MONTH, U_DAYOFYEAR, U_DAY, U_WEEKDAY, U_WEEK, U_HOUR, U_MINUTE, U_SECOND };
static int date_unit(const char *u) {
    static const struct { const char *n; int u; } UN[] = {
        {"yyyy", U_YEAR}, {"yy", U_YEAR}, {"year", U_YEAR}, {"q", U_QUARTER}, {"qq", U_QUARTER},
        {"quarter", U_QUARTER}, {"m", U_MONTH}, {"mm", U_MONTH}, {"month", U_MONTH},
        {"y", U_DAYOFYEAR}, {"dy", U_DAYOFYEAR}, {"dayofyear", U_DAYOFYEAR},
        {"d", U_DAY}, {"dd", U_DAY}, {"day", U_DAY}, {"w", U_WEEKDAY}, {"dw", U_WEEKDAY},
        {"weekday", U_WEEKDAY}, {"ww", U_WEEK}, {"wk", U_WEEK}, {"week", U_WEEK},
        {"h", U_HOUR}, {"hh", U_HOUR}, {"hour", U_HOUR}, {"n", U_MINUTE}, {"mi", U_MINUTE},
        {"minute", U_MINUTE}, {"s", U_SECOND}, {"ss", U_SECOND}, {"second", U_SECOND}, {NULL, 0}
    };
    for (int i = 0; UN[i].n; i++) if (!kf_stricmp(UN[i].n, u)) return UN[i].u;
    return 0;
}

static double add_months(double d, long n) {
    int y, mo, dd, h, mi, s;
    date_to_parts(d, &y, &mo, &dd, &h, &mi, &s);
    long total = (long)y * 12 + (mo - 1) + n;
    y = (int)(total / 12); mo = (int)(total % 12) + 1;
    if (dd > days_in_month(y, mo)) dd = days_in_month(y, mo);
    return date_from_parts(y, mo, dd, h, mi, s);
}

static int arg_num(Exec *x, Expr *e, Val v, double *out) {
    if (num_of(v, out)) return 1;
    xerr(x, "Data type mismatch in criteria expression (argument of %s is not numeric: '%.40s').", e->name, sv_str(v));
    return 0;
}
static int arg_date(Exec *x, Expr *e, Val v, double *out) {
    if (sv_date(v, out)) return 1;
    xerr(x, "Data type mismatch in criteria expression (argument of %s is not a date: '%.40s').", e->name, sv_str(v));
    return 0;
}

static char *str_trim(const char *s, int left, int right) {
    if (left) while (*s && isspace((unsigned char)*s)) s++;
    size_t n = strlen(s);
    if (right) while (n && isspace((unsigned char)s[n - 1])) n--;
    return kstrndup(s, n);
}

/* 1-based position of needle in hay at or after start (case-insensitive), 0 if none */
static long str_find(const char *hay, const char *needle, long start) {
    if (start < 1) start = 1;
    if (start > u8_len(hay) + 1) return 0;
    const char *h = hay + u8_off(hay, start - 1);
    const char *f = kf_stristr(h, needle);
    if (!f) return 0;
    long pos = start;
    for (const char *q = h; q < f; q++) if ((*q & 0xC0) != 0x80) pos++;
    return pos;
}

static Val eval_func(Exec *x, Expr *e, Ctx *c) {
    /* lazily evaluated functions */
    switch (e->op) {
    case F_IIF: {
        Val cond = eval(x, e->args[0], c);
        return eval(x, e->args[truthy(cond) ? 1 : 2], c);
    }
    case F_COALESCE: case F_NZ: case F_ISNULL:
        if (e->op == F_ISNULL && e->nargs == 1) return vbool(is_null(eval(x, e->args[0], c)));
        for (int i = 0; i < e->nargs; i++) {
            Val v = eval(x, e->args[i], c);
            if (x->failed || !is_null(v)) return v;
        }
        return e->op == F_NZ && e->nargs == 1 ? v_str("") : v_null();
    case F_NOW: return v_date(date_now());
    case F_DATE: return v_date(floor(date_now()));
    case F_IDENTITY: return g_have_identity ? v_num(g_identity) : v_null();
    }
    Val a[3] = {v_null(), v_null(), v_null()};
    Val *av = a;
    if (e->nargs > 3) av = kmalloc(sizeof(Val) * e->nargs);
    int anynull = 0;
    for (int i = 0; i < e->nargs; i++) {
        av[i] = eval(x, e->args[i], c);
        if (x->failed) return v_null();
        if (is_null(av[i])) anynull = 1;
    }
    if (e->op == F_CONCAT) {
        Buf b; buf_init(&b);
        for (int i = 0; i < e->nargs; i++) buf_puts(&b, sv_str(av[i]));
        return v_str(buf_cstr(&b));
    }
    if (e->op == F_NULLIF) {
        if (!anynull && sql_cmp(av[0], av[1]) == 0) return v_null();
        return av[0];
    }
    if (anynull) return v_null();                       /* everything else propagates NULL */
    double n1, n2, d;
    const char *s0 = sv_str(av[0]);
    switch (e->op) {
    case F_UPPER: return v_str(kf_upper(s0));
    case F_LOWER: return v_str(kf_lower(s0));
    case F_LEN: return v_num(u8_len(s0));
    case F_TRIM: return v_str(str_trim(s0, 1, 1));
    case F_LTRIM: return v_str(str_trim(s0, 1, 0));
    case F_RTRIM: return v_str(str_trim(s0, 0, 1));
    case F_LEFT: case F_RIGHT: {
        if (!arg_num(x, e, av[1], &n1)) return v_null();
        long len = u8_len(s0), k = (long)n1;
        if (k < 0) k = 0;
        if (k > len) k = len;
        if (e->op == F_LEFT) return v_str(kstrndup(s0, u8_off(s0, k)));
        return v_str(kstrdup(s0 + u8_off(s0, len - k)));
    }
    case F_MID: {
        if (!arg_num(x, e, av[1], &n1)) return v_null();
        long len = u8_len(s0), st = (long)n1, cnt = len;
        if (e->nargs == 3) { if (!arg_num(x, e, av[2], &n2)) return v_null(); cnt = (long)n2; }
        if (st < 1) { cnt += st - 1; st = 1; }           /* SQL Server semantics for start <= 0 */
        if (cnt <= 0 || st > len) return v_str("");
        size_t b0 = u8_off(s0, st - 1);
        size_t b1 = b0 + u8_off(s0 + b0, cnt);
        return v_str(kstrndup(s0 + b0, b1 - b0));
    }
    case F_ROUND:
        if (!arg_num(x, e, av[0], &n1)) return v_null();
        n2 = 0;
        if (e->nargs == 2 && !arg_num(x, e, av[1], &n2)) return v_null();
        return v_num(round_places(n1, (int)n2));
    case F_ABS: case F_INT: case F_FIX: case F_FLOOR: case F_CEILING: case F_SQRT: case F_SIGN:
    case F_CINT: case F_CDBL:
        if (!arg_num(x, e, av[0], &n1)) return v_null();
        switch (e->op) {
        case F_ABS: return v_num(fabs(n1));
        case F_INT: case F_FLOOR: return v_num(floor(n1));
        case F_FIX: return v_num(trunc(n1));
        case F_CEILING: return v_num(ceil(n1));
        case F_SIGN: return v_num(n1 > 0 ? 1 : n1 < 0 ? -1 : 0);
        case F_CINT: return v_num(round_places(n1, 0));
        case F_CDBL: return v_num(n1);
        default:
            if (n1 < 0) { xerr(x, "Invalid procedure call: SQRT of a negative number."); return v_null(); }
            return v_num(sqrt(n1));
        }
    case F_POWER: case F_MOD:
        if (!arg_num(x, e, av[0], &n1) || !arg_num(x, e, av[1], &n2)) return v_null();
        if (e->op == F_POWER) return v_num(pow(n1, n2));
        if (n2 == 0) { xerr(x, "Division by zero."); return v_null(); }
        return v_num(fmod(n1, n2));
    case F_YEAR: case F_MONTH: case F_DAY: case F_HOUR: case F_MINUTE: case F_SECOND: case F_WEEKDAY: {
        if (!arg_date(x, e, av[0], &d)) return v_null();
        int y, mo, dd, h, mi, s;
        date_to_parts(d, &y, &mo, &dd, &h, &mi, &s);
        switch (e->op) {
        case F_YEAR: return v_num(y);
        case F_MONTH: return v_num(mo);
        case F_DAY: return v_num(dd);
        case F_HOUR: return v_num(h);
        case F_MINUTE: return v_num(mi);
        case F_SECOND: return v_num(s);
        default: return v_num(date_dow(d));
        }
    }
    case F_REPLACE: {
        const char *find = sv_str(av[1]), *rep = sv_str(av[2]);
        size_t fl = strlen(find);
        if (!fl) return v_str(s0);
        Buf b; buf_init(&b);
        const char *p = s0, *f;
        while ((f = kf_stristr(p, find))) { buf_put(&b, p, f - p); buf_puts(&b, rep); p = f + fl; }
        buf_puts(&b, p);
        return v_str(buf_cstr(&b));
    }
    case F_INSTR:                                       /* InStr([start,] haystack, needle) */
        if (e->nargs == 3) {
            if (!arg_num(x, e, av[0], &n1)) return v_null();
            return v_num(str_find(sv_str(av[1]), sv_str(av[2]), (long)n1));
        }
        return v_num(str_find(s0, sv_str(av[1]), 1));
    case F_CHARINDEX:                                   /* CHARINDEX(needle, haystack [, start]) */
        n1 = 1;
        if (e->nargs == 3 && !arg_num(x, e, av[2], &n1)) return v_null();
        return v_num(str_find(sv_str(av[1]), s0, (long)n1));
    case F_STR: return v_str(s0);
    case F_VAL: {
        char *end;
        double v = strtod(str_trim(s0, 1, 0), &end);
        return v_num(isfinite(v) ? v : 0);
    }
    case F_CDATE:
        if (!arg_date(x, e, av[0], &d)) return v_null();
        return v_date(d);
    case F_DATESERIAL:
        if (!arg_num(x, e, av[0], &n1) || !arg_num(x, e, av[1], &n2) || !arg_num(x, e, av[2], &d)) return v_null();
        return v_date(add_months(date_from_parts((int)n1, 1, 1, 0, 0, 0), (long)n2 - 1) + (long)d - 1);
    case F_DATEADD: case F_DATEDIFF: case F_DATEPART: {
        int u = date_unit(s0);
        if (!u) { xerr(x, "Invalid procedure call: unknown date interval '%s' in %s.", s0, e->name); return v_null(); }
        if (e->op == F_DATEPART) {
            if (!arg_date(x, e, av[1], &d)) return v_null();
            int y, mo, dd, h, mi, s;
            date_to_parts(d, &y, &mo, &dd, &h, &mi, &s);
            switch (u) {
            case U_YEAR: return v_num(y);
            case U_QUARTER: return v_num((mo - 1) / 3 + 1);
            case U_MONTH: return v_num(mo);
            case U_DAYOFYEAR: return v_num(floor(d) - date_from_parts(y, 1, 1, 0, 0, 0) + 1);
            case U_DAY: return v_num(dd);
            case U_WEEKDAY: return v_num(date_dow(d));
            case U_WEEK: {
                double jan1 = date_from_parts(y, 1, 1, 0, 0, 0);
                return v_num(floor((floor(d) - jan1 + date_dow(jan1) - 1) / 7) + 1);
            }
            case U_HOUR: return v_num(h);
            case U_MINUTE: return v_num(mi);
            default: return v_num(s);
            }
        }
        if (e->op == F_DATEADD) {
            if (!arg_num(x, e, av[1], &n1) || !arg_date(x, e, av[2], &d)) return v_null();
            long k = (long)trunc(n1);
            switch (u) {
            case U_YEAR: return v_date(add_months(d, k * 12));
            case U_QUARTER: return v_date(add_months(d, k * 3));
            case U_MONTH: return v_date(add_months(d, k));
            case U_WEEK: return v_date(d + k * 7.0);
            case U_HOUR: return v_date(d + k / 24.0);
            case U_MINUTE: return v_date(d + k / 1440.0);
            case U_SECOND: return v_date(d + k / 86400.0);
            default: return v_date(d + k);
            }
        }
        double d1, d2;
        if (!arg_date(x, e, av[1], &d1) || !arg_date(x, e, av[2], &d2)) return v_null();
        int y1, m1, y2, m2;
        date_to_parts(d1, &y1, &m1, NULL, NULL, NULL, NULL);
        date_to_parts(d2, &y2, &m2, NULL, NULL, NULL, NULL);
        long long s1 = llround(d1 * 86400.0), s2 = llround(d2 * 86400.0);
        switch (u) {
        case U_YEAR: return v_num(y2 - y1);
        case U_QUARTER: return v_num((y2 * 4 + (m2 - 1) / 3) - (y1 * 4 + (m1 - 1) / 3));
        case U_MONTH: return v_num((y2 * 12 + m2) - (y1 * 12 + m1));
        case U_WEEK: return v_num(trunc((floor(d2) - floor(d1)) / 7));
        case U_HOUR: return v_num(floor(s2 / 3600.0) - floor(s1 / 3600.0));
        case U_MINUTE: return v_num(floor(s2 / 60.0) - floor(s1 / 60.0));
        case U_SECOND: return v_num((double)(s2 - s1));
        default: return v_num(floor(d2) - floor(d1));
        }
    }
    case F_ASCII: return v_num((unsigned char)s0[0]);
    case F_CHR: {
        if (!arg_num(x, e, av[0], &n1)) return v_null();
        char ch = (char)(int)n1;
        return v_str(kstrndup(&ch, 1));
    }
    case F_SPACE: case F_REPLICATE: {
        const char *unit = e->op == F_SPACE ? " " : s0;
        if (!arg_num(x, e, av[e->op == F_SPACE ? 0 : 1], &n1)) return v_null();
        long k = (long)n1;
        if (k < 0) k = 0;
        if (k * (long)strlen(unit) > 1000000) { xerr(x, "%s result is too long.", e->name); return v_null(); }
        Buf b; buf_init(&b);
        for (long i = 0; i < k; i++) buf_puts(&b, unit);
        return v_str(buf_cstr(&b));
    }
    case F_REVERSE: {
        size_t l = strlen(s0);
        char *r = kmalloc(l + 1);
        for (size_t i = 0; i < l; i++) r[i] = s0[l - 1 - i];
        return v_str(r);
    }
    }
    return v_null();
}

/* store-time conversion of a value into a column's type */
static int coerce(Exec *x, Val in, ColDef *cd, Val *out) {
    double d;
    if (is_null(in)) { *out = in; return 1; }
    switch (cd->ct) {
    case CT_INT: case CT_FLOAT:
        if (in.t == VT_STR && is_blank(in.u.str.s)) { *out = v_null(); return 1; }  /* CF's '' -> NULL */
        if (!sv_num(in, &d) || !isfinite(d)) break;
        if (cd->ct == CT_INT) d = round_places(d, 0);
        else if (cd->scale >= 0) d = round_places(d, cd->scale);
        *out = v_num(d);
        return 1;
    case CT_BIT: {
        int b;
        if (in.t == VT_STR && is_blank(in.u.str.s)) { *out = v_null(); return 1; }
        if (!v_tobool(in.t == VT_DATE ? v_num(in.u.n) : in, &b)) break;
        *out = v_num(b ? 1 : 0);
        return 1;
    }
    case CT_DATE:
        if (in.t == VT_STR && is_blank(in.u.str.s)) { *out = v_null(); return 1; }
        if (!sv_date(in, &d)) break;
        *out = v_date(d);
        return 1;
    default: {
        const char *s = sv_str(in);
        if (cd->size > 0 && u8_len(s) > cd->size) {
            xerr(x, "The field '%s' is too small to accept the amount of data you attempted to add (%ld characters, maximum %d). Try inserting or pasting less data.",
                 cd->name, u8_len(s), cd->size);
            return 0;
        }
        *out = in.t == VT_STR ? in : v_str(s);
        return 1;
    }
    }
    xerr(x, "Data type mismatch in criteria expression: '%.40s' cannot be stored in field '%s' (%s).", sv_str(in), cd->name, cd->tname);
    return 0;
}

static Val eval(Exec *x, Expr *e, Ctx *c) {
    if (x->failed) return v_null();
    switch (e->k) {
    case E_LIT: return e->v;
    case E_COL: {
        Ctx *cc = c;
        for (int d = 0; d < e->depth && cc; d++) cc = cc->parent;
        if (!cc || !cc->tuple || e->src < 0) return v_null();
        Val *row = cc->tuple[e->src];
        return row ? row[e->col] : v_null();
    }
    case E_IDENTITY: return g_have_identity ? v_num(g_identity) : v_null();
    case E_NEG: {
        Val a = eval(x, e->a, c);
        double d;
        if (is_null(a)) return a;
        if (!num_of(a, &d)) return mismatch(x, "unary minus");
        return v_num(-d);
    }
    case E_NOT: {
        Val a = eval(x, e->a, c);
        return is_null(a) ? a : vbool(!truthy(a));
    }
    case E_ARITH: {
        Val a = eval(x, e->a, c), b = eval(x, e->b, c);
        return arith(x, e->op, a, b);
    }
    case E_CONCAT: {
        Val a = eval(x, e->a, c), b = eval(x, e->b, c);
        if (is_null(a) && is_null(b)) return v_null();
        return v_str(kprintf("%s%s", sv_str(a), sv_str(b)));
    }
    case E_CMP: {
        Val a = eval(x, e->a, c), b = eval(x, e->b, c);
        return cmp_op(e->op, a, b);
    }
    case E_AND: {
        Val a = eval(x, e->a, c);
        if (!is_null(a) && !truthy(a)) return vbool(0);
        Val b = eval(x, e->b, c);
        if (!is_null(b) && !truthy(b)) return vbool(0);
        return is_null(a) || is_null(b) ? v_null() : vbool(1);
    }
    case E_OR: {
        Val a = eval(x, e->a, c);
        if (truthy(a)) return vbool(1);
        Val b = eval(x, e->b, c);
        if (truthy(b)) return vbool(1);
        return is_null(a) || is_null(b) ? v_null() : vbool(0);
    }
    case E_LIKE: {
        Val a = eval(x, e->a, c), b = eval(x, e->b, c);
        if (is_null(a) || is_null(b)) return v_null();
        return vbool(like_match(sv_str(a), sv_str(b)) != e->neg);
    }
    case E_INLIST: {
        Val a = eval(x, e->a, c);
        if (is_null(a)) return a;
        int sawnull = 0;
        for (int i = 0; i < e->nargs; i++) {
            Val b = eval(x, e->args[i], c);
            if (is_null(b)) { sawnull = 1; continue; }
            if (sql_cmp(a, b) == 0) return vbool(!e->neg);
        }
        return sawnull ? v_null() : vbool(e->neg);
    }
    case E_INSUB: {
        Val a = eval(x, e->a, c);
        if (is_null(a)) return a;
        ResultSet *rs = run_sub(x, e->sub, c);
        if (!rs) return v_null();
        int sawnull = 0;
        for (int r = 0; r < rs->nrows; r++) {
            Val b = rs->rows[r][0];
            if (is_null(b)) { sawnull = 1; continue; }
            if (sql_cmp(a, b) == 0) return vbool(!e->neg);
        }
        return sawnull ? v_null() : vbool(e->neg);
    }
    case E_EXISTS: {
        ResultSet *rs = run_sub(x, e->sub, c);
        if (!rs) return v_null();
        return vbool((rs->nrows > 0) != e->neg);
    }
    case E_SUBQ: {
        ResultSet *rs = run_sub(x, e->sub, c);
        if (!rs) return v_null();
        if (rs->nrows == 0) return v_null();
        if (rs->nrows > 1) { xerr(x, "At most one record can be returned by this subquery."); return v_null(); }
        return rs->rows[0][0];
    }
    case E_BETWEEN: {
        Val a = eval(x, e->a, c), lo = eval(x, e->b, c), hi = eval(x, e->c, c);
        if (is_null(a) || is_null(lo) || is_null(hi)) return v_null();
        int in = sql_cmp(a, lo) >= 0 && sql_cmp(a, hi) <= 0;
        return vbool(in != e->neg);
    }
    case E_ISNULL: {
        Val a = eval(x, e->a, c);
        return vbool(is_null(a) != e->neg);
    }
    case E_FUNC: return eval_func(x, e, c);
    case E_AGG: return eval_agg(x, e, c);
    case E_CASE: {
        Val base = e->a ? eval(x, e->a, c) : v_null();
        for (int i = 0; i + 1 < e->nargs; i += 2) {
            Val w = eval(x, e->args[i], c);
            int hit = e->a ? (!is_null(base) && !is_null(w) && sql_cmp(base, w) == 0) : truthy(w);
            if (hit) return eval(x, e->args[i + 1], c);
        }
        return e->b ? eval(x, e->b, c) : v_null();
    }
    case E_CAST: {
        Val a = eval(x, e->a, c), out;
        ColDef cd = *e->cd;
        cd.name = "CAST";
        if (cd.ct == CT_TEXT && cd.size > 0) {            /* CAST truncates instead of failing */
            const char *s = sv_str(a);
            if (!is_null(a) && u8_len(s) > cd.size) a = v_str(kstrndup(s, u8_off(s, cd.size)));
        }
        if (!coerce(x, a, &cd, &out)) return v_null();
        return out;
    }
    }
    return v_null();
}

/* ============================================================== execution */
typedef struct TList { Val ***v; int n; } TList;

static Val **tuple_dup(Val **t, int ns) {
    Val **r = kmalloc(sizeof(Val *) * (ns ? ns : 1));
    if (ns) memcpy(r, t, sizeof(Val *) * ns);
    return r;
}
static void tuple_merge(Val **dst, Val **a, Val **b, int ns) {
    for (int i = 0; i < ns; i++) dst[i] = a[i] ? a[i] : b[i];
}
static uint64_t join_mask(JoinNode *j) {
    if (j->kind == J_LEAF) return (uint64_t)1 << j->src;
    return join_mask(j->l) | join_mask(j->r);
}

static int pass_all(Exec *x, Expr **cj, int n, Ctx *c) {
    for (int k = 0; k < n; k++) {
        Val v = eval(x, cj[k], c);
        if (x->failed || !truthy(v)) return 0;
    }
    return 1;
}

static int eval_join(Exec *x, Select *s, JoinNode *j, Ctx *outer, TList *out) {
    int ns = s->nsrc;
    out->v = NULL; out->n = 0;
    if (j->kind == J_LEAF) {
        Src *src = s->srcs[j->src];
        for (int r = 0; r < src->nrows; r++) {
            Val **t = kmalloc(sizeof(Val *) * ns);
            t[j->src] = src->rows[r];
            VPUSH(out->v, out->n, t);
        }
        return 1;
    }
    TList L, R;
    if (!eval_join(x, s, j->l, outer, &L) || !eval_join(x, s, j->r, outer, &R)) return 0;
    TList *A = &L, *B = &R;
    if (j->kind == J_RIGHT) { A = &R; B = &L; }       /* iterate the preserved side */
    Val **scratch = kmalloc(sizeof(Val *) * ns);
    Ctx c; memset(&c, 0, sizeof c);
    c.parent = outer; c.tuple = scratch;
    for (int i = 0; i < A->n; i++) {
        int matched = 0;
        for (int k = 0; k < B->n; k++) {
            tuple_merge(scratch, A->v[i], B->v[k], ns);
            if (j->on) {
                Val v = eval(x, j->on, &c);
                if (x->failed) return 0;
                if (!truthy(v)) continue;
            }
            VPUSH(out->v, out->n, tuple_dup(scratch, ns));
            matched = 1;
        }
        if (!matched && (j->kind == J_LEFT || j->kind == J_RIGHT)) VPUSH(out->v, out->n, A->v[i]);
    }
    return 1;
}

/* sort contexts */
typedef struct OrdCtx { int n; int *idx; int *desc; } OrdCtx;
static int row_order_cmp(const void *pa, const void *pb, void *vc) {
    Val *a = *(Val *const *)pa, *b = *(Val *const *)pb;
    OrdCtx *c = vc;
    for (int k = 0; k < c->n; k++) {
        int r = order_cmp(a[c->idx[k]], b[c->idx[k]]);
        if (r) return c->desc[k] ? -r : r;
    }
    return 0;
}

typedef struct GRow { Val *key; Val **t; } GRow;
static int grow_cmp(const void *pa, const void *pb, void *vc) {
    const GRow *a = *(GRow *const *)pa, *b = *(GRow *const *)pb;
    int n = *(int *)vc;
    for (int k = 0; k < n; k++) {
        int r = order_cmp(a->key[k], b->key[k]);
        if (r) return r;
    }
    return 0;
}

typedef struct DRow { Val *row; int dup; } DRow;
static int drow_cmp(const void *pa, const void *pb, void *vc) {
    const DRow *a = *(DRow *const *)pa, *b = *(DRow *const *)pb;
    int w = *(int *)vc;
    for (int i = 0; i < w; i++) {
        int r = order_cmp(a->row[i], b->row[i]);
        if (r) return r;
    }
    return 0;
}

/* drop duplicate rows (first width columns), keeping first occurrences in order */
static int rows_distinct(Val **rows, int n, int width) {
    if (n < 2) return n;
    DRow *store = kmalloc(sizeof(DRow) * n);
    DRow **d = kmalloc(sizeof(DRow *) * n);
    for (int i = 0; i < n; i++) { store[i].row = rows[i]; d[i] = &store[i]; }
    msort(d, n, sizeof(DRow *), drow_cmp, &width);    /* stable: first occurrence leads */
    for (int i = 1; i < n; i++) if (drow_cmp(&d[i - 1], &d[i], &width) == 0) d[i]->dup = 1;
    int m = 0;
    for (int i = 0; i < n; i++) if (!store[i].dup) rows[m++] = store[i].row;
    return m;
}

static void apply_window(Val ***rows, int *n, double top, int pct, long limit, long offset) {
    if (top >= 0) {
        long k = pct ? (long)ceil(*n * top / 100.0) : (long)top;
        if (k < *n) *n = (int)k;
    }
    if (offset > 0) {
        if (offset >= *n) { *n = 0; return; }
        *rows += offset;
        *n -= (int)offset;
    }
    if (limit >= 0 && limit < *n) *n = (int)limit;
}

static Val *project(Exec *x, Select *s, Ctx *c, int nk) {
    int nout = s->nitems;
    Val *row = kmalloc(sizeof(Val) * (nout + nk + 1));
    for (int i = 0; i < nout; i++) row[i] = eval(x, s->items[i]->e, c);
    for (int k = 0; k < nk; k++) {
        OrderItem *o = s->order[k];
        row[nout + k] = o->outcol >= 0 ? row[o->outcol] : eval(x, o->e, c);
    }
    return x->failed ? NULL : row;
}

static ResultSet *exec_core(Exec *x, Select *s, Ctx *outer, int final) {
    int ns = s->nsrc;
    /* materialise sources */
    for (int i = 0; i < ns; i++) {
        Src *src = s->srcs[i];
        if (src->sub) {
            ResultSet *r = exec_select(x, src->sub, outer);
            if (!r) return NULL;
            src->rows = r->rows; src->nrows = r->nrows;
        } else {
            src->rows = src->tab->rows; src->nrows = src->tab->nrows;
        }
    }
    /* FROM: cross the comma-separated join expressions, applying each WHERE
     * conjunct as soon as every table it mentions is present */
    TList acc = {NULL, 0};
    Val **empty = kmalloc(sizeof(Val *) * (ns ? ns : 1));
    VPUSH(acc.v, acc.n, empty);
    uint64_t have = 0;
    char *applied = kmalloc(s->nconj + 1);
    Ctx c; memset(&c, 0, sizeof c);
    c.parent = outer;
    for (int f = 0; f < s->nfrom; f++) {
        TList r;
        if (!eval_join(x, s, s->from[f], outer, &r)) return NULL;
        uint64_t fm = join_mask(s->from[f]);
        have |= fm;
        Expr **cj = NULL; int ncj = 0;
        /* conjuncts that only need this FROM item filter it before the cross product */
        for (int k = 0; k < s->nconj; k++)
            if (!applied[k] && s->conjmask[k] && !(s->conjmask[k] & ~fm)) { applied[k] = 1; VPUSH(cj, ncj, s->conj[k]); }
        if (ncj) {
            int m = 0;
            for (int i = 0; i < r.n; i++) {
                c.tuple = r.v[i];
                if (pass_all(x, cj, ncj, &c)) r.v[m++] = r.v[i];
                else if (x->failed) return NULL;
            }
            r.n = m;
            cj = NULL; ncj = 0;
        }
        for (int k = 0; k < s->nconj; k++)
            if (!applied[k] && !(s->conjmask[k] & ~have)) { applied[k] = 1; VPUSH(cj, ncj, s->conj[k]); }
        TList nx = {NULL, 0};
        Val **scratch = kmalloc(sizeof(Val *) * ns);
        c.tuple = scratch;
        for (int i = 0; i < acc.n; i++) {
            for (int k = 0; k < r.n; k++) {
                tuple_merge(scratch, acc.v[i], r.v[k], ns);
                if (ncj && !pass_all(x, cj, ncj, &c)) { if (x->failed) return NULL; continue; }
                VPUSH(nx.v, nx.n, tuple_dup(scratch, ns));
            }
        }
        acc = nx;
    }
    {   /* whatever is left (no FROM clause at all) */
        Expr **cj = NULL; int ncj = 0;
        for (int k = 0; k < s->nconj; k++) if (!applied[k]) VPUSH(cj, ncj, s->conj[k]);
        if (ncj) {
            int m = 0;
            for (int i = 0; i < acc.n; i++) {
                c.tuple = acc.v[i];
                if (pass_all(x, cj, ncj, &c)) acc.v[m++] = acc.v[i];
                else if (x->failed) return NULL;
            }
            acc.n = m;
        }
    }
    /* project (and group) */
    int nout = s->nitems, nk = final ? s->norder : 0;
    Val **rows = NULL; int nrows = 0;
    if (!s->has_agg) {
        for (int i = 0; i < acc.n; i++) {
            c.tuple = acc.v[i];
            Val *row = project(x, s, &c, nk);
            if (!row) return NULL;
            VPUSH(rows, nrows, row);
        }
    } else {
        GRow **g = kmalloc(sizeof(GRow *) * (acc.n + 1));
        for (int i = 0; i < acc.n; i++) {
            g[i] = kmalloc(sizeof(GRow));
            g[i]->t = acc.v[i];
            if (s->ngroup) {
                g[i]->key = kmalloc(sizeof(Val) * s->ngroup);
                c.tuple = acc.v[i];
                for (int k = 0; k < s->ngroup; k++) g[i]->key[k] = eval(x, s->group[k], &c);
                if (x->failed) return NULL;
            }
        }
        int ng = s->ngroup;
        if (ng) msort(g, acc.n, sizeof(GRow *), grow_cmp, &ng);
        int i = 0;
        do {
            int j = i + 1;
            if (ng) while (j < acc.n && grow_cmp(&g[i], &g[j], &ng) == 0) j++;
            else j = acc.n;
            if (ng && i >= acc.n) break;                /* GROUP BY over no rows: no groups */
            int cnt = j - i;
            if (cnt < 0) cnt = 0;
            Val ***grp = kmalloc(sizeof(Val **) * (cnt + 1));
            for (int k = 0; k < cnt; k++) grp[k] = g[i + k]->t;
            Ctx gc; memset(&gc, 0, sizeof gc);
            gc.parent = outer; gc.grp = grp; gc.ngrp = cnt; gc.grouped = 1;
            gc.tuple = cnt ? grp[0] : empty;
            int keep = 1;
            if (s->having) {
                Val h = eval(x, s->having, &gc);
                if (x->failed) return NULL;
                keep = truthy(h);
            }
            if (keep) {
                Val *row = project(x, s, &gc, nk);
                if (!row) return NULL;
                VPUSH(rows, nrows, row);
            }
            i = j;
        } while (i < acc.n);
    }
    if (s->distinct) nrows = rows_distinct(rows, nrows, nout);
    if (nk) {
        OrdCtx oc;
        oc.n = nk;
        oc.idx = kmalloc(sizeof(int) * nk);
        oc.desc = kmalloc(sizeof(int) * nk);
        for (int k = 0; k < nk; k++) { oc.idx[k] = nout + k; oc.desc[k] = s->order[k]->desc; }
        msort(rows, nrows, sizeof(Val *), row_order_cmp, &oc);
    }
    apply_window(&rows, &nrows, s->top, s->top_percent, final ? s->limit : -1, final ? s->offset : -1);
    ResultSet *rs = kmalloc(sizeof(ResultSet));
    rs->ncols = nout; rs->names = s->outnames; rs->rows = rows; rs->nrows = nrows;
    return rs;
}

static ResultSet *exec_compound(Exec *x, Select *s, Ctx *outer) {
    Val **rows = NULL; int nrows = 0, dedupe = 0;
    for (Select *core = s; core; core = core->next) {
        ResultSet *r = exec_core(x, core, outer, 0);
        if (!r) return NULL;
        if (core != s && !core->union_all) dedupe = 1;
        for (int i = 0; i < r->nrows; i++) VPUSH(rows, nrows, r->rows[i]);
    }
    if (dedupe) nrows = rows_distinct(rows, nrows, s->nitems);
    if (s->norder) {
        OrdCtx oc;
        oc.n = s->norder;
        oc.idx = kmalloc(sizeof(int) * oc.n);
        oc.desc = kmalloc(sizeof(int) * oc.n);
        for (int k = 0; k < oc.n; k++) { oc.idx[k] = s->order[k]->outcol; oc.desc[k] = s->order[k]->desc; }
        msort(rows, nrows, sizeof(Val *), row_order_cmp, &oc);
    }
    apply_window(&rows, &nrows, -1, 0, s->limit, s->offset);
    ResultSet *rs = kmalloc(sizeof(ResultSet));
    rs->ncols = s->nitems; rs->names = s->outnames; rs->rows = rows; rs->nrows = nrows;
    return rs;
}

static ResultSet *exec_select(Exec *x, Select *s, Ctx *outer) {
    if (x->failed) return NULL;
    if (!s->correlated && s->cache) return s->cache;
    ResultSet *rs = s->next ? exec_compound(x, s, outer) : exec_core(x, s, outer, 1);
    if (rs && !s->correlated) s->cache = rs;
    return rs;
}

/* ===================================================== constraint checks */
static int check_notnull(Exec *x, Table *w, Val *row) {
    for (int c = 0; c < w->ncols; c++) {
        if ((w->cols[c].notnull || w->cols[c].pk) && is_null(row[c])) {
            xerr(x, "The field '%s.%s' cannot contain a Null value because the Required property for this field is set to True. Enter a value in this field.",
                 w->name, w->cols[c].name);
            return 0;
        }
    }
    return 1;
}

typedef struct KeyCtx { int *cols; int n; } KeyCtx;
static int key_cmp(const void *pa, const void *pb, void *vc) {
    Val *a = *(Val *const *)pa, *b = *(Val *const *)pb;
    KeyCtx *k = vc;
    for (int i = 0; i < k->n; i++) {
        int r = order_cmp(a[k->cols[i]], b[k->cols[i]]);
        if (r) return r;
    }
    return 0;
}

/* would rows [from, nrows) duplicate a key? from = 0 checks everything */
static int key_dup(Table *w, int *cols, int n, int from) {
    KeyCtx k = {cols, n};
    int added = w->nrows - from;
    if (from > 0 && added <= 8) {                      /* a few new rows: linear scan */
        for (int i = from; i < w->nrows; i++) {
            int hasnull = 0;
            for (int c = 0; c < n; c++) if (is_null(w->rows[i][cols[c]])) hasnull = 1;
            if (hasnull) continue;
            for (int j = 0; j < i; j++) if (key_cmp(&w->rows[i], &w->rows[j], &k) == 0) return 1;
        }
        return 0;
    }
    Val **v = kmalloc(sizeof(Val *) * (w->nrows + 1));
    int m = 0;
    for (int i = 0; i < w->nrows; i++) {
        int hasnull = 0;
        for (int c = 0; c < n; c++) if (is_null(w->rows[i][cols[c]])) hasnull = 1;
        if (!hasnull) v[m++] = w->rows[i];
    }
    msort(v, m, sizeof(Val *), key_cmp, &k);
    for (int i = 1; i < m; i++) if (key_cmp(&v[i - 1], &v[i], &k) == 0) return 1;
    return 0;
}

static int check_unique(Exec *x, Table *w, int from) {
    int *pk = kmalloc(sizeof(int) * (w->ncols + 1)), npk = 0;
    for (int c = 0; c < w->ncols; c++) if (w->cols[c].pk) pk[npk++] = c;
    int bad = npk && key_dup(w, pk, npk, from);
    for (int c = 0; !bad && c < w->ncols; c++)
        if (w->cols[c].unique && !(w->cols[c].pk && npk == 1)) bad = key_dup(w, &c, 1, from);
    if (bad) {
        xerr(x, "The changes you requested to the table were not successful because they would create duplicate values in the index, primary key, or relationship. Change the data in the field or fields that contain duplicate data, remove the index, or redefine the index to permit duplicate entries and try again.");
        return 0;
    }
    return 1;
}

/* ======================================================= DML / DDL */
static Expr **default_exprs(Exec *x, Table *t) {
    Expr **d = kmalloc(sizeof(Expr *) * (t->ncols + 1));
    Select *scope = sel_new();
    for (int c = 0; c < t->ncols; c++) {
        if (!t->cols[c].defexpr) continue;
        d[c] = parse_expr_text(x, t->cols[c].defexpr);
        if (!d[c]) return NULL;
        bind_expr(x, scope, d[c]);
        if (x->failed) return NULL;
    }
    return d;
}

static int eval_default(Exec *x, Expr *d, ColDef *cd, Val *out) {
    Val *nulltuple[1] = {NULL};
    Ctx c; memset(&c, 0, sizeof c);
    c.tuple = nulltuple;
    Val v = eval(x, d, &c);
    return !x->failed && coerce(x, v, cd, out);
}

static int exec_insert(Exec *x, Stmt *st, long *aff) {
    Table *t = table_get(x, st->table, 1);
    if (!t) return 0;
    int nm = st->ncols ? st->ncols : t->ncols;
    int *map = kmalloc(sizeof(int) * (nm + 1));
    for (int i = 0; i < nm; i++) {
        if (!st->ncols) { map[i] = i; continue; }
        map[i] = table_col(t, st->cols[i]);
        if (map[i] < 0) {
            xerr(x, "INSERT INTO statement contains the following unknown field name: '%s'. Make sure you have typed the name correctly, and try the operation again.", st->cols[i]);
            return 0;
        }
        for (int j = 0; j < i; j++) if (map[j] == map[i]) { xerr(x, "Duplicate output destination '%s'.", st->cols[i]); return 0; }
    }
    /* collect source rows */
    Val **src = NULL; int nsrc = 0;
    if (st->sel) {
        bind_select(x, st->sel);
        ResultSet *rs = x->failed ? NULL : exec_select(x, st->sel, NULL);
        if (!rs) return 0;
        if (rs->ncols != nm) { xerr(x, "Number of query values and destination fields are not the same."); return 0; }
        src = rs->rows; nsrc = rs->nrows;
    } else {
        Val *nulltuple[1] = {NULL};
        Ctx c; memset(&c, 0, sizeof c);
        c.tuple = nulltuple;
        for (int r = 0; r < st->nvals; r++) {
            ValRow *vr = st->vals[r];
            if (vr->n != nm) { xerr(x, "Number of query values and destination fields are not the same."); return 0; }
            Val *row = kmalloc(sizeof(Val) * (nm + 1));
            for (int i = 0; i < nm; i++) {
                bind_expr(x, st->scope, vr->e[i]);
                row[i] = eval(x, vr->e[i], &c);
                if (x->failed) return 0;
            }
            VPUSH(src, nsrc, row);
        }
    }
    Expr **defs = default_exprs(x, t);
    if (!defs) return 0;
    Table *w = table_clone(t);
    int first = w->nrows;
    double lastid = 0; int haveid = 0;
    char *given = kmalloc(w->ncols + 1);
    for (int r = 0; r < nsrc; r++) {
        Val *row = kmalloc(sizeof(Val) * w->ncols);
        memset(given, 0, w->ncols);
        for (int i = 0; i < nm; i++) given[map[i]] = 1;
        for (int c = 0; c < w->ncols; c++)
            if (!given[c] && defs[c] && !eval_default(x, defs[c], &w->cols[c], &row[c])) return 0;
        for (int i = 0; i < nm; i++)
            if (!coerce(x, src[r][i], &w->cols[map[i]], &row[map[i]])) return 0;
        for (int c = 0; c < w->ncols; c++) {
            if (!w->cols[c].autoinc) continue;
            if (is_null(row[c])) { row[c] = v_num(w->nextid); w->nextid += 1; }
            else if (row[c].u.n >= w->nextid) w->nextid = floor(row[c].u.n) + 1;
            lastid = row[c].u.n; haveid = 1;
        }
        if (!check_notnull(x, w, row)) return 0;
        table_append(w, row);
    }
    if (!nsrc) { *aff = 0; return 1; }
    if (!check_unique(x, w, first) || !table_commit(x, w)) return 0;
    if (haveid) { g_identity = lastid; g_have_identity = 1; }
    *aff = nsrc;
    return 1;
}

static int exec_update(Exec *x, Stmt *st, long *aff) {
    Select *s = st->sel;
    bind_select(x, s);
    if (x->failed) return 0;
    Table *t = s->srcs[0]->tab;
    int *map = kmalloc(sizeof(int) * (st->ncols + 1));
    for (int i = 0; i < st->ncols; i++) {
        map[i] = table_col(t, st->cols[i]);
        if (map[i] < 0) { xerr(x, "Too few parameters. Expected 1. (Unknown column '%s' in SET clause.)", st->cols[i]); return 0; }
        bind_expr(x, s, st->set[i]);
        if (x->failed) return 0;
        if (expr_has_agg(st->set[i])) { xerr(x, "Cannot have aggregate function in UPDATE expression."); return 0; }
    }
    Table *w = table_clone(t);
    long n = 0;
    Ctx c; memset(&c, 0, sizeof c);
    Val *tp[1];
    c.tuple = tp;
    for (int r = 0; r < t->nrows; r++) {
        tp[0] = t->rows[r];
        if (s->where) {
            Val v = eval(x, s->where, &c);
            if (x->failed) return 0;
            if (!truthy(v)) continue;
        }
        Val *nr = kmalloc(sizeof(Val) * w->ncols);
        memcpy(nr, t->rows[r], sizeof(Val) * w->ncols);
        for (int i = 0; i < st->ncols; i++) {
            Val v = eval(x, st->set[i], &c);              /* expressions see the old row */
            if (x->failed || !coerce(x, v, &w->cols[map[i]], &nr[map[i]])) return 0;
            ColDef *cd = &w->cols[map[i]];
            if (cd->autoinc && !is_null(nr[map[i]]) && nr[map[i]].u.n >= w->nextid) w->nextid = floor(nr[map[i]].u.n) + 1;
        }
        if (!check_notnull(x, w, nr)) return 0;
        w->rows[r] = nr;
        n++;
    }
    if (n && (!check_unique(x, w, 0) || !table_commit(x, w))) return 0;
    *aff = n;
    return 1;
}

static int exec_delete(Exec *x, Stmt *st, long *aff) {
    Select *s = st->sel;
    bind_select(x, s);
    if (x->failed) return 0;
    Table *t = s->srcs[0]->tab;
    Table *w = table_clone(t);
    w->nrows = 0;
    Ctx c; memset(&c, 0, sizeof c);
    Val *tp[1];
    c.tuple = tp;
    for (int r = 0; r < t->nrows; r++) {
        tp[0] = t->rows[r];
        int del = 1;
        if (s->where) {
            Val v = eval(x, s->where, &c);
            if (x->failed) return 0;
            del = truthy(v);
        }
        if (!del) w->rows[w->nrows++] = t->rows[r];
    }
    long n = t->nrows - w->nrows;
    if (n && !table_commit(x, w)) return 0;
    *aff = n;
    return 1;
}

static int exec_create(Exec *x, Stmt *st) {
    if (!sql_valid_table_name(st->table)) { xerr(x, "Invalid table name '%s'.", st->table); return 0; }
    kf_mkdirs(x->dbdir);
    char *real;
    if (table_path(x, st->table, &real)) {
        if (st->ifx) return 1;
        xerr(x, "Table '%s' already exists.", real);
        return 0;
    }
    if (!st->ndefs) { xerr(x, "CREATE TABLE %s has no columns.", st->table); return 0; }
    Table *t = kmalloc(sizeof(Table));
    t->name = st->table;
    t->path = kf_path_join(x->dbdir, kprintf("%s.tbl", st->table));
    t->ncols = st->ndefs;
    t->cols = kmalloc(sizeof(ColDef) * st->ndefs);
    t->nextid = st->seed >= 1 ? floor(st->seed) : 1;
    int nauto = 0;
    for (int i = 0; i < st->ndefs; i++) {
        t->cols[i] = *st->defs[i];
        if (t->cols[i].autoinc) nauto++;
        for (int j = 0; j < i; j++) if (!kf_stricmp(t->cols[j].name, t->cols[i].name)) {
            xerr(x, "Field '%s' is defined more than once.", t->cols[i].name);
            return 0;
        }
    }
    if (nauto > 1) { xerr(x, "Table '%s' may have only one auto-increment (COUNTER) column.", st->table); return 0; }
    if (!default_exprs(x, t)) return 0;                /* validate DEFAULTs now */
    return table_commit(x, t);
}

static int exec_drop(Exec *x, Stmt *st) {
    if (!sql_valid_table_name(st->table)) { xerr(x, "Invalid table name '%s'.", st->table); return 0; }
    char *path = table_path(x, st->table, NULL);
    if (!path) {
        if (st->ifx) return 1;
        xerr(x, "Table '%s' not found.", st->table);
        return 0;
    }
    if (unlink(path) != 0) { xerr(x, "Could not drop table '%s' (%s).", st->table, strerror(errno)); return 0; }
    cache_drop(path);
    return 1;
}

static int exec_addcol(Exec *x, Stmt *st) {
    Table *t = table_get(x, st->table, 1);
    if (!t) return 0;
    ColDef *cd = st->defs[0];
    if (table_col(t, cd->name) >= 0) { xerr(x, "Field '%s' already exists in table '%s'.", cd->name, t->name); return 0; }
    if (cd->autoinc) for (int c = 0; c < t->ncols; c++) if (t->cols[c].autoinc) {
        xerr(x, "Table '%s' may have only one auto-increment (COUNTER) column.", t->name);
        return 0;
    }
    Table *w = table_clone(t);
    w->cols = kmalloc(sizeof(ColDef) * (t->ncols + 1));
    memcpy(w->cols, t->cols, sizeof(ColDef) * t->ncols);
    w->cols[t->ncols] = *cd;
    w->ncols = t->ncols + 1;
    if (cd->autoinc) w->nextid = st->seed >= 1 ? floor(st->seed) : 1;
    Expr *def = NULL;
    if (cd->defexpr) {
        Select *scope = sel_new();
        if (!(def = parse_expr_text(x, cd->defexpr))) return 0;
        bind_expr(x, scope, def);
        if (x->failed) return 0;
    }
    for (int r = 0; r < t->nrows; r++) {
        Val *nr = kmalloc(sizeof(Val) * w->ncols);
        memcpy(nr, t->rows[r], sizeof(Val) * t->ncols);
        if (cd->autoinc) { nr[t->ncols] = v_num(w->nextid); w->nextid += 1; }
        else if (def && !eval_default(x, def, cd, &nr[t->ncols])) return 0;
        if (!check_notnull(x, w, nr)) return 0;
        w->rows[r] = nr;
    }
    if (!check_unique(x, w, 0)) return 0;
    return table_commit(x, w);
}

static int exec_dropcol(Exec *x, Stmt *st) {
    Table *t = table_get(x, st->table, 1);
    if (!t) return 0;
    int k = table_col(t, st->cols[0]);
    if (k < 0) { xerr(x, "Field '%s' does not exist in table '%s'.", st->cols[0], t->name); return 0; }
    if (t->ncols == 1) { xerr(x, "Cannot delete the only field of table '%s'; use DROP TABLE.", t->name); return 0; }
    Table *w = table_clone(t);
    w->ncols = t->ncols - 1;
    for (int c = k; c < w->ncols; c++) w->cols[c] = t->cols[c + 1];
    for (int r = 0; r < t->nrows; r++) {
        Val *nr = kmalloc(sizeof(Val) * w->ncols);
        for (int c = 0, o = 0; c < t->ncols; c++) if (c != k) nr[o++] = t->rows[r][c];
        w->rows[r] = nr;
    }
    return table_commit(x, w);
}

static int exec_stmt(Exec *x, Stmt *st, ResultSet **rs, long *aff) {
    switch (st->kind) {
    case ST_SELECT:
        bind_select(x, st->sel);
        if (x->failed) return 0;
        *rs = exec_select(x, st->sel, NULL);
        return *rs != NULL;
    case ST_INSERT:  return exec_insert(x, st, aff);
    case ST_UPDATE:  return exec_update(x, st, aff);
    case ST_DELETE:  return exec_delete(x, st, aff);
    case ST_CREATE:  return exec_create(x, st);
    case ST_DROP:    return exec_drop(x, st);
    case ST_ADDCOL:  return exec_addcol(x, st);
    case ST_DROPCOL: return exec_dropcol(x, st);
    case ST_NOOP:    return 1;
    }
    xerr(x, "Internal error: unknown statement kind.");
    return 0;
}

/* ============================================================ public API */
/* convert to CF output form inside the private arena (copying every string
 * out of the table cache): NULL -> "", dates -> "yyyy-mm-dd hh:mm:ss" */
static ResultSet *rs_finalize(ResultSet *in) {
    ResultSet *rs = kmalloc(sizeof(ResultSet));
    rs->ncols = in->ncols;
    rs->nrows = in->nrows;
    rs->names = kmalloc(sizeof(char *) * (in->ncols + 1));
    for (int c = 0; c < in->ncols; c++) rs->names[c] = kstrdup(in->names[c]);
    rs->rows = kmalloc(sizeof(Val *) * (in->nrows + 1));
    for (int r = 0; r < in->nrows; r++) {
        Val *row = kmalloc(sizeof(Val) * (in->ncols + 1));
        for (int c = 0; c < in->ncols; c++) {
            Val v = in->rows[r][c];
            switch (v.t) {
            case VT_NUM:  row[c] = v; break;
            case VT_BOOL: row[c] = v_num(v.u.b); break;
            case VT_DATE: row[c] = v_str(fmt_date(v.u.n)); break;
            case VT_STR:  row[c] = v_strdup(v.u.str.s); break;
            default:      row[c] = v_str(""); break;
            }
        }
        rs->rows[r] = row;
    }
    return rs;
}

/* build the caller's Query in the (current) caller arena */
static Query *rs_to_query(ResultSet *rs) {
    Query *q = query_new(0, NULL);
    for (int c = 0; c < rs->ncols; c++) query_add_column(q, rs->names[c]);
    for (int r = 0; r < rs->nrows; r++) {
        int row = query_add_row(q);
        for (int c = 0; c < rs->ncols; c++) {
            Val v = rs->rows[r][c];
            q->data[c][row] = v.t == VT_STR ? v_strdup(v.u.str.s) : v;
        }
    }
    return q;
}

static void put_err(Exec *x, char *err, size_t errlen) {
    if (err && errlen) snprintf(err, errlen, "%s", x->msg);
}

/* execute exactly one statement */
static int exec_one(const char *dbdir, const char *sql, Query **out, long *affected, char *err, size_t errlen) {
    if (out) *out = NULL;
    if (affected) *affected = 0;
    if (err && errlen) err[0] = 0;
    Exec x; memset(&x, 0, sizeof x);
    x.dbdir = dbdir && *dbdir ? dbdir : ".";
    Arena *caller = g_arena, *work = arena_new();
    g_arena = work;
    ResultSet *rs = NULL;
    long aff = 0;
    Stmt *st = NULL;
    if (!sql) xerr(&x, "Invalid SQL statement; the statement is empty.");
    else st = parse_sql(&x, sql);
    if (st && !x.failed) {
        pthread_mutex_lock(&g_lock);
        g_serial++;
        exec_stmt(&x, st, &rs, &aff);
        if (!x.failed && rs) rs = rs_finalize(rs);
        pthread_mutex_unlock(&g_lock);
    }
    g_arena = caller;
    int ok = !x.failed;
    if (ok) {
        if (rs && out) *out = rs_to_query(rs);
        if (affected) *affected = rs ? rs->nrows : aff;
    } else put_err(&x, err, errlen);
    arena_free(work);
    return ok;
}

/* Split text into ;-separated statements, honouring 'strings', "names",
 * [names] and `names` and dropping -- and slash-star comments. fn is called for
 * every non-blank statement (numbered from 1) until it returns 0.
 * Returns the number of statements seen, or -1 if fn failed. */
typedef int (*StmtFn)(const char *stmt, int stmtno, void *ctx);

static int for_each_stmt(const char *text, StmtFn fn, void *ctx) {
    char *buf = malloc(strlen(text) + 1);
    if (!buf) return -1;
    const char *p = text;
    int stmtno = 0;
    while (*p) {
        size_t k = 0;
        int any = 0;
        while (*p && *p != ';') {
            if (p[0] == '-' && p[1] == '-') { while (*p && *p != '\n') p++; continue; }
            if (p[0] == '/' && p[1] == '*') {
                const char *e = strstr(p + 2, "*/");
                p = e ? e + 2 : p + strlen(p);
                buf[k++] = ' ';
                continue;
            }
            if (*p == '\'' || *p == '"' || *p == '[' || *p == '`') {
                char close = *p == '[' ? ']' : *p;
                buf[k++] = *p++;
                while (*p) {
                    if (*p == close) {
                        if (close != ']' && p[1] == close) { buf[k++] = *p++; buf[k++] = *p++; continue; }
                        break;
                    }
                    buf[k++] = *p++;
                }
                if (*p) buf[k++] = *p++;
                any = 1;
                continue;
            }
            if (!isspace((unsigned char)*p)) any = 1;
            buf[k++] = *p++;
        }
        if (*p == ';') p++;
        buf[k] = 0;
        if (!any) continue;
        if (!fn(buf, ++stmtno, ctx)) { free(buf); return -1; }
    }
    free(buf);
    return stmtno;
}

typedef struct Batch {
    const char *dbdir;
    int     want;             /* caller wants a Query back */
    Query  *last;             /* result of the last SELECT in the batch */
    long    affected;         /* rows of the last statement */
    char   *err; size_t errlen;
    const char *suffix;       /* "batch" / "script" for error messages */
} Batch;

static int batch_stmt(const char *stmt, int stmtno, void *vb) {
    Batch *b = vb;
    Query *q = NULL;
    long n = 0;
    if (!exec_one(b->dbdir, stmt, b->want ? &q : NULL, &n, b->err, b->errlen)) {
        if (b->err && b->errlen && (stmtno > 1 || !strcmp(b->suffix, "script"))) {
            size_t l = strlen(b->err);
            snprintf(b->err + l, b->errlen - l, " (%s statement %d)", b->suffix, stmtno);
        }
        return 0;
    }
    if (q) b->last = q;
    b->affected = n;
    return 1;
}

/* One statement, or a ;-separated batch (CF + SQL Server habit:
 * "INSERT ...; SELECT @@IDENTITY AS NewID"). Statements run in order, each
 * atomically on its own; the last result set produced is returned. */
int sql_exec(const char *dbdir, const char *sql, Query **out, long *affected, char *err, size_t errlen) {
    if (out) *out = NULL;
    if (affected) *affected = 0;
    if (err && errlen) err[0] = 0;
    if (!sql) return exec_one(dbdir, NULL, out, affected, err, errlen);
    Batch b; memset(&b, 0, sizeof b);
    b.dbdir = dbdir; b.want = out != NULL; b.err = err; b.errlen = errlen; b.suffix = "batch";
    int n = for_each_stmt(sql, batch_stmt, &b);
    if (n == 0) return exec_one(dbdir, "", out, affected, err, errlen);   /* "statement is empty" */
    if (n < 0) {
        if (err && errlen && !err[0]) snprintf(err, errlen, DRV "Out of memory.");
        return 0;
    }
    if (out) *out = b.last;
    if (affected) *affected = b.affected;
    return 1;
}

int sql_exec_script(const char *dbdir, const char *script, char *err, size_t errlen) {
    if (err && errlen) err[0] = 0;
    if (!script) return 1;
    Batch b; memset(&b, 0, sizeof b);
    b.dbdir = dbdir; b.err = err; b.errlen = errlen; b.suffix = "script";
    int n = for_each_stmt(script, batch_stmt, &b);
    if (n < 0 && err && errlen && !err[0]) snprintf(err, errlen, DRV "Out of memory.");
    return n >= 0;
}

static int name_cmp(const void *pa, const void *pb, void *ctx) {
    (void)ctx;
    return kf_stricmp(*(char *const *)pa, *(char *const *)pb);
}

int sql_list_tables(const char *dbdir, Query **out, char *err, size_t errlen) {
    if (out) *out = NULL;
    if (err && errlen) err[0] = 0;
    Exec x; memset(&x, 0, sizeof x);
    x.dbdir = dbdir && *dbdir ? dbdir : ".";
    Arena *caller = g_arena, *work = arena_new();
    g_arena = work;
    ResultSet *rs = kmalloc(sizeof(ResultSet));
    static char *names[] = {"TABLE_NAME", "COLUMN_COUNT", "ROW_COUNT"};
    rs->ncols = 3; rs->names = names;
    pthread_mutex_lock(&g_lock);
    g_serial++;
    DIR *d = opendir(x.dbdir);
    if (!d) xerr(&x, "Data source directory '%s' not found.", x.dbdir);
    else {
        char **tn = NULL; int ntn = 0;
        struct dirent *de;
        while ((de = readdir(d))) {
            size_t l = strlen(de->d_name);
            if (l > 4 && !strcmp(de->d_name + l - 4, ".tbl")) {
                char *nm = kstrndup(de->d_name, l - 4);
                if (sql_valid_table_name(nm)) VPUSH(tn, ntn, nm);
            }
        }
        closedir(d);
        msort(tn, ntn, sizeof(char *), name_cmp, NULL);
        for (int i = 0; i < ntn && !x.failed; i++) {
            Table *t = table_load(&x, kf_path_join(x.dbdir, kprintf("%s.tbl", tn[i])), tn[i]);
            if (!t) break;
            Val *row = kmalloc(sizeof(Val) * 3);
            row[0] = v_strdup(tn[i]);
            row[1] = v_num(t->ncols);
            row[2] = v_num(t->nrows);
            VPUSH(rs->rows, rs->nrows, row);
        }
    }
    pthread_mutex_unlock(&g_lock);
    g_arena = caller;
    int ok = !x.failed;
    if (ok && out) *out = rs_to_query(rs);
    if (!ok) put_err(&x, err, errlen);
    arena_free(work);
    return ok;
}

int sql_describe(const char *dbdir, const char *table, Query **out, char *err, size_t errlen) {
    if (out) *out = NULL;
    if (err && errlen) err[0] = 0;
    Exec x; memset(&x, 0, sizeof x);
    x.dbdir = dbdir && *dbdir ? dbdir : ".";
    Arena *caller = g_arena, *work = arena_new();
    g_arena = work;
    ResultSet *rs = kmalloc(sizeof(ResultSet));
    static char *names[] = {"COLUMN_NAME", "TYPE_NAME", "ORDINAL", "IS_NULLABLE", "IS_PRIMARY_KEY",
                            "IS_AUTOINCREMENT", "COLUMN_DEFAULT"};
    rs->ncols = 7; rs->names = names;
    pthread_mutex_lock(&g_lock);
    g_serial++;
    Table *t = table_get(&x, table ? table : "", 1);
    if (t) {
        for (int c = 0; c < t->ncols; c++) {
            ColDef *cd = &t->cols[c];
            Val *row = kmalloc(sizeof(Val) * 7);
            row[0] = v_strdup(cd->name);
            row[1] = v_strdup(cd->tname);
            row[2] = v_num(c + 1);
            row[3] = v_str(cd->notnull || cd->pk ? "NO" : "YES");
            row[4] = v_str(cd->pk ? "YES" : "NO");
            row[5] = v_str(cd->autoinc ? "YES" : "NO");
            row[6] = v_strdup(cd->defexpr ? cd->defexpr : "");
            VPUSH(rs->rows, rs->nrows, row);
        }
    }
    pthread_mutex_unlock(&g_lock);
    g_arena = caller;
    int ok = !x.failed;
    if (ok && out) *out = rs_to_query(rs);
    if (!ok) put_err(&x, err, errlen);
    arena_free(work);
    return ok;
}

int sql_last_identity(double *out) {
    if (out) *out = g_have_identity ? g_identity : 0;
    return g_have_identity;
}
