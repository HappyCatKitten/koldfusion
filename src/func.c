/*
 * func.c - CFML built-in functions, part 1: helpers, lists, strings,
 * formatting (DateFormat, NumberFormat, DollarFormat ...), regular expressions.
 */
#define _GNU_SOURCE
#include "engine.h"
#include "func.h"
#include <stdlib.h>
#include <ctype.h>
#include <math.h>
#include <regex.h>
#include <time.h>
#include <pthread.h>

/* ================================================================ arg helpers */
const char *fn_name(Expr *call) { return call && call->name ? kf_upper(call->name) : "?"; }

static const char *argdesc(Val v) {
    if (v_is_simple(v)) return kf_html_escape(v_tostr(v));
    return kprintf("[%s]", v_typename(v));
}

void fn_param_error(Ctx *c, Expr *call, int i, Val v, const char *must) {
    kf_throw_at(c, call, "Expression", kprintf("Parameter validation error for function %s.", fn_name(call)),
                kprintf("Parameter %d of function %s, which is now \"%s\", %s.", i + 1, fn_name(call), argdesc(v), must));
}

const char *fa_str(Ctx *c, Expr *call, Val *argv, int i) {
    if (!v_is_simple(argv[i]) && argv[i].t != VT_BINARY) fn_param_error(c, call, i, argv[i], "must be a simple value");
    return v_tostr(argv[i]);
}
double fa_num(Ctx *c, Expr *call, Val *argv, int i) {
    double d;
    if (!v_tonum(argv[i], &d)) fn_param_error(c, call, i, argv[i], "must be a number");
    return d;
}
int fa_int(Ctx *c, Expr *call, Val *argv, int i) { return (int)floor(fa_num(c, call, argv, i) + 1e-9); }
int fa_bool(Ctx *c, Expr *call, Val *argv, int i) {
    int b;
    if (!v_tobool(argv[i], &b)) fn_param_error(c, call, i, argv[i], "must be a boolean value");
    return b;
}
double fa_date(Ctx *c, Expr *call, Val *argv, int i) {
    double d;
    if (!v_todate(argv[i], &d)) fn_param_error(c, call, i, argv[i], "must be a date/time value");
    return d;
}
Array *fa_arr(Ctx *c, Expr *call, Val *argv, int i) {
    if (argv[i].t != VT_ARRAY) fn_param_error(c, call, i, argv[i], "must be an array");
    return argv[i].u.a;
}
Struct *fa_struct(Ctx *c, Expr *call, Val *argv, int i) {
    if (argv[i].t != VT_STRUCT) fn_param_error(c, call, i, argv[i], "must be a structure");
    return argv[i].u.st;
}
Query *fa_query(Ctx *c, Expr *call, Val *argv, int i) {
    if (argv[i].t != VT_QUERY) fn_param_error(c, call, i, argv[i], "must be a query");
    return argv[i].u.q;
}
size_t fa_len(Val v) { return v.t == VT_STR || v.t == VT_BINARY ? v.u.str.len : strlen(v_tostr(v)); }

/* ================================================================ lists */
static int is_delim(char ch, const char *delims) { return ch && strchr(delims, ch) != NULL; }

Array *list_to_array_k(const char *list, const char *delims) {
    Array *a = array_new();
    if (!delims || !*delims) delims = ",";
    const char *p = list;
    while (*p) {
        while (*p && is_delim(*p, delims)) p++;
        if (!*p) break;
        const char *s = p;
        while (*p && !is_delim(*p, delims)) p++;
        array_push(a, v_strn(kstrndup(s, p - s), p - s));
    }
    return a;
}
int list_len(const char *list, const char *delims) { return list_to_array_k(list, delims)->n; }
char *list_get_at(const char *list, int idx, const char *delims) {
    Array *a = list_to_array_k(list, delims);
    if (idx < 1 || idx > a->n) return NULL;
    return (char *)v_tostr(a->v[idx - 1]);
}
static char first_delim(const char *d) { return d && *d ? d[0] : ','; }
static char *join(Array *a, char delim) {
    Buf b; buf_init(&b);
    for (int i = 0; i < a->n; i++) { if (i) buf_putc(&b, delim); buf_puts(&b, v_tostr(a->v[i])); }
    return buf_cstr(&b);
}
/* rebuild a list replacing element idx (0-based) keeping original delimiters */
typedef struct { const char *s; int len; int start; } LTok;
static int list_tokens(const char *list, const char *delims, LTok *out, int max) {
    int n = 0; const char *p = list;
    while (*p) {
        while (*p && is_delim(*p, delims)) p++;
        if (!*p) break;
        const char *s = p;
        while (*p && !is_delim(*p, delims)) p++;
        if (n < max) { out[n].s = s; out[n].len = (int)(p - s); out[n].start = (int)(s - list); }
        n++;
    }
    return n;
}

static const char *D(int argc, Val *argv, int i, const char *def) { return argc > i ? v_tostr(argv[i]) : def; }

F(listlen) { return v_num(list_len(fa_str(c, call, argv, 0), D(argc, argv, 1, ","))); }
F(listgetat) {
    const char *l = fa_str(c, call, argv, 0);
    int i = fa_int(c, call, argv, 1);
    const char *d = D(argc, argv, 2, ",");
    char *r = list_get_at(l, i, d);
    if (!r) kf_throw_at(c, call, "Expression", kprintf("Invalid list index %d.", i),
                        kprintf("In function ListGetAt(list, index [, delimiters]) the value of index, %d, is not a valid index for the list "
                                "given as the first argument (this list has %d elements). Valid indexes are in the range 1 through %d.",
                                i, list_len(l, d), list_len(l, d)));
    return v_str(r);
}
F(listfirst) { Array *a = list_to_array_k(fa_str(c, call, argv, 0), D(argc, argv, 1, ",")); return a->n ? a->v[0] : v_str(""); }
F(listlast) { Array *a = list_to_array_k(fa_str(c, call, argv, 0), D(argc, argv, 1, ",")); return a->n ? a->v[a->n - 1] : v_str(""); }
F(listrest) {
    const char *l = fa_str(c, call, argv, 0), *d = D(argc, argv, 1, ",");
    while (*l && is_delim(*l, d)) l++;
    while (*l && !is_delim(*l, d)) l++;
    while (*l && is_delim(*l, d)) l++;
    return v_strdup(l);
}
F(listappend) {
    const char *l = fa_str(c, call, argv, 0), *v = fa_str(c, call, argv, 1), *d = D(argc, argv, 2, ",");
    if (!*l) return v_strdup(v);
    return v_str(kprintf("%s%c%s", l, first_delim(d), v));
}
F(listprepend) {
    const char *l = fa_str(c, call, argv, 0), *v = fa_str(c, call, argv, 1), *d = D(argc, argv, 2, ",");
    if (!*l) return v_strdup(v);
    return v_str(kprintf("%s%c%s", v, first_delim(d), l));
}
static Val list_modify(Ctx *c, Expr *call, Val *argv, int argc, int mode) {
    /* mode 0 = set, 1 = insert, 2 = delete */
    const char *l = fa_str(c, call, argv, 0);
    int idx = fa_int(c, call, argv, 1);
    const char *v = mode == 2 ? "" : fa_str(c, call, argv, 2);
    const char *d = D(argc, argv, mode == 2 ? 2 : 3, ",");
    int cnt = list_len(l, d);
    LTok *t = kmalloc(sizeof(LTok) * (cnt + 1));
    list_tokens(l, d, t, cnt);
    if (idx < 1 || idx > cnt)
        kf_throw_at(c, call, "Expression", kprintf("Invalid list index %d.", idx),
                    kprintf("In function %s, the value of index, %d, is not valid. The list has %d elements.", fn_name(call), idx, cnt));
    Buf b; buf_init(&b);
    LTok *k = &t[idx - 1];
    if (mode == 0) { buf_put(&b, l, k->start); buf_puts(&b, v); buf_puts(&b, l + k->start + k->len); }
    else if (mode == 1) { buf_put(&b, l, k->start); buf_puts(&b, v); buf_putc(&b, first_delim(d)); buf_puts(&b, l + k->start); }
    else {
        /* remove element and one adjacent delimiter */
        int s = k->start, e = k->start + k->len;
        if (idx < cnt) e = t[idx].start;
        else if (idx > 1) s = t[idx - 2].start + t[idx - 2].len;
        buf_put(&b, l, s); buf_puts(&b, l + e);
    }
    return v_str(buf_cstr(&b));
}
F(listsetat) { return list_modify(c, call, argv, argc, 0); }
F(listinsertat) { return list_modify(c, call, argv, argc, 1); }
F(listdeleteat) { return list_modify(c, call, argv, argc, 2); }
static Val list_find(Ctx *c, Expr *call, Val *argv, int argc, int nocase, int contains) {
    Array *a = list_to_array_k(fa_str(c, call, argv, 0), D(argc, argv, 2, ","));
    const char *v = fa_str(c, call, argv, 1);
    for (int i = 0; i < a->n; i++) {
        const char *e = v_tostr(a->v[i]);
        int m = contains ? (nocase ? kf_stristr(e, v) != NULL : strstr(e, v) != NULL)
                         : (nocase ? !kf_stricmp(e, v) : !strcmp(e, v));
        if (m) return v_num(i + 1);
    }
    return v_num(0);
}
F(listfind) { return list_find(c, call, argv, argc, 0, 0); }
F(listfindnocase) { return list_find(c, call, argv, argc, 1, 0); }
F(listcontains) { return list_find(c, call, argv, argc, 0, 1); }
F(listcontainsnocase) { return list_find(c, call, argv, argc, 1, 1); }
F(listchangedelims) {
    Array *a = list_to_array_k(fa_str(c, call, argv, 0), D(argc, argv, 2, ","));
    const char *nd = fa_str(c, call, argv, 1);
    Buf b; buf_init(&b);
    for (int i = 0; i < a->n; i++) { if (i) buf_puts(&b, nd); buf_puts(&b, v_tostr(a->v[i])); }
    return v_str(buf_cstr(&b));
}
F(listtoarray) { return v_arr(list_to_array_k(fa_str(c, call, argv, 0), D(argc, argv, 1, ","))); }
F(arraytolist) {
    Array *a = fa_arr(c, call, argv, 0);
    const char *d = D(argc, argv, 1, ",");
    Buf b; buf_init(&b);
    for (int i = 0; i < a->n; i++) { if (i) buf_puts(&b, d); buf_puts(&b, val_simple_str(c, a->v[i], call)); }
    return v_str(buf_cstr(&b));
}
static Val list_value_count(Ctx *c, Expr *call, Val *argv, int argc, int nocase) {
    Array *a = list_to_array_k(fa_str(c, call, argv, 0), D(argc, argv, 2, ","));
    const char *v = fa_str(c, call, argv, 1);
    int n = 0;
    for (int i = 0; i < a->n; i++) if (nocase ? !kf_stricmp(v_tostr(a->v[i]), v) : !strcmp(v_tostr(a->v[i]), v)) n++;
    return v_num(n);
}
F(listvaluecount) { return list_value_count(c, call, argv, argc, 0); }
F(listvaluecountnocase) { return list_value_count(c, call, argv, argc, 1); }
F(listqualify) {
    const char *l = fa_str(c, call, argv, 0), *q = fa_str(c, call, argv, 1), *d = D(argc, argv, 2, ",");
    const char *elems = D(argc, argv, 3, "ALL");
    Array *a = list_to_array_k(l, d);
    Buf b; buf_init(&b);
    for (int i = 0; i < a->n; i++) {
        if (i) buf_putc(&b, first_delim(d));
        const char *e = v_tostr(a->v[i]);
        int qualify = kf_stricmp(elems, "CHAR") || !v_isnumeric_str(e, NULL);
        if (qualify) buf_puts(&b, q);
        buf_puts(&b, e);
        if (qualify) buf_puts(&b, q);
    }
    return v_str(buf_cstr(&b));
}
static const char *g_sorttype; static int g_sortdesc;
static int cmp_sort(const void *pa, const void *pb) {
    const Val *a = pa, *b = pb;
    int r;
    if (!kf_stricmp(g_sorttype, "numeric")) {
        double x = 0, y = 0; v_tonum(*a, &x); v_tonum(*b, &y);
        r = x < y ? -1 : x > y;
    } else if (!kf_stricmp(g_sorttype, "textnocase")) r = kf_stricmp(v_tostr(*a), v_tostr(*b));
    else r = strcmp(v_tostr(*a), v_tostr(*b));
    return g_sortdesc ? -r : r;
}
static void sort_vals(Ctx *c, Expr *call, Val *v, int n, const char *type, const char *order) {
    if (kf_stricmp(type, "numeric") && kf_stricmp(type, "text") && kf_stricmp(type, "textnocase"))
        kf_throw_at(c, call, "Expression", kprintf("Invalid sort type %s.", kf_html_escape(type)),
                    "The sort type must be one of numeric, text or textnocase.");
    if (!kf_stricmp(type, "numeric"))
        for (int i = 0; i < n; i++) { double d; if (!v_tonum(v[i], &d)) kf_throw_at(c, call, "Expression",
            "Non-numeric value found in numeric sort.", kprintf("The value \"%s\" is not numeric.", argdesc(v[i]))); }
    g_sorttype = type; g_sortdesc = !kf_stricmp(order, "desc");
    static pthread_mutex_t mu = PTHREAD_MUTEX_INITIALIZER;
    pthread_mutex_lock(&mu);
    g_sorttype = type; g_sortdesc = !kf_stricmp(order, "desc");
    qsort(v, n, sizeof(Val), cmp_sort);
    pthread_mutex_unlock(&mu);
}
F(listsort) {
    const char *d = D(argc, argv, 3, ",");
    Array *a = list_to_array_k(fa_str(c, call, argv, 0), d);
    sort_vals(c, call, a->v, a->n, fa_str(c, call, argv, 1), D(argc, argv, 2, "asc"));
    return v_str(join(a, first_delim(d)));
}
F(arraysort) {
    Array *a = fa_arr(c, call, argv, 0);
    sort_vals(c, call, a->v, a->n, fa_str(c, call, argv, 1), D(argc, argv, 2, "asc"));
    return v_bool(1);
}

/* ================================================================ strings */
F(len) {
    if (argv[0].t == VT_BINARY) return v_num((double)argv[0].u.str.len);
    fa_str(c, call, argv, 0);
    return v_num((double)fa_len(argv[0]));
}
F(left) {
    const char *s = fa_str(c, call, argv, 0); int n = fa_int(c, call, argv, 1);
    if (n < 0) fn_param_error(c, call, 1, argv[1], "must be a non-negative integer");
    size_t l = fa_len(argv[0]);
    return v_strn(kstrndup(s, (size_t)n < l ? (size_t)n : l), (size_t)n < l ? (size_t)n : l);
}
F(right) {
    const char *s = fa_str(c, call, argv, 0); int n = fa_int(c, call, argv, 1);
    if (n < 0) fn_param_error(c, call, 1, argv[1], "must be a non-negative integer");
    size_t l = fa_len(argv[0]);
    if ((size_t)n >= l) return v_strdup(s);
    return v_strdup(s + l - n);
}
F(mid) {
    const char *s = fa_str(c, call, argv, 0); int st = fa_int(c, call, argv, 1), n = fa_int(c, call, argv, 2);
    if (st < 1) fn_param_error(c, call, 1, argv[1], "must be a positive integer");
    if (n < 0) fn_param_error(c, call, 2, argv[2], "must be a non-negative integer");
    size_t l = fa_len(argv[0]);
    if ((size_t)st > l) return v_str("");
    size_t take = l - (st - 1);
    if ((size_t)n < take) take = n;
    return v_strn(kstrndup(s + st - 1, take), take);
}
F(ucase) { (void)argc; return v_str(kf_upper(fa_str(c, call, argv, 0))); }
F(lcase) { (void)argc; return v_str(kf_lower(fa_str(c, call, argv, 0))); }
F(trim) { return v_str(kf_trim(fa_str(c, call, argv, 0))); }
F(ltrim) { const char *s = fa_str(c, call, argv, 0); while (*s && isspace((unsigned char)*s)) s++; return v_strdup(s); }
F(rtrim) {
    const char *s = fa_str(c, call, argv, 0); size_t n = strlen(s);
    while (n && isspace((unsigned char)s[n - 1])) n--;
    return v_strn(kstrndup(s, n), n);
}
static Val do_find(Ctx *c, Expr *call, Val *argv, int argc, int nocase) {
    const char *sub = fa_str(c, call, argv, 0), *s = fa_str(c, call, argv, 1);
    int start = argc > 2 ? fa_int(c, call, argv, 2) : 1;
    size_t l = strlen(s);
    if (start < 1) start = 1;
    if ((size_t)start > l) return v_num(0);
    if (!*sub) return v_num(0);
    const char *p = nocase ? kf_stristr(s + start - 1, sub) : strstr(s + start - 1, sub);
    return v_num(p ? (double)(p - s + 1) : 0);
}
F(find) { return do_find(c, call, argv, argc, 0); }
F(findnocase) { return do_find(c, call, argv, argc, 1); }
F(findoneof) {
    const char *set = fa_str(c, call, argv, 0), *s = fa_str(c, call, argv, 1);
    int start = argc > 2 ? fa_int(c, call, argv, 2) : 1;
    for (size_t i = start > 0 ? start - 1 : 0; s[i]; i++) if (strchr(set, s[i])) return v_num((double)i + 1);
    return v_num(0);
}
static char *replace_str(const char *s, const char *from, const char *to, int all, int nocase) {
    if (!*from) return kstrdup(s);
    Buf b; buf_init(&b);
    size_t fl = strlen(from);
    const char *p = s;
    for (;;) {
        const char *m = nocase ? kf_stristr(p, from) : strstr(p, from);
        if (!m) break;
        buf_put(&b, p, m - p);
        buf_puts(&b, to);
        p = m + fl;
        if (!all) break;
    }
    buf_puts(&b, p);
    return buf_cstr(&b);
}
F(replace) {
    const char *scope = D(argc, argv, 3, "ONE");
    return v_str(replace_str(fa_str(c, call, argv, 0), fa_str(c, call, argv, 1), fa_str(c, call, argv, 2), !kf_stricmp(scope, "all"), 0));
}
F(replacenocase) {
    const char *scope = D(argc, argv, 3, "ONE");
    return v_str(replace_str(fa_str(c, call, argv, 0), fa_str(c, call, argv, 1), fa_str(c, call, argv, 2), !kf_stricmp(scope, "all"), 1));
}
F(replacelist) {
    const char *s = fa_str(c, call, argv, 0);
    Array *from = list_to_array_k(fa_str(c, call, argv, 1), ",");
    Array *to = list_to_array_k(fa_str(c, call, argv, 2), ",");
    char *r = kstrdup(s);
    for (int i = 0; i < from->n; i++)
        r = replace_str(r, v_tostr(from->v[i]), i < to->n ? v_tostr(to->v[i]) : "", 1, 0);
    return v_str(r);
}
F(removechars) {
    const char *s = fa_str(c, call, argv, 0); int st = fa_int(c, call, argv, 1), n = fa_int(c, call, argv, 2);
    size_t l = strlen(s);
    if (st < 1 || (size_t)st > l) fn_param_error(c, call, 1, argv[1], "must be a valid position within the string");
    Buf b; buf_init(&b);
    buf_put(&b, s, st - 1);
    if ((size_t)(st - 1 + n) < l) buf_puts(&b, s + st - 1 + n);
    return v_str(buf_cstr(&b));
}
F(repeatstring) {
    const char *s = fa_str(c, call, argv, 0); int n = fa_int(c, call, argv, 1);
    Buf b; buf_init(&b);
    for (int i = 0; i < n; i++) buf_puts(&b, s);
    return v_str(buf_cstr(&b));
}
F(reverse) {
    const char *s = fa_str(c, call, argv, 0); size_t l = strlen(s);
    char *r = kmalloc(l + 1);
    for (size_t i = 0; i < l; i++) r[i] = s[l - 1 - i];
    return v_strn(r, l);
}
F(spanincluding) {
    const char *s = fa_str(c, call, argv, 0), *set = fa_str(c, call, argv, 1);
    size_t n = strspn(s, set);
    return v_strn(kstrndup(s, n), n);
}
F(spanexcluding) {
    const char *s = fa_str(c, call, argv, 0), *set = fa_str(c, call, argv, 1);
    size_t n = strcspn(s, set);
    return v_strn(kstrndup(s, n), n);
}
F(gettoken) {
    char *r = list_get_at(fa_str(c, call, argv, 0), fa_int(c, call, argv, 1), D(argc, argv, 2, " \t\n\r"));
    return v_str(r ? r : "");
}
F(asc) { const char *s = fa_str(c, call, argv, 0); return v_num((unsigned char)s[0]); }
F(chr) { int n = fa_int(c, call, argv, 0); char *r = kmalloc(2); r[0] = (char)n; return v_strn(r, n ? 1 : 0); }
F(val) {
    const char *s = fa_str(c, call, argv, 0);
    while (isspace((unsigned char)*s)) s++;
    const char *p = s;
    if (*p == '+' || *p == '-') p++;
    const char *digits = p;
    while (isdigit((unsigned char)*p)) p++;
    if (*p == '.') { p++; while (isdigit((unsigned char)*p)) p++; }
    if (p == digits || (p == digits + 1 && *digits == '.')) return v_num(0);
    return v_num(atof(kstrndup(s, p - s)));
}
F(compare) { int r = strcmp(fa_str(c, call, argv, 0), fa_str(c, call, argv, 1)); return v_num(r < 0 ? -1 : r > 0); }
F(comparenocase) { int r = kf_stricmp(fa_str(c, call, argv, 0), fa_str(c, call, argv, 1)); return v_num(r < 0 ? -1 : r > 0); }
F(stripcr) {
    const char *s = fa_str(c, call, argv, 0);
    Buf b; buf_init(&b);
    for (; *s; s++) if (*s != '\r') buf_putc(&b, *s);
    return v_str(buf_cstr(&b));
}
F(insert) {
    const char *sub = fa_str(c, call, argv, 0), *s = fa_str(c, call, argv, 1);
    int pos = fa_int(c, call, argv, 2);
    size_t l = strlen(s);
    if (pos < 0 || (size_t)pos > l) fn_param_error(c, call, 2, argv[2], "must be a valid position within the string");
    return v_str(kprintf("%.*s%s%s", pos, s, sub, s + pos));
}
static Val justify(Ctx *c, Expr *call, Val *argv, int mode) {
    const char *s = fa_str(c, call, argv, 0); int w = fa_int(c, call, argv, 1);
    int l = (int)strlen(s);
    if (l >= w) return v_strdup(s);
    int pad = w - l, lp = mode == 0 ? 0 : mode == 2 ? pad : pad / 2;
    Buf b; buf_init(&b);
    for (int i = 0; i < lp; i++) buf_putc(&b, ' ');
    buf_puts(&b, s);
    for (int i = 0; i < pad - lp; i++) buf_putc(&b, ' ');
    return v_str(buf_cstr(&b));
}
F(ljustify) { return justify(c, call, argv, 0); }
F(cjustify) { return justify(c, call, argv, 1); }
F(rjustify) { return justify(c, call, argv, 2); }
F(paragraphformat) {
    const char *s = fa_str(c, call, argv, 0);
    Buf b; buf_init(&b);
    for (const char *p = s; *p; p++) {
        if (*p == '\r') continue;
        if (*p == '\n') {
            const char *q = p + 1;
            while (*q == '\r') q++;
            if (*q == '\n') { buf_puts(&b, "\n<P>\n"); p = q; continue; }
            buf_putc(&b, ' ');
            continue;
        }
        buf_putc(&b, *p);
    }
    return v_str(buf_cstr(&b));
}
F(wrap) {
    const char *s = fa_str(c, call, argv, 0); int w = fa_int(c, call, argv, 1);
    Buf b; buf_init(&b);
    int col = 0;
    const char *p = s;
    while (*p) {
        const char *ws = p; while (*p && !isspace((unsigned char)*p)) p++;
        int wl = (int)(p - ws);
        if (col && col + 1 + wl > w) { buf_putc(&b, '\n'); col = 0; }
        else if (col) { buf_putc(&b, ' '); col++; }
        while (w > 0 && wl > w) { buf_put(&b, ws, w); buf_putc(&b, '\n'); ws += w; wl -= w; }
        buf_put(&b, ws, wl); col += wl;
        while (*p && isspace((unsigned char)*p)) { if (*p == '\n') { buf_putc(&b, '\n'); col = 0; } p++; }
    }
    return v_str(buf_cstr(&b));
}
char *kf_htmleditformat(const char *s) {
    Buf b; buf_init(&b);
    for (; *s; s++) {
        switch (*s) {
        case '<': buf_puts(&b, "&lt;"); break;
        case '>': buf_puts(&b, "&gt;"); break;
        case '&': buf_puts(&b, "&amp;"); break;
        case '"': buf_puts(&b, "&quot;"); break;
        case '\r': break;
        default: buf_putc(&b, *s);
        }
    }
    return buf_cstr(&b);
}
F(htmleditformat) { return v_str(kf_htmleditformat(fa_str(c, call, argv, 0))); }
F(htmlcodeformat) { return v_str(kprintf("<PRE>%s</PRE>", kf_htmleditformat(fa_str(c, call, argv, 0)))); }
char *kf_urlencode(const char *s) {
    Buf b; buf_init(&b);
    for (; *s; s++) {
        unsigned char ch = (unsigned char)*s;
        if (isalnum(ch)) buf_putc(&b, (char)ch);
        else buf_printf(&b, "%%%02X", ch);
    }
    return buf_cstr(&b);
}
char *kf_urldecode(const char *s, size_t n) {
    Buf b; buf_init(&b);
    for (size_t i = 0; i < n; i++) {
        if (s[i] == '+') buf_putc(&b, ' ');
        else if (s[i] == '%' && i + 2 < n + 0 && isxdigit((unsigned char)s[i + 1]) && isxdigit((unsigned char)s[i + 2])) {
            char hex[3] = {s[i + 1], s[i + 2], 0};
            buf_putc(&b, (char)strtol(hex, NULL, 16));
            i += 2;
        } else buf_putc(&b, s[i]);
    }
    return buf_cstr(&b);
}
F(urlencodedformat) { return v_str(kf_urlencode(fa_str(c, call, argv, 0))); }
F(urldecode) { const char *s = fa_str(c, call, argv, 0); return v_str(kf_urldecode(s, strlen(s))); }
F(jsstringformat) {
    const char *s = fa_str(c, call, argv, 0);
    Buf b; buf_init(&b);
    for (; *s; s++) {
        switch (*s) {
        case '"': buf_puts(&b, "\\\""); break;
        case '\'': buf_puts(&b, "\\'"); break;
        case '\\': buf_puts(&b, "\\\\"); break;
        case '\n': buf_puts(&b, "\\n"); break;
        case '\r': buf_puts(&b, "\\r"); break;
        case '\t': buf_puts(&b, "\\t"); break;
        default: buf_putc(&b, *s);
        }
    }
    return v_str(buf_cstr(&b));
}
F(xmlformat) {
    const char *s = fa_str(c, call, argv, 0);
    Buf b; buf_init(&b);
    for (; *s; s++) {
        switch (*s) {
        case '<': buf_puts(&b, "&lt;"); break;
        case '>': buf_puts(&b, "&gt;"); break;
        case '&': buf_puts(&b, "&amp;"); break;
        case '"': buf_puts(&b, "&quot;"); break;
        case '\'': buf_puts(&b, "&apos;"); break;
        default: buf_putc(&b, *s);
        }
    }
    return v_str(buf_cstr(&b));
}
F(hash) { fa_str(c, call, argv, 0); return v_str(md5_hex_upper(v_tostr(argv[0]), fa_len(argv[0]))); }
F(encrypt) {
    const char *s = fa_str(c, call, argv, 0);
    return v_str(cfmx_compat_encrypt(s, fa_len(argv[0]), fa_str(c, call, argv, 1)));
}
F(decrypt) {
    size_t n;
    char *r = cfmx_compat_decrypt(fa_str(c, call, argv, 0), fa_str(c, call, argv, 1), &n);
    return v_strn(r, n);
}
F(tobase64) {
    if (argv[0].t == VT_BINARY) return v_str(base64_encode((const unsigned char *)argv[0].u.str.s, argv[0].u.str.len));
    const char *s = fa_str(c, call, argv, 0);
    return v_str(base64_encode((const unsigned char *)s, fa_len(argv[0])));
}
F(tobinary) {
    if (argv[0].t == VT_BINARY) return argv[0];
    size_t n;
    unsigned char *p = base64_decode(fa_str(c, call, argv, 0), &n);
    return v_binary((const char *)p, n);
}
F(tostring) {
    if (argv[0].t == VT_BINARY) return v_strn(kstrndup(argv[0].u.str.s, argv[0].u.str.len), argv[0].u.str.len);
    return v_strdup(fa_str(c, call, argv, 0));
}

/* ================================================================ regex */
static regex_t *re_compile(Ctx *c, Expr *call, const char *pat, int nocase) {
    regex_t *re = kmalloc(sizeof(regex_t));
    /* CF regular expressions are POSIX-flavoured; translate a few Perl-isms
     * people typed anyway (\d \w \s) into POSIX classes */
    Buf b; buf_init(&b);
    for (const char *p = pat; *p; p++) {
        if (*p == '\\' && p[1]) {
            switch (p[1]) {
            case 'd': buf_puts(&b, "[0-9]"); p++; continue;
            case 'D': buf_puts(&b, "[^0-9]"); p++; continue;
            case 'w': buf_puts(&b, "[A-Za-z0-9_]"); p++; continue;
            case 'W': buf_puts(&b, "[^A-Za-z0-9_]"); p++; continue;
            case 's': buf_puts(&b, "[[:space:]]"); p++; continue;
            case 'S': buf_puts(&b, "[^[:space:]]"); p++; continue;
            }
        }
        buf_putc(&b, *p);
    }
    int rc = regcomp(re, buf_cstr(&b), REG_EXTENDED | (nocase ? REG_ICASE : 0));
    if (rc) {
        char eb[256]; regerror(rc, re, eb, sizeof eb);
        kf_throw_at(c, call, "Expression", kprintf("Bad regular expression \"%s\".", kf_html_escape(pat)), eb);
    }
    return re;
}
static Val re_find(Ctx *c, Expr *call, Val *argv, int argc, int nocase) {
    regex_t *re = re_compile(c, call, fa_str(c, call, argv, 0), nocase);
    const char *s = fa_str(c, call, argv, 1);
    int start = argc > 2 ? fa_int(c, call, argv, 2) : 1;
    int subex = argc > 3 ? fa_bool(c, call, argv, 3) : 0;
    size_t l = strlen(s);
    regmatch_t m[10];
    int found = start >= 1 && (size_t)(start - 1) <= l && regexec(re, s + start - 1, 10, m, start > 1 ? REG_NOTBOL : 0) == 0;
    size_t re_nsub_last = re->re_nsub;
    regfree(re);
    if (!subex) return v_num(found ? (double)(m[0].rm_so + start) : 0);
    Struct *r = struct_new();
    Array *pos = array_new(), *len = array_new();
    if (found) {
        size_t nsub = re_nsub_last + 1;
        for (size_t i = 0; i < nsub && i < 10; i++) {
            if (m[i].rm_so < 0) { array_push(pos, v_num(0)); array_push(len, v_num(0)); continue; }
            array_push(pos, v_num((double)(m[i].rm_so + start)));
            array_push(len, v_num((double)(m[i].rm_eo - m[i].rm_so)));
        }
    } else { array_push(pos, v_num(0)); array_push(len, v_num(0)); }
    struct_set(r, "pos", v_arr(pos));
    struct_set(r, "len", v_arr(len));
    return v_struct(r);
}
F(refind) { return re_find(c, call, argv, argc, 0); }
F(refindnocase) { return re_find(c, call, argv, argc, 1); }
static Val re_replace(Ctx *c, Expr *call, Val *argv, int argc, int nocase) {
    const char *s = fa_str(c, call, argv, 0);
    regex_t *re = re_compile(c, call, fa_str(c, call, argv, 1), nocase);
    const char *rep = fa_str(c, call, argv, 2);
    int all = argc > 3 && !kf_stricmp(v_tostr(argv[3]), "all");
    Buf b; buf_init(&b);
    const char *p = s;
    regmatch_t m[10];
    int flags = 0;
    while (*p || p == s) {
        if (regexec(re, p, 10, m, flags) != 0) break;
        buf_put(&b, p, m[0].rm_so);
        for (const char *r = rep; *r; r++) {
            if (*r == '\\' && isdigit((unsigned char)r[1])) {
                int k = r[1] - '0';
                if (m[k].rm_so >= 0) buf_put(&b, p + m[k].rm_so, m[k].rm_eo - m[k].rm_so);
                r++;
            } else buf_putc(&b, *r);
        }
        if (m[0].rm_eo == m[0].rm_so) {
            if (!p[m[0].rm_eo]) { p += m[0].rm_eo; break; }
            buf_putc(&b, p[m[0].rm_eo]);
            p += m[0].rm_eo + 1;
        } else p += m[0].rm_eo;
        flags = REG_NOTBOL;
        if (!all) break;
    }
    buf_puts(&b, p);
    regfree(re);
    return v_str(buf_cstr(&b));
}
F(rereplace) { return re_replace(c, call, argv, argc, 0); }
F(rereplacenocase) { return re_replace(c, call, argv, argc, 1); }

/* ================================================================ formatting */
static const char *MONTHN[] = {"January","February","March","April","May","June","July","August",
                               "September","October","November","December"};
static const char *DAYN[] = {"Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"};

char *kf_dateformat(double dt, const char *mask) {
    if (!mask || !*mask) mask = "dd-mmm-yy";
    if (!kf_stricmp(mask, "short")) mask = "m/d/yy";
    else if (!kf_stricmp(mask, "medium")) mask = "mmm d, yyyy";
    else if (!kf_stricmp(mask, "long")) mask = "mmmm d, yyyy";
    else if (!kf_stricmp(mask, "full")) mask = "dddd, mmmm d, yyyy";
    int y, mo, d, h, mi, s;
    date_to_parts(dt, &y, &mo, &d, &h, &mi, &s);
    int dow = date_dow(dt);
    Buf b; buf_init(&b);
    for (const char *p = mask; *p; ) {
        char ch = (char)tolower((unsigned char)*p);
        int n = 0;
        while (tolower((unsigned char)p[n]) == ch && (ch == 'd' || ch == 'm' || ch == 'y' || ch == 'g')) n++;
        if (ch == 'd' && n) {
            if (n == 1) buf_printf(&b, "%d", d);
            else if (n == 2) buf_printf(&b, "%02d", d);
            else if (n == 3) buf_printf(&b, "%.3s", DAYN[dow - 1]);
            else buf_puts(&b, DAYN[dow - 1]);
            p += n;
        } else if (ch == 'm' && n) {
            if (n == 1) buf_printf(&b, "%d", mo);
            else if (n == 2) buf_printf(&b, "%02d", mo);
            else if (n == 3) buf_printf(&b, "%.3s", MONTHN[mo - 1]);
            else buf_puts(&b, MONTHN[mo - 1]);
            p += n;
        } else if (ch == 'y' && n) {
            if (n <= 2) buf_printf(&b, "%02d", y % 100);
            else buf_printf(&b, "%d", y);
            p += n;
        } else if (ch == 'g' && n) {
            buf_puts(&b, "AD");
            p += n;
        } else buf_putc(&b, *p++);
    }
    return buf_cstr(&b);
}

char *kf_timeformat(double dt, const char *mask) {
    if (!mask || !*mask) mask = "hh:mm tt";
    if (!kf_stricmp(mask, "short")) mask = "h:mm tt";
    else if (!kf_stricmp(mask, "medium")) mask = "h:mm:ss tt";
    else if (!kf_stricmp(mask, "long") || !kf_stricmp(mask, "full")) mask = "h:mm:ss tt";
    int y, mo, d, h, mi, s;
    date_to_parts(dt, &y, &mo, &d, &h, &mi, &s);
    int h12 = h % 12 == 0 ? 12 : h % 12;
    Buf b; buf_init(&b);
    for (const char *p = mask; *p; ) {
        char ch = *p;
        int n = 0;
        while (p[n] == ch) n++;
        if (ch == 'h') { buf_printf(&b, n >= 2 ? "%02d" : "%d", h12); p += n; }
        else if (ch == 'H') { buf_printf(&b, n >= 2 ? "%02d" : "%d", h); p += n; }
        else if (ch == 'm' || ch == 'M') { buf_printf(&b, n >= 2 ? "%02d" : "%d", mi); p += n; }
        else if (ch == 's' || ch == 'S') { buf_printf(&b, n >= 2 ? "%02d" : "%d", s); p += n; }
        else if (ch == 't' || ch == 'T') {
            const char *ap = h < 12 ? "AM" : "PM";
            if (n == 1) buf_putc(&b, ap[0]); else buf_puts(&b, ap);
            p += n;
        } else buf_putc(&b, *p++);
    }
    return buf_cstr(&b);
}

static char *commas(const char *digits) {
    size_t l = strlen(digits);
    Buf b; buf_init(&b);
    for (size_t i = 0; i < l; i++) {
        buf_putc(&b, digits[i]);
        if ((l - i - 1) % 3 == 0 && i + 1 < l) buf_putc(&b, ',');
    }
    return buf_cstr(&b);
}

char *kf_numberformat(double n, const char *mask) {
    if (!mask || !*mask) {
        char tmp[64]; snprintf(tmp, sizeof tmp, "%.0f", fabs(round(n)));
        return kprintf("%s%s", n < 0 && round(n) != 0 ? "-" : "", commas(tmp));
    }
    int has_comma = strchr(mask, ',') != NULL, has_dollar = strchr(mask, '$') != NULL;
    int paren = strchr(mask, '(') != NULL, plus = strchr(mask, '+') != NULL, minus = strchr(mask, '-') != NULL;
    int left = strchr(mask, 'L') != NULL, center = strchr(mask, 'C') != NULL;
    const char *dot = strchr(mask, '.');
    int intplaces = 0, decplaces = 0, zeropad = 0;
    for (const char *p = mask; *p && (!dot || p < dot); p++) {
        if (*p == '9' || *p == '_') intplaces++;
        if (*p == '0') { intplaces++; zeropad++; }
    }
    if (dot) for (const char *p = dot + 1; *p; p++) if (*p == '9' || *p == '0' || *p == '_') decplaces++;
    double a = fabs(n);
    char tmp[128];
    snprintf(tmp, sizeof tmp, "%.*f", decplaces, a);
    char *ip = kstrdup(tmp), *dp = strchr(ip, '.');
    if (dp) *dp++ = 0;
    while ((int)strlen(ip) < zeropad) ip = kprintf("0%s", ip);
    Buf b; buf_init(&b);
    int neg = n < 0 && atof(tmp) != 0;
    if (neg) buf_puts(&b, paren ? "(" : "-");
    else if (plus) buf_putc(&b, '+');
    else if (minus || paren) buf_putc(&b, ' ');
    if (has_dollar) buf_putc(&b, '$');
    buf_puts(&b, has_comma ? commas(ip) : ip);
    if (dp && decplaces) buf_printf(&b, ".%s", dp);
    if (neg && paren) buf_putc(&b, ')');
    else if (paren) buf_putc(&b, ' ');
    char *r = buf_cstr(&b);
    /* pad to mask width (right justified unless L / C) */
    int width = (int)strlen(mask) - (strchr(mask, 'L') ? 1 : 0) - (strchr(mask, 'C') ? 1 : 0) - (strchr(mask, '^') ? 1 : 0);
    int rl = (int)strlen(r);
    if (rl < width && (intplaces > (int)strlen(ip) || left || center)) {
        int pad = width - rl;
        if (left) return kprintf("%s%*s", r, pad, "");
        if (center) return kprintf("%*s%s%*s", pad / 2, "", r, pad - pad / 2, "");
        return kprintf("%*s%s", pad, "", r);
    }
    return r;
}

char *kf_dollarformat(double n) {
    char tmp[64];
    snprintf(tmp, sizeof tmp, "%.2f", fabs(n));
    char *ip = kstrdup(tmp), *dp = strchr(ip, '.');
    *dp++ = 0;
    if (n < 0 && atof(tmp) != 0) return kprintf("($%s.%s)", commas(ip), dp);
    return kprintf("$%s.%s", commas(ip), dp);
}

F(dateformat) {
    double d = fa_date(c, call, argv, 0);
    return v_str(kf_dateformat(d, argc > 1 ? fa_str(c, call, argv, 1) : NULL));
}
F(timeformat) {
    double d = fa_date(c, call, argv, 0);
    return v_str(kf_timeformat(d, argc > 1 ? fa_str(c, call, argv, 1) : NULL));
}
F(numberformat) {
    const char *s = fa_str(c, call, argv, 0);
    double d = 0;
    if (*s && !v_tonum(argv[0], &d)) fn_param_error(c, call, 0, argv[0], "must be a number");
    return v_str(kf_numberformat(d, argc > 1 ? fa_str(c, call, argv, 1) : NULL));
}
F(decimalformat) {
    double d = fa_num(c, call, argv, 0);
    return v_str(kf_numberformat(d, ",.00"));
}
F(dollarformat) {
    const char *s = fa_str(c, call, argv, 0);
    double d = 0;
    if (*s && !v_tonum(argv[0], &d)) fn_param_error(c, call, 0, argv[0], "must be a number");
    return v_str(kf_dollarformat(d));
}
F(lscurrencyformat) {
    double d = fa_num(c, call, argv, 0);
    const char *type = D(argc, argv, 1, "local");
    if (!kf_stricmp(type, "none")) return v_str(kf_numberformat(d, ",.00"));
    if (!kf_stricmp(type, "international")) return v_str(kprintf("USD%s", kf_numberformat(d, ",.00")));
    return v_str(kf_dollarformat(d));
}
F(lseurocurrencyformat) {
    double d = fa_num(c, call, argv, 0);
    return v_str(kprintf("EUR%s", kf_numberformat(d, ",.00")));
}
F(yesnoformat) {
    const char *s = fa_str(c, call, argv, 0);
    int b;
    if (!*s) return v_str("No");
    if (!v_tobool(argv[0], &b)) fn_param_error(c, call, 0, argv[0], "must be a boolean value");
    return v_str(b ? "Yes" : "No");
}
