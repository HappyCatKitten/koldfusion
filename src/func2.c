/*
 * func2.c - CFML built-in functions, part 2: arrays, structures, queries,
 * date/time, math, decision, system functions, and the function table.
 */
#define _GNU_SOURCE
#include "engine.h"
#include "func.h"
#include <stdlib.h>
#include <ctype.h>
#include <math.h>
#include <time.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/utsname.h>

static const char *D(int argc, Val *argv, int i, const char *def) { return argc > i ? v_tostr(argv[i]) : def; }

/* ================================================================ arrays */
F(arraynew) {
    int d = fa_int(c, call, argv, 0);
    if (d < 1 || d > 3) kf_throw_at(c, call, "Expression", "Invalid array dimension.",
                                    kprintf("Arrays may have 1, 2 or 3 dimensions; %d is not valid.", d));
    Array *a = array_new();
    a->dims = d;
    return v_arr(a);
}
F(arraylen) { (void)argc; return v_num(fa_arr(c, call, argv, 0)->n); }
F(arrayappend) { array_push(fa_arr(c, call, argv, 0), argv[1]); return v_bool(1); }
F(arrayprepend) { array_insert(fa_arr(c, call, argv, 0), 1, argv[1]); return v_bool(1); }
F(arrayinsertat) {
    Array *a = fa_arr(c, call, argv, 0); int p = fa_int(c, call, argv, 1);
    if (p < 1 || p > a->n + 1) kf_throw_at(c, call, "Expression", "Array index out of range.",
                                           kprintf("Cannot insert at position %d of an array with %d elements.", p, a->n));
    array_insert(a, p, argv[2]);
    return v_bool(1);
}
F(arraydeleteat) {
    Array *a = fa_arr(c, call, argv, 0); int p = fa_int(c, call, argv, 1);
    if (p < 1 || p > a->n) kf_throw_at(c, call, "Expression", "Array index out of range.",
                                       kprintf("Cannot delete element %d of an array with %d elements.", p, a->n));
    array_delete(a, p);
    return v_bool(1);
}
F(arrayset) {
    Array *a = fa_arr(c, call, argv, 0);
    int from = fa_int(c, call, argv, 1), to = fa_int(c, call, argv, 2);
    for (int i = from; i <= to; i++) array_set(a, i, argv[3]);
    return v_bool(1);
}
F(arrayresize) { Array *a = fa_arr(c, call, argv, 0); int n = fa_int(c, call, argv, 1); if (n > a->n) array_resize(a, n); return v_bool(1); }
F(arrayclear) { fa_arr(c, call, argv, 0)->n = 0; return v_bool(1); }
F(arrayisempty) { return v_bool(fa_arr(c, call, argv, 0)->n == 0); }
F(arrayswap) {
    Array *a = fa_arr(c, call, argv, 0); int i = fa_int(c, call, argv, 1), j = fa_int(c, call, argv, 2);
    if (i < 1 || j < 1 || i > a->n || j > a->n) kf_throw_at(c, call, "Expression", "Array index out of range.", "");
    Val t = a->v[i - 1]; a->v[i - 1] = a->v[j - 1]; a->v[j - 1] = t;
    return v_bool(1);
}
static double arr_num(Ctx *c, Expr *call, Val v) {
    double d;
    if (!v_tonum(v, &d)) kf_throw_at(c, call, "Expression", "Non-numeric value in array.",
                                     kprintf("The array element \"%s\" is not numeric.", v_is_simple(v) ? v_tostr(v) : v_typename(v)));
    return d;
}
F(arraysum) { Array *a = fa_arr(c, call, argv, 0); double s = 0; for (int i = 0; i < a->n; i++) s += arr_num(c, call, a->v[i]); return v_num(s); }
F(arrayavg) { Array *a = fa_arr(c, call, argv, 0); double s = 0; for (int i = 0; i < a->n; i++) s += arr_num(c, call, a->v[i]); return v_num(a->n ? s / a->n : 0); }
F(arraymin) { Array *a = fa_arr(c, call, argv, 0); double m = 0; for (int i = 0; i < a->n; i++) { double d = arr_num(c, call, a->v[i]); if (!i || d < m) m = d; } return v_num(m); }
F(arraymax) { Array *a = fa_arr(c, call, argv, 0); double m = 0; for (int i = 0; i < a->n; i++) { double d = arr_num(c, call, a->v[i]); if (!i || d > m) m = d; } return v_num(m); }
F(isarray) {
    (void)c; (void)call;
    if (argv[0].t != VT_ARRAY) return v_bool(0);
    if (argc > 1) { double d; v_tonum(argv[1], &d); return v_bool((argv[0].u.a->dims ? argv[0].u.a->dims : 1) == (int)d); }
    return v_bool(1);
}

/* ================================================================ structures */
F(structnew) { (void)c; (void)argc; (void)argv; (void)call; return v_struct(struct_new()); }
F(isstruct) { (void)c; (void)argc; (void)call; return v_bool(argv[0].t == VT_STRUCT); }
F(structinsert) {
    Struct *s = fa_struct(c, call, argv, 0);
    const char *k = fa_str(c, call, argv, 1);
    int ow = argc > 3 ? fa_bool(c, call, argv, 3) : 0;
    if (!ow && struct_get(s, k))
        kf_throw_at(c, call, "Expression", "Cannot insert key into structure.",
                    kprintf("The key %s already exists in the structure and the allowoverwrite argument is set to FALSE.", kf_upper(k)));
    struct_set(s, k, argv[2]);
    return v_bool(1);
}
F(structupdate) {
    Struct *s = fa_struct(c, call, argv, 0);
    const char *k = fa_str(c, call, argv, 1);
    if (!struct_get(s, k)) kf_throw_at(c, call, "Expression", kprintf("Cannot update key %s.", kf_upper(k)),
                                       kprintf("The key %s does not exist in the structure.", kf_upper(k)));
    struct_set(s, k, argv[2]);
    return v_bool(1);
}
F(structdelete) {
    Struct *s = fa_struct(c, call, argv, 0);
    int existed = struct_delete(s, fa_str(c, call, argv, 1));
    if (argc > 2 && fa_bool(c, call, argv, 2)) return v_bool(existed);
    return v_bool(1);
}
F(structfind) {
    Struct *s = fa_struct(c, call, argv, 0);
    const char *k = fa_str(c, call, argv, 1);
    Val *v = struct_get(s, k);
    if (!v) kf_throw_at(c, call, "Expression", kprintf("Cannot find %s key in structure.", kf_upper(k)),
                        "The specified key cannot be found in the structure.");
    return *v;
}
F(structkeyexists) { return v_bool(struct_get(fa_struct(c, call, argv, 0), fa_str(c, call, argv, 1)) != NULL); }
F(structkeylist) {
    Struct *s = fa_struct(c, call, argv, 0);
    const char *d = D(argc, argv, 1, ",");
    Buf b; buf_init(&b);
    for (int i = 0; i < s->n; i++) { if (i) buf_puts(&b, d); buf_puts(&b, kf_upper(s->e[i].key)); }
    return v_str(buf_cstr(&b));
}
F(structkeyarray) {
    Struct *s = fa_struct(c, call, argv, 0);
    Array *a = array_new();
    for (int i = 0; i < s->n; i++) array_push(a, v_str(kf_upper(s->e[i].key)));
    return v_arr(a);
}
F(structcount) { return v_num(fa_struct(c, call, argv, 0)->n); }
F(structclear) { struct_clear(fa_struct(c, call, argv, 0)); return v_bool(1); }
F(structisempty) { return v_bool(fa_struct(c, call, argv, 0)->n == 0); }
F(structcopy) { return v_struct(struct_copy(fa_struct(c, call, argv, 0), 0)); }
F(duplicate) { (void)c; (void)argc; (void)call; return v_deepcopy(argv[0]); }
F(structappend) {
    Struct *a = fa_struct(c, call, argv, 0), *b = fa_struct(c, call, argv, 1);
    int ow = argc > 2 ? fa_bool(c, call, argv, 2) : 1;
    for (int i = 0; i < b->n; i++) if (ow || !struct_get(a, b->e[i].key)) struct_set(a, b->e[i].key, b->e[i].v);
    return v_bool(1);
}
F(structget) {
    const char *path = fa_str(c, call, argv, 0);
    Val v;
    if (resolve_path(c, path, &v) && v.t == VT_STRUCT) return v;
    Struct *s = struct_new();
    assign_path(c, path, v_struct(s));
    resolve_path(c, path, &v);
    return v;
}

/* ================================================================ queries */
F(querynew) {
    Array *cols = list_to_array_k(fa_str(c, call, argv, 0), ",");
    Query *q = query_new(0, NULL);
    for (int i = 0; i < cols->n; i++) query_add_column(q, kf_trim(v_tostr(cols->v[i])));
    return v_query(q);
}
F(queryaddrow) {
    Query *q = fa_query(c, call, argv, 0);
    int n = argc > 1 ? fa_int(c, call, argv, 1) : 1;
    for (int i = 0; i < n; i++) query_add_row(q);
    return v_num(q->nrows);
}
F(querysetcell) {
    Query *q = fa_query(c, call, argv, 0);
    const char *col = fa_str(c, call, argv, 1);
    int row = argc > 3 ? fa_int(c, call, argv, 3) : q->nrows;
    int ci = query_col_index(q, col);
    if (ci < 0) kf_throw_at(c, call, "Expression", kprintf("Invalid column name %s.", kf_upper(col)),
                            kprintf("The query does not contain a column named %s. Columns: %s", kf_upper(col), query_column_list(q)));
    if (row < 1 || row > q->nrows) kf_throw_at(c, call, "Expression", "Invalid row number.",
                                               kprintf("Row %d is out of range; the query has %d rows.", row, q->nrows));
    query_set(q, ci, row - 1, v_is_simple(argv[2]) ? argv[2] : argv[2]);
    return v_bool(1);
}
F(queryaddcolumn) {
    Query *q = fa_query(c, call, argv, 0);
    const char *col = fa_str(c, call, argv, 1);
    Array *a = fa_arr(c, call, argv, 2);
    int ci = query_add_column(q, col);
    while (q->nrows < a->n) query_add_row(q);
    for (int i = 0; i < a->n; i++) query_set(q, ci, i, a->v[i]);
    return v_num(ci + 1);
}
F(isquery) { (void)c; (void)argc; (void)call; return v_bool(argv[0].t == VT_QUERY); }
static Val value_list(Ctx *c, Expr *call, int argc, Val *argv, int quoted) {
    (void)argv;
    Expr *a = call->args[0];
    if (a->k != E_DOT)
        kf_throw_at(c, call, "Expression", kprintf("Invalid parameter for function %s.", fn_name(call)),
                    "The argument must be a query column reference of the form query.column.");
    Val qv = eval(c, a->a);
    if (qv.t != VT_QUERY)
        kf_throw_at(c, call, "Expression", kprintf("Invalid parameter for function %s.", fn_name(call)),
                    "The argument must be a query column reference of the form query.column.");
    Query *q = qv.u.q;
    int ci = query_col_index(q, a->name);
    if (ci < 0) kf_throw_at(c, call, "Expression", kprintf("Column %s not found.", kf_upper(a->name)), "");
    const char *d = argc > 1 ? v_tostr(eval(c, call->args[1])) : ",";
    Buf b; buf_init(&b);
    for (int r = 0; r < q->nrows; r++) {
        if (r) buf_puts(&b, d);
        if (quoted) buf_putc(&b, '\'');
        buf_puts(&b, v_tostr(query_get(q, ci, r)));
        if (quoted) buf_putc(&b, '\'');
    }
    return v_str(buf_cstr(&b));
}
F(valuelist) { return value_list(c, call, argc, argv, 0); }
F(quotedvaluelist) { return value_list(c, call, argc, argv, 1); }

/* ================================================================ dates */
static double now(void) { return date_now(); }
F(now) { (void)c; (void)argc; (void)argv; (void)call; return v_date(now()); }
static int y2(int y) { return y < 0 ? y : y < 30 ? 2000 + y : y < 100 ? 1900 + y : y; }
F(createdate) {
    int y = y2(fa_int(c, call, argv, 0)), m = fa_int(c, call, argv, 1), d = fa_int(c, call, argv, 2);
    if (m < 1 || m > 12 || d < 1 || d > days_in_month(y, m) || y < 100)
        kf_throw_at(c, call, "Expression", "Invalid date.",
                    kprintf("The date %d/%d/%d is not a valid date (month/day/year).", m, d, y));
    return v_date(date_from_parts(y, m, d, 0, 0, 0));
}
F(createtime) {
    int h = fa_int(c, call, argv, 0), m = fa_int(c, call, argv, 1), s = fa_int(c, call, argv, 2);
    if (h < 0 || h > 23 || m < 0 || m > 59 || s < 0 || s > 59)
        kf_throw_at(c, call, "Expression", "Invalid time.", kprintf("%d:%d:%d is not a valid time.", h, m, s));
    return v_date((h * 3600.0 + m * 60 + s) / 86400.0);
}
F(createdatetime) {
    int y = y2(fa_int(c, call, argv, 0)), mo = fa_int(c, call, argv, 1), d = fa_int(c, call, argv, 2);
    int h = fa_int(c, call, argv, 3), mi = fa_int(c, call, argv, 4), s = fa_int(c, call, argv, 5);
    if (mo < 1 || mo > 12 || d < 1 || d > days_in_month(y, mo) || h > 23 || mi > 59 || s > 59)
        kf_throw_at(c, call, "Expression", "Invalid date/time.", "One of the date or time parts is out of range.");
    return v_date(date_from_parts(y, mo, d, h, mi, s));
}
F(createodbcdate) {
    int y, mo, d; date_to_parts(fa_date(c, call, argv, 0), &y, &mo, &d, NULL, NULL, NULL);
    return v_str(kprintf("{d '%04d-%02d-%02d'}", y, mo, d));
}
F(createodbctime) {
    int h, mi, s; date_to_parts(fa_date(c, call, argv, 0), NULL, NULL, NULL, &h, &mi, &s);
    return v_str(kprintf("{t '%02d:%02d:%02d'}", h, mi, s));
}
F(createodbcdatetime) { return v_str(date_odbc(fa_date(c, call, argv, 0))); }
F(createtimespan) {
    return v_num(fa_num(c, call, argv, 0) + fa_num(c, call, argv, 1) / 24.0 + fa_num(c, call, argv, 2) / 1440.0 +
                 fa_num(c, call, argv, 3) / 86400.0);
}
static int part_of(double dt, const char *part) {
    int y, mo, d, h, mi, s;
    date_to_parts(dt, &y, &mo, &d, &h, &mi, &s);
    if (!kf_stricmp(part, "yyyy")) return y;
    if (!kf_stricmp(part, "q")) return (mo - 1) / 3 + 1;
    if (!kf_stricmp(part, "m")) return mo;
    if (!kf_stricmp(part, "y")) return (int)(floor(dt) - date_from_parts(y, 1, 1, 0, 0, 0)) + 1;
    if (!kf_stricmp(part, "d")) return d;
    if (!kf_stricmp(part, "w")) return date_dow(dt);
    if (!kf_stricmp(part, "ww")) {
        double j1 = date_from_parts(y, 1, 1, 0, 0, 0);
        int doy = (int)(floor(dt) - j1) + 1;
        return (doy + date_dow(j1) - 2) / 7 + 1;
    }
    if (!kf_stricmp(part, "h")) return h;
    if (!kf_stricmp(part, "n")) return mi;
    if (!kf_stricmp(part, "s")) return s;
    return -1;
}
static void bad_part(Ctx *c, Expr *call, const char *part) __attribute__((noreturn));
static void bad_part(Ctx *c, Expr *call, const char *part) {
    kf_throw_at(c, call, "Expression", kprintf("Invalid date part %s.", kf_html_escape(part)),
                "The datepart must be one of yyyy, q, m, y, d, w, ww, h, n, s.");
}
F(datepart) {
    const char *p = fa_str(c, call, argv, 0);
    int r = part_of(fa_date(c, call, argv, 1), p);
    if (r < 0) bad_part(c, call, p);
    return v_num(r);
}
static double add_months(double dt, int n) {
    int y, mo, d, h, mi, s;
    date_to_parts(dt, &y, &mo, &d, &h, &mi, &s);
    int total = y * 12 + (mo - 1) + n;
    y = total / 12; mo = total % 12 + 1;
    if (d > days_in_month(y, mo)) d = days_in_month(y, mo);
    return date_from_parts(y, mo, d, h, mi, s);
}
F(dateadd) {
    const char *p = fa_str(c, call, argv, 0);
    double n = fa_num(c, call, argv, 1), dt = fa_date(c, call, argv, 2);
    int ni = (int)n;
    if (!kf_stricmp(p, "yyyy")) return v_date(add_months(dt, ni * 12));
    if (!kf_stricmp(p, "q")) return v_date(add_months(dt, ni * 3));
    if (!kf_stricmp(p, "m")) return v_date(add_months(dt, ni));
    if (!kf_stricmp(p, "y") || !kf_stricmp(p, "d") || !kf_stricmp(p, "w")) return v_date(dt + ni);
    if (!kf_stricmp(p, "ww")) return v_date(dt + ni * 7);
    if (!kf_stricmp(p, "h")) return v_date(dt + ni / 24.0);
    if (!kf_stricmp(p, "n")) return v_date(dt + ni / 1440.0);
    if (!kf_stricmp(p, "s")) return v_date(dt + ni / 86400.0);
    bad_part(c, call, p);
}
F(datediff) {
    const char *p = fa_str(c, call, argv, 0);
    double a = fa_date(c, call, argv, 1), b = fa_date(c, call, argv, 2);
    double diff = b - a;
    if (!kf_stricmp(p, "yyyy") || !kf_stricmp(p, "q") || !kf_stricmp(p, "m")) {
        int y1, m1, d1, h1, i1, s1, y2, m2, d2, h2, i2, s2;
        date_to_parts(a, &y1, &m1, &d1, &h1, &i1, &s1);
        date_to_parts(b, &y2, &m2, &d2, &h2, &i2, &s2);
        int months = (y2 - y1) * 12 + (m2 - m1);
        double frac1 = d1 + (h1 * 3600 + i1 * 60 + s1) / 86400.0, frac2 = d2 + (h2 * 3600 + i2 * 60 + s2) / 86400.0;
        if (months > 0 && frac2 < frac1) months--;
        if (months < 0 && frac2 > frac1) months++;
        if (!kf_stricmp(p, "yyyy")) return v_num(months / 12);
        if (!kf_stricmp(p, "q")) return v_num(months / 3);
        return v_num(months);
    }
    long unit;
    if (!kf_stricmp(p, "y") || !kf_stricmp(p, "d") || !kf_stricmp(p, "w")) unit = 86400;
    else if (!kf_stricmp(p, "ww")) unit = 7 * 86400;
    else if (!kf_stricmp(p, "h")) unit = 3600;
    else if (!kf_stricmp(p, "n")) unit = 60;
    else if (!kf_stricmp(p, "s")) unit = 1;
    else bad_part(c, call, p);
    long secs = (long)llround(diff * 86400.0);
    return v_num((double)(secs / unit));
}
F(datecompare) {
    double a = fa_date(c, call, argv, 0), b = fa_date(c, call, argv, 1);
    const char *p = D(argc, argv, 2, "s");
    double unit = 1 / 86400.0;
    if (!kf_stricmp(p, "yyyy")) { int ya = part_of(a, "yyyy"), yb = part_of(b, "yyyy"); return v_num(ya < yb ? -1 : ya > yb); }
    if (!kf_stricmp(p, "m")) { double x = part_of(a, "yyyy") * 12 + part_of(a, "m"), y = part_of(b, "yyyy") * 12 + part_of(b, "m"); return v_num(x < y ? -1 : x > y); }
    if (!kf_stricmp(p, "d")) unit = 1;
    else if (!kf_stricmp(p, "h")) unit = 1 / 24.0;
    else if (!kf_stricmp(p, "n")) unit = 1 / 1440.0;
    double x = floor(a / unit + 1e-7), y = floor(b / unit + 1e-7);
    return v_num(x < y ? -1 : x > y);
}
F(dateconvert) {
    const char *how = fa_str(c, call, argv, 0);
    double d = fa_date(c, call, argv, 1);
    if (!kf_stricmp(how, "local2utc")) return v_date(date_local_to_utc(d));
    if (!kf_stricmp(how, "utc2local")) return v_date(date_utc_to_local(d));
    kf_throw_at(c, call, "Expression", "Invalid conversion type.", "Use local2Utc or utc2Local.");
}
#define DATEPART_FN(nm, part) F(nm) { (void)argc; return v_num(part_of(fa_date(c, call, argv, 0), part)); }
DATEPART_FN(year, "yyyy") DATEPART_FN(month, "m") DATEPART_FN(day, "d") DATEPART_FN(hour, "h")
DATEPART_FN(minute, "n") DATEPART_FN(second, "s") DATEPART_FN(dayofweek, "w") DATEPART_FN(dayofyear, "y")
DATEPART_FN(quarter, "q") DATEPART_FN(week, "ww")
F(dayofweekasstring) {
    static const char *DN[] = {"Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"};
    int d = fa_int(c, call, argv, 0);
    if (d < 1 || d > 7) fn_param_error(c, call, 0, argv[0], "must be in the range 1 to 7");
    return v_str(DN[d - 1]);
}
F(monthasstring) {
    static const char *MN[] = {"January","February","March","April","May","June","July","August","September","October","November","December"};
    int m = fa_int(c, call, argv, 0);
    if (m < 1 || m > 12) fn_param_error(c, call, 0, argv[0], "must be in the range 1 to 12");
    return v_str(MN[m - 1]);
}
F(daysinmonth) { int y, m; date_to_parts(fa_date(c, call, argv, 0), &y, &m, NULL, NULL, NULL, NULL); return v_num(days_in_month(y, m)); }
F(daysinyear) { int y; date_to_parts(fa_date(c, call, argv, 0), &y, NULL, NULL, NULL, NULL, NULL); return v_num(is_leap(y) ? 366 : 365); }
F(firstdayofmonth) {
    double d = fa_date(c, call, argv, 0);
    int y, m; date_to_parts(d, &y, &m, NULL, NULL, NULL, NULL);
    return v_num(floor(date_from_parts(y, m, 1, 0, 0, 0)) - floor(date_from_parts(y, 1, 1, 0, 0, 0)) + 1);
}
F(isdate) {
    (void)c; (void)call;
    if (argv[0].t == VT_DATE) return v_bool(1);
    if (argv[0].t != VT_STR) return v_bool(0);
    double d;
    if (v_isnumeric_str(argv[0].u.str.s, NULL)) return v_bool(0);
    return v_bool(date_parse(argv[0].u.str.s, &d));
}
F(isnumericdate) { (void)argc; (void)c; (void)call; double d; return v_bool(v_tonum(argv[0], &d)); }
F(isleapyear) { return v_bool(is_leap(fa_int(c, call, argv, 0))); }
F(parsedatetime) {
    double d;
    if (argv[0].t == VT_DATE) return argv[0];
    if (!v_todate(argv[0], &d)) fn_param_error(c, call, 0, argv[0], "must be a valid date/time string");
    return v_date(d);
}
F(gethttptimestring) {
    double d = argc ? fa_date(c, call, argv, 0) : now();
    d = date_local_to_utc(d);
    int y, mo, dd, h, mi, s;
    date_to_parts(d, &y, &mo, &dd, &h, &mi, &s);
    static const char *DN[] = {"Sun","Mon","Tue","Wed","Thu","Fri","Sat"};
    static const char *MN[] = {"Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"};
    return v_str(kprintf("%s, %02d %s %04d %02d:%02d:%02d GMT", DN[date_dow(d) - 1], dd, MN[mo - 1], y, h, mi, s));
}
F(gettimezoneinfo) {
    (void)c; (void)argc; (void)argv; (void)call;
    time_t t = time(NULL);
    struct tm lt; localtime_r(&t, &lt);
    Struct *s = struct_new();
    long off = -lt.tm_gmtoff;   /* CF reports seconds to ADD to local time to get UTC */
    struct_set(s, "utcTotalOffset", v_num((double)off));
    struct_set(s, "utcHourOffset", v_num((double)(off / 3600)));
    struct_set(s, "utcMinuteOffset", v_num((double)((labs(off) % 3600) / 60)));
    struct_set(s, "isDSTOn", v_bool(lt.tm_isdst > 0));
    return v_struct(s);
}

/* ================================================================ math */
#define MATH1(nm, expr) F(nm) { (void)argc; double x = fa_num(c, call, argv, 0); return v_num(expr); }
MATH1(abs, fabs(x)) MATH1(ceiling, ceil(x)) MATH1(int, floor(x)) MATH1(fix, trunc(x))
MATH1(round, floor(x + 0.5)) MATH1(sgn, x > 0 ? 1 : x < 0 ? -1 : 0) MATH1(exp, exp(x))
MATH1(sin, sin(x)) MATH1(cos, cos(x)) MATH1(tan, tan(x)) MATH1(atn, atan(x))
MATH1(incrementvalue, floor(x) + 1) MATH1(decrementvalue, floor(x) - 1)
F(sqr) { double x = fa_num(c, call, argv, 0); if (x < 0) fn_param_error(c, call, 0, argv[0], "must be a non-negative number"); return v_num(sqrt(x)); }
F(log) { double x = fa_num(c, call, argv, 0); if (x <= 0) fn_param_error(c, call, 0, argv[0], "must be a positive number"); return v_num(log(x)); }
F(log10) { double x = fa_num(c, call, argv, 0); if (x <= 0) fn_param_error(c, call, 0, argv[0], "must be a positive number"); return v_num(log10(x)); }
F(asin) { double x = fa_num(c, call, argv, 0); if (x < -1 || x > 1) fn_param_error(c, call, 0, argv[0], "must be between -1 and 1"); return v_num(asin(x)); }
F(acos) { double x = fa_num(c, call, argv, 0); if (x < -1 || x > 1) fn_param_error(c, call, 0, argv[0], "must be between -1 and 1"); return v_num(acos(x)); }
F(pi) { (void)c; (void)argc; (void)argv; (void)call; return v_num(M_PI); }
F(min) { double a = fa_num(c, call, argv, 0), b = fa_num(c, call, argv, 1); return v_num(a < b ? a : b); }
F(max) { double a = fa_num(c, call, argv, 0), b = fa_num(c, call, argv, 1); return v_num(a > b ? a : b); }
static __thread unsigned int rnd_state;
static double rnd(void) {
    if (!rnd_state) rnd_state = (unsigned)time(NULL) ^ (unsigned)(uintptr_t)&rnd_state;
    return (double)rand_r(&rnd_state) / ((double)RAND_MAX + 1.0);
}
F(rand) { (void)c; (void)argc; (void)argv; (void)call; return v_num(rnd()); }
F(randomize) { rnd_state = (unsigned)fa_int(c, call, argv, 0); return v_num(rnd()); }
F(randrange) {
    int a = fa_int(c, call, argv, 0), b = fa_int(c, call, argv, 1);
    if (a > b) { int t = a; a = b; b = t; }
    return v_num(a + (int)(rnd() * (b - a + 1)));
}
F(bitand) { return v_num((double)((long)fa_num(c, call, argv, 0) & (long)fa_num(c, call, argv, 1))); }
F(bitor) { return v_num((double)((long)fa_num(c, call, argv, 0) | (long)fa_num(c, call, argv, 1))); }
F(bitxor) { return v_num((double)((long)fa_num(c, call, argv, 0) ^ (long)fa_num(c, call, argv, 1))); }
F(bitnot) { return v_num((double)(int32_t)~(int32_t)(long)fa_num(c, call, argv, 0)); }
F(bitshln) { return v_num((double)(int32_t)((uint32_t)(long)fa_num(c, call, argv, 0) << fa_int(c, call, argv, 1))); }
F(bitshrn) { return v_num((double)((uint32_t)(long)fa_num(c, call, argv, 0) >> fa_int(c, call, argv, 1))); }
F(bitmaskread) {
    uint32_t n = (uint32_t)(long)fa_num(c, call, argv, 0); int st = fa_int(c, call, argv, 1), len = fa_int(c, call, argv, 2);
    return v_num((double)((n >> st) & ((1u << len) - 1)));
}
F(bitmaskset) {
    uint32_t n = (uint32_t)(long)fa_num(c, call, argv, 0), m = (uint32_t)(long)fa_num(c, call, argv, 1);
    int st = fa_int(c, call, argv, 2), len = fa_int(c, call, argv, 3);
    uint32_t mask = ((1u << len) - 1) << st;
    return v_num((double)(int32_t)((n & ~mask) | ((m << st) & mask)));
}
F(bitmaskclear) {
    uint32_t n = (uint32_t)(long)fa_num(c, call, argv, 0); int st = fa_int(c, call, argv, 1), len = fa_int(c, call, argv, 2);
    return v_num((double)(int32_t)(n & ~(((1u << len) - 1) << st)));
}
F(formatbasen) {
    long n = (long)fa_num(c, call, argv, 0); int radix = fa_int(c, call, argv, 1);
    if (radix < 2 || radix > 36) fn_param_error(c, call, 1, argv[1], "must be between 2 and 36");
    char buf[80]; int i = 79; buf[i] = 0;
    int neg = n < 0; unsigned long u = neg ? (unsigned long)(-n) : (unsigned long)n;
    do { buf[--i] = "0123456789abcdefghijklmnopqrstuvwxyz"[u % radix]; u /= radix; } while (u);
    if (neg) buf[--i] = '-';
    return v_strdup(buf + i);
}
F(inputbasen) {
    const char *s = fa_str(c, call, argv, 0); int radix = fa_int(c, call, argv, 1);
    char *end;
    long v = strtol(s, &end, radix);
    if (*end || !*s) fn_param_error(c, call, 0, argv[0], kprintf("must be a valid base %d number", radix));
    return v_num((double)v);
}

/* ================================================================ decision */
F(isdefined) { return v_bool(resolve_path(c, fa_str(c, call, argv, 0), NULL)); }
F(parameterexists) {
    Expr *a = call->args[0];
    if (a->k != E_VAR && a->k != E_DOT && a->k != E_INDEX) return v_bool(1);
    const char *path = kstrndup(a->src, a->srclen);
    return v_bool(resolve_path(c, path, NULL));
}
F(issimplevalue) { (void)c; (void)argc; (void)call; return v_bool(v_is_simple(argv[0])); }
F(isnumeric) {
    (void)c; (void)argc; (void)call;
    if (argv[0].t == VT_NUM) return v_bool(1);
    if (argv[0].t != VT_STR) return v_bool(0);
    return v_bool(v_isnumeric_str(argv[0].u.str.s, NULL));
}
F(isboolean) { (void)c; (void)argc; (void)call; int b; return v_bool(v_is_simple(argv[0]) && v_tobool(argv[0], &b)); }
F(isbinary) { (void)c; (void)argc; (void)call; return v_bool(argv[0].t == VT_BINARY); }
F(isdebugmode) { (void)argc; (void)argv; (void)call; return v_bool(c->rs->show_debug && c->rs->debug_override != 0); }
int wddx_deserialize(const char *packet, Val *out, const char **err);
F(iswddx) {
    (void)argc; (void)call; (void)c;
    if (!v_is_simple(argv[0])) return v_bool(0);
    Val v; const char *err;
    return v_bool(wddx_deserialize(v_tostr(argv[0]), &v, &err));
}

/* ================================================================ dynamic evaluation */
F(evaluate) {
    Val r = v_null();
    for (int i = 0; i < argc; i++) {
        const char *src = fa_str(c, call, argv, i);
        const char *err;
        if (!*kf_trim(src)) { r = v_str(""); continue; }
        Expr *e = expr_parse_string(src, &err);
        if (!e) kf_throw_at(c, call, "Expression", kprintf("An error has occurred while processing the expression:<P>%s",
                                                           kf_html_escape(src)), err);
        r = eval(c, e);
    }
    return r;
}
F(de) {
    const char *s = fa_str(c, call, argv, 0);
    Buf b; buf_init(&b);
    buf_putc(&b, '"');
    for (; *s; s++) { if (*s == '"') buf_putc(&b, '"'); buf_putc(&b, *s); }
    buf_putc(&b, '"');
    return v_str(buf_cstr(&b));
}
F(iif) {
    int cond = fa_bool(c, call, argv, 0);
    const char *src = fa_str(c, call, argv, cond ? 1 : 2);
    const char *err;
    if (!*kf_trim(src)) return v_str("");
    Expr *e = expr_parse_string(src, &err);
    if (!e) kf_throw_at(c, call, "Expression", kprintf("An error has occurred while processing the expression:<P>%s",
                                                       kf_html_escape(src)), err);
    return eval(c, e);
}
F(setvariable) { (void)argc; assign_path(c, fa_str(c, call, argv, 0), argv[1]); return argv[1]; }
F(preservesinglequotes) { (void)c; (void)argc; (void)call; return argv[0]; }
F(writeoutput) { (void)argc; out_puts(c, fa_str(c, call, argv, 0)); return v_bool(1); }

/* ================================================================ system */
char *kf_create_uuid(void) {
    unsigned char b[16];
    FILE *f = fopen("/dev/urandom", "rb");
    if (!f || fread(b, 1, 16, f) != 16) for (int i = 0; i < 16; i++) b[i] = (unsigned char)(rnd() * 256);
    if (f) fclose(f);
    char hex[33];
    for (int i = 0; i < 16; i++) snprintf(hex + i * 2, 3, "%02X", b[i]);
    return kprintf("%.8s-%.4s-%.4s-%.16s", hex, hex + 8, hex + 12, hex + 16);
}
F(createuuid) { (void)c; (void)argc; (void)argv; (void)call; return v_str(kf_create_uuid()); }
F(gettickcount) { (void)c; (void)argc; (void)argv; (void)call; return v_num(floor(kf_time_ms())); }
F(getbasetemplatepath) { (void)argc; (void)argv; (void)call; return v_strdup(c->rs->base_template ? c->rs->base_template : ""); }
F(getcurrenttemplatepath) { (void)argc; (void)argv; (void)call; return v_strdup(c->rs->cur_tpl ? c->rs->cur_tpl->path : ""); }
F(getdirectoryfrompath) {
    const char *p = fa_str(c, call, argv, 0);
    const char *a = strrchr(p, '/'), *b = strrchr(p, '\\');
    const char *sl = a > b ? a : b;
    return v_str(sl ? kstrndup(p, sl - p + 1) : kstrdup(""));
}
F(getfilefrompath) { const char *p = fa_str(c, call, argv, 0); const char *s = strrchr(p, '/'); if (!s) s = strrchr(p, '\\'); return v_strdup(s ? s + 1 : p); }
F(expandpath) {
    const char *p = fa_str(c, call, argv, 0);
    Ctx tmp = *c;
    tmp.tagdir = kf_template_dir(c->rs->base_template ? c->rs->base_template : kf_docroot());
    return v_strdup(resolve_template_path(&tmp, p, 0));
}
F(fileexists) {
    struct stat st;
    return v_bool(stat(kf_native_path(fa_str(c, call, argv, 0)), &st) == 0 && S_ISREG(st.st_mode));
}
F(directoryexists) {
    struct stat st;
    return v_bool(stat(kf_native_path(fa_str(c, call, argv, 0)), &st) == 0 && S_ISDIR(st.st_mode));
}
F(gettempdirectory) { (void)c; (void)argc; (void)argv; (void)call; char *d = kf_path_join(G.root, "temp/"); kf_mkdirs(d); return v_str(d); }
F(gettempfile) {
    const char *dir = fa_str(c, call, argv, 0), *prefix = fa_str(c, call, argv, 1);
    char *p = kf_path_join(dir, kprintf("%.3sXXXXXX", prefix));
    int fd = mkstemp(p);
    if (fd < 0) kf_throw_at(c, call, "Expression", "Unable to create a temporary file.", kprintf("Directory %s.", kf_html_escape(dir)));
    close(fd);
    char *np = kprintf("%s.tmp", p);
    rename(p, np);
    return v_str(np);
}
F(getbasetaglist) {
    (void)argc; (void)argv; (void)call;
    RState *rs = c->rs;
    Buf b; buf_init(&b);
    if (rs->tagstack) for (int i = rs->tagstack->n - 1; i >= 0; i--) {
        if (b.len) buf_putc(&b, ',');
        buf_puts(&b, v_tostr(rs->tagstack->v[i]));
    }
    return v_str(buf_cstr(&b));
}
F(getbasetagdata) {
    const char *name = fa_str(c, call, argv, 0);
    int inst = argc > 1 ? fa_int(c, call, argv, 1) : 1;
    RState *rs = c->rs;
    if (rs->tagstack) for (int i = rs->tagstack->n - 1; i >= 0; i--) {
        if (!kf_stricmp(v_tostr(rs->tagstack->v[i]), name) && --inst == 0) {
            Struct *td = rs->tagdata->v[i].u.st;
            Val *vars = struct_get(td, "__variables");
            if (!vars) return rs->tagdata->v[i];
            /* the ancestor's live Variables scope: children may change the base tag's data */
            Struct *r = vars->u.st;
            if (!struct_get(r, "ThisTag")) struct_set(r, "ThisTag", *struct_get(td, "ThisTag"));
            if (!struct_get(r, "Attributes")) struct_set(r, "Attributes", *struct_get(td, "Attributes"));
            return v_struct(r);
        }
    }
    kf_throw_at(c, call, "Expression", kprintf("Cannot find base tag %s.", kf_upper(name)),
                "The requested tag is not an ancestor of the current custom tag.");
}
static char *ini_get(const char *path, const char *section, const char *entry) {
    size_t len;
    char *data = kf_read_file(path, &len);
    if (!data) return NULL;
    char *res = NULL;
    int in = 0;
    for (char *line = strtok(data, "\n"); line; line = strtok(NULL, "\n")) {
        char *l = kf_trim(line);
        if (*l == '[') { char *e = strchr(l, ']'); if (e) *e = 0; in = !kf_stricmp(l + 1, section); continue; }
        if (!in) continue;
        char *eq = strchr(l, '=');
        if (!eq) continue;
        *eq = 0;
        if (!kf_stricmp(kf_trim(l), entry)) { res = kf_trim(eq + 1); break; }
    }
    free(data);
    return res;
}
F(getprofilestring) {
    char *r = ini_get(fa_str(c, call, argv, 0), fa_str(c, call, argv, 1), fa_str(c, call, argv, 2));
    return v_str(r ? r : "");
}
F(setprofilestring) {
    const char *path = fa_str(c, call, argv, 0), *section = fa_str(c, call, argv, 1);
    const char *entry = fa_str(c, call, argv, 2), *value = fa_str(c, call, argv, 3);
    size_t len;
    char *data = kf_read_file(path, &len);
    Buf b; buf_init(&b);
    int in = 0, done = 0, found_section = 0;
    if (data) {
        char *save;
        for (char *line = strtok_r(data, "\n", &save); line; line = strtok_r(NULL, "\n", &save)) {
            char *l = kf_trim(line);
            if (*l == '[') {
                if (in && !done) { buf_printf(&b, "%s=%s\n", entry, value); done = 1; }
                char *nm = kstrdup(l + 1); char *e = strchr(nm, ']'); if (e) *e = 0;
                in = !kf_stricmp(nm, section);
                if (in) found_section = 1;
            } else if (in && !done) {
                char *eq = strchr(l, '=');
                if (eq && !kf_stricmp(kf_trim(kstrndup(l, eq - l)), entry)) { buf_printf(&b, "%s=%s\n", entry, value); done = 1; continue; }
            }
            buf_printf(&b, "%s\n", line);
        }
        free(data);
    }
    if (!done) {
        if (!found_section) buf_printf(&b, "[%s]\n", section);
        buf_printf(&b, "%s=%s\n", entry, value);
    }
    kf_write_file(path, b.s, b.len, 0);
    return v_str("");
}
F(getmetricdata) {
    const char *mode = fa_str(c, call, argv, 0);
    if (kf_stricmp(mode, "perf_monitor"))
        kf_throw_at(c, call, "Expression", "Invalid mode for GetMetricData.", "The only supported mode is PERF_MONITOR.");
    Struct *s = struct_new();
    struct_set(s, "InstanceName", v_str("KoldFusion Server"));
    struct_set(s, "PageHits", v_num((double)G.requests_served));
    struct_set(s, "ReqQueued", v_num(G.queued_requests));
    struct_set(s, "ReqRunning", v_num(G.active_requests));
    struct_set(s, "ReqTimedOut", v_num(G.unresponsive));
    struct_set(s, "BytesIn", v_num(0));
    struct_set(s, "BytesOut", v_num(0));
    struct_set(s, "AvgQueueTime", v_num(0));
    struct_set(s, "AvgReqTime", v_num(0));
    struct_set(s, "AvgDBTime", v_num(0));
    struct_set(s, "DBHits", v_num(0));
    return v_struct(s);
}
F(getclientvariableslist) {
    (void)argc; (void)argv; (void)call;
    RState *rs = c->rs;
    if (!rs->client_enabled) return v_str("");
    Buf b; buf_init(&b);
    for (int i = 0; i < rs->client->n; i++) {
        const char *k = rs->client->e[i].key;
        if (!kf_stricmp(k, "cfid") || !kf_stricmp(k, "cftoken") || !kf_stricmp(k, "urltoken") ||
            !kf_stricmp(k, "hitcount") || !kf_stricmp(k, "lastvisit") || !kf_stricmp(k, "timecreated")) continue;
        if (b.len) buf_putc(&b, ',');
        buf_puts(&b, kf_upper(k));
    }
    return v_str(buf_cstr(&b));
}
F(deleteclientvariable) {
    RState *rs = c->rs;
    if (!rs->client_enabled) return v_bool(0);
    rs->client_dirty = 1;
    return v_bool(struct_delete(rs->client, fa_str(c, call, argv, 0)));
}
static const char *LOCALES[] = {"English (US)", "English (UK)", "English (Australian)", "English (Canadian)",
    "English (New Zealand)", "French (Standard)", "French (Canadian)", "French (Belgian)", "French (Swiss)",
    "German (Standard)", "German (Austrian)", "German (Swiss)", "Italian (Standard)", "Italian (Swiss)",
    "Spanish (Standard)", "Spanish (Mexican)", "Spanish (Modern)", "Dutch (Standard)", "Dutch (Belgian)",
    "Norwegian (Bokmal)", "Norwegian (Nynorsk)", "Portuguese (Standard)", "Portuguese (Brazilian)", "Swedish", NULL};
F(setlocale) {
    const char *want = fa_str(c, call, argv, 0);
    for (int i = 0; LOCALES[i]; i++) {
        if (!kf_stricmp(LOCALES[i], want)) {
            const char *old = c->rs->locale ? c->rs->locale : "English (US)";
            c->rs->locale = LOCALES[i];
            return v_str(old);
        }
    }
    kf_throw_at(c, call, "Expression", kprintf("Invalid locale %s.", kf_html_escape(want)),
                "Server.ColdFusion.SupportedLocales lists the locales this server supports. "
                "(KoldFusion formats every locale like English (US).)");
}
F(getlocale) { (void)argc; (void)argv; (void)call; return v_str(c->rs->locale ? c->rs->locale : "English (US)"); }
F(createobject) {
    const char *type = fa_str(c, call, argv, 0);
    if (!kf_stricmp(type, "com"))
        kf_throw_at(c, call, "Object", "COM objects are not supported on this platform.",
                    "KoldFusion for UNIX does not support COM. The CFOBJECT tag and CreateObject() can only create COM objects "
                    "on Windows NT.");
    if (!kf_stricmp(type, "corba"))
        kf_throw_at(c, call, "Object", "Unable to initialise the CORBA ORB.",
                    "No Visibroker ORB is installed on this server.");
    kf_throw_at(c, call, "Object", "Unable to create the Java object.",
                "The Java Virtual Machine could not be loaded. Check the Java settings in the KoldFusion Administrator "
                "(Server &gt; Java).");
}
F(javacast) {
    (void)argc;
    const char *type = fa_str(c, call, argv, 0);
    if (!kf_stricmp(type, "int") || !kf_stricmp(type, "long")) return v_num(trunc(fa_num(c, call, argv, 1)));
    if (!kf_stricmp(type, "double") || !kf_stricmp(type, "float")) return v_num(fa_num(c, call, argv, 1));
    if (!kf_stricmp(type, "boolean")) return v_bool(fa_bool(c, call, argv, 1));
    if (!kf_stricmp(type, "string")) return v_strdup(fa_str(c, call, argv, 1));
    kf_throw_at(c, call, "Expression", kprintf("Invalid JavaCast type %s.", kf_html_escape(type)),
                "The type must be one of boolean, int, long, float, double, string.");
}
F(getfunctionlist) {
    (void)argc; (void)argv; (void)call; (void)c;
    Query *q = func_list_all();
    Struct *s = struct_new();
    for (int r = 0; r < q->nrows; r++) struct_set(s, v_tostr(query_get(q, 0, r)), v_str(""));
    return v_struct(s);
}

/* advanced security (security.c) */
int sec_is_authenticated(RState *rs, const char *context);
int sec_is_authorized(RState *rs, const char *type, const char *resource, const char *action);
int sec_is_protected(const char *type, const char *resource, const char *action);
F(isauthenticated) { return v_bool(sec_is_authenticated(c->rs, argc ? fa_str(c, call, argv, 0) : NULL)); }
F(isauthorized) {
    return v_bool(sec_is_authorized(c->rs, fa_str(c, call, argv, 0), fa_str(c, call, argv, 1), D(argc, argv, 2, "")));
}
F(isprotected) { return v_bool(sec_is_protected(fa_str(c, call, argv, 0), fa_str(c, call, argv, 1), D(argc, argv, 2, ""))); }
F(authenticateduser) { (void)argc; (void)argv; (void)call; return v_str(c->rs->auth_user ? c->rs->auth_user : ""); }
F(authenticatedcontext) {
    (void)argc; (void)argv; (void)call;
    Val *v = c->rs->auth ? struct_get(c->rs->auth, "context") : NULL;
    return v ? *v : v_str("");
}

/* LS (locale-sensitive) functions: English (US) only */
F(lsisnumeric) { return fn_isnumeric(c, argc, argv, call); }
static int ls_strip(const char *s, Buf *b, int *neg) {
    *neg = 0;
    buf_init(b);
    for (; *s; s++) {
        if (*s == '(') *neg = 1;
        else if (*s == ',' || *s == '$' || *s == ' ' || *s == ')') continue;
        else if (!kf_strnicmp(s, "USD", 3) || !kf_strnicmp(s, "EUR", 3)) { s += 2; continue; }
        else buf_putc(b, *s);
    }
    double d;
    return v_isnumeric_str(buf_cstr(b), &d);
}
F(lsparsenumber) {
    (void)argc;
    Buf b; int neg; double d;
    const char *s = fa_str(c, call, argv, 0);
    if (strpbrk(s, "$(") || !ls_strip(s, &b, &neg) || !v_isnumeric_str(buf_cstr(&b), &d))
        fn_param_error(c, call, 0, argv[0], "must be a valid number in the current locale");
    return v_num(neg ? -d : d);
}
F(lsiscurrency) {
    (void)argc; Buf b; int neg;
    return v_bool(ls_strip(fa_str(c, call, argv, 0), &b, &neg));
}
F(lsparsecurrency) {
    (void)argc; Buf b; int neg; double d;
    if (!ls_strip(fa_str(c, call, argv, 0), &b, &neg) || !v_isnumeric_str(buf_cstr(&b), &d))
        fn_param_error(c, call, 0, argv[0], "must be a valid currency value");
    return v_num(neg ? -d : d);
}

/* ================================================================ table */
#define FN(name, mn, mx) {#name, fn_##name, mn, mx}
/* part 1 functions */
#define X(nm) Val fn_##nm(Ctx *, int, Val *, Expr *);
X(listlen) X(listgetat) X(listfirst) X(listlast) X(listrest) X(listappend) X(listprepend) X(listsetat)
X(listinsertat) X(listdeleteat) X(listfind) X(listfindnocase) X(listcontains) X(listcontainsnocase)
X(listchangedelims) X(listtoarray) X(arraytolist) X(listvaluecount) X(listvaluecountnocase) X(listqualify)
X(listsort) X(arraysort) X(len) X(left) X(right) X(mid) X(ucase) X(lcase) X(trim) X(ltrim) X(rtrim)
X(find) X(findnocase) X(findoneof) X(replace) X(replacenocase) X(replacelist) X(removechars)
X(repeatstring) X(reverse) X(spanincluding) X(spanexcluding) X(gettoken) X(asc) X(chr) X(val)
X(compare) X(comparenocase) X(stripcr) X(insert) X(ljustify) X(cjustify) X(rjustify) X(paragraphformat)
X(wrap) X(htmleditformat) X(htmlcodeformat) X(urlencodedformat) X(urldecode) X(jsstringformat)
X(xmlformat) X(hash) X(encrypt) X(decrypt) X(tobase64) X(tobinary) X(tostring) X(refind)
X(refindnocase) X(rereplace) X(rereplacenocase) X(dateformat) X(timeformat) X(numberformat)
X(decimalformat) X(dollarformat) X(lscurrencyformat) X(lseurocurrencyformat) X(yesnoformat)

static const FuncDef FUNCS[] = {
    FN(listlen,1,2), FN(listgetat,2,3), FN(listfirst,1,2), FN(listlast,1,2), FN(listrest,1,2),
    FN(listappend,2,3), FN(listprepend,2,3), FN(listsetat,3,4), FN(listinsertat,3,4), FN(listdeleteat,2,3),
    FN(listfind,2,3), FN(listfindnocase,2,3), FN(listcontains,2,3), FN(listcontainsnocase,2,3),
    FN(listchangedelims,2,3), FN(listtoarray,1,2), FN(arraytolist,1,2), FN(listvaluecount,2,3),
    FN(listvaluecountnocase,2,3), FN(listqualify,2,4), FN(listsort,2,4), FN(arraysort,2,3),
    FN(len,1,1), FN(left,2,2), FN(right,2,2), FN(mid,3,3), FN(ucase,1,1), FN(lcase,1,1), FN(trim,1,1),
    FN(ltrim,1,1), FN(rtrim,1,1), FN(find,2,3), FN(findnocase,2,3), FN(findoneof,2,3), FN(replace,3,4),
    FN(replacenocase,3,4), FN(replacelist,3,3), FN(removechars,3,3), FN(repeatstring,2,2), FN(reverse,1,1),
    FN(spanincluding,2,2), FN(spanexcluding,2,2), FN(gettoken,2,3), FN(asc,1,1), FN(chr,1,1), FN(val,1,1),
    FN(compare,2,2), FN(comparenocase,2,2), FN(stripcr,1,1), FN(insert,3,3), FN(ljustify,2,2),
    FN(cjustify,2,2), FN(rjustify,2,2), FN(paragraphformat,1,1), FN(wrap,2,3), FN(htmleditformat,1,2),
    FN(htmlcodeformat,1,2), FN(urlencodedformat,1,2), FN(urldecode,1,2), FN(jsstringformat,1,1),
    FN(xmlformat,1,1), FN(hash,1,1), FN(encrypt,2,2), FN(decrypt,2,2), FN(tobase64,1,1), FN(tobinary,1,1),
    FN(tostring,1,1), FN(refind,2,4), FN(refindnocase,2,4), FN(rereplace,3,4), FN(rereplacenocase,3,4),
    FN(dateformat,1,2), FN(timeformat,1,2), FN(numberformat,1,2), FN(decimalformat,1,1), FN(dollarformat,1,1),
    FN(lscurrencyformat,1,2), FN(lseurocurrencyformat,1,2), FN(yesnoformat,1,1),
    {"lsdateformat", fn_dateformat, 1, 2}, {"lstimeformat", fn_timeformat, 1, 2},
    {"lsnumberformat", fn_numberformat, 1, 2}, {"lsparsedatetime", fn_parsedatetime, 1, 1},
    {"lsisdate", fn_isdate, 1, 1}, FN(lsisnumeric,1,1), FN(lsparsenumber,1,1), FN(lsiscurrency,1,2),
    FN(lsparsecurrency,1,2), {"lsparseeurocurrency", fn_lsparsecurrency, 1, 1},
    FN(arraynew,1,1), FN(arraylen,1,1), FN(arrayappend,2,2), FN(arrayprepend,2,2), FN(arrayinsertat,3,3),
    FN(arraydeleteat,2,2), FN(arrayset,4,4), FN(arrayresize,2,2), FN(arrayclear,1,1), FN(arrayisempty,1,1),
    FN(arrayswap,3,3), FN(arraysum,1,1), FN(arrayavg,1,1), FN(arraymin,1,1), FN(arraymax,1,1), FN(isarray,1,2),
    FN(structnew,0,0), FN(isstruct,1,1), FN(structinsert,3,4), FN(structupdate,3,3), FN(structdelete,2,3),
    FN(structfind,2,2), FN(structkeyexists,2,2), FN(structkeylist,1,2), FN(structkeyarray,1,1),
    FN(structcount,1,1), FN(structclear,1,1), FN(structisempty,1,1), FN(structcopy,1,1), FN(duplicate,1,1),
    FN(structappend,2,3), FN(structget,1,1),
    FN(querynew,1,1), FN(queryaddrow,1,2), FN(querysetcell,3,4), FN(queryaddcolumn,3,3), FN(isquery,1,1),
    FN(valuelist,1,2), FN(quotedvaluelist,1,2),
    FN(now,0,0), FN(createdate,3,3), FN(createtime,3,3), FN(createdatetime,6,6), FN(createodbcdate,1,1),
    FN(createodbctime,1,1), FN(createodbcdatetime,1,1), FN(createtimespan,4,4), FN(datepart,2,2),
    FN(dateadd,3,3), FN(datediff,3,3), FN(datecompare,2,3), FN(dateconvert,2,2), FN(year,1,1), FN(month,1,1),
    FN(day,1,1), FN(hour,1,1), FN(minute,1,1), FN(second,1,1), FN(dayofweek,1,1), FN(dayofyear,1,1),
    FN(quarter,1,1), FN(week,1,1), FN(dayofweekasstring,1,1), FN(monthasstring,1,1), FN(daysinmonth,1,1),
    FN(daysinyear,1,1), FN(firstdayofmonth,1,1), FN(isdate,1,1), FN(isnumericdate,1,1), FN(isleapyear,1,1),
    FN(parsedatetime,1,2), FN(gethttptimestring,0,1), FN(gettimezoneinfo,0,0),
    FN(abs,1,1), FN(ceiling,1,1), FN(int,1,1), FN(fix,1,1), FN(round,1,1), FN(sgn,1,1), FN(exp,1,1),
    FN(sin,1,1), FN(cos,1,1), FN(tan,1,1), FN(atn,1,1), FN(asin,1,1), FN(acos,1,1), FN(sqr,1,1), FN(log,1,1),
    FN(log10,1,1), FN(pi,0,0), FN(min,2,2), FN(max,2,2), FN(rand,0,0), FN(randomize,1,1), FN(randrange,2,2),
    FN(incrementvalue,1,1), FN(decrementvalue,1,1), FN(bitand,2,2), FN(bitor,2,2), FN(bitxor,2,2),
    FN(bitnot,1,1), FN(bitshln,2,2), FN(bitshrn,2,2), FN(bitmaskread,3,3), FN(bitmaskset,4,4),
    FN(bitmaskclear,3,3), FN(formatbasen,2,2), FN(inputbasen,2,2),
    FN(isdefined,1,1), FN(parameterexists,1,1), FN(issimplevalue,1,1), FN(isnumeric,1,1), FN(isboolean,1,1),
    FN(isbinary,1,1), FN(isdebugmode,0,0), FN(iswddx,1,1),
    FN(evaluate,1,-1), FN(de,1,1), FN(iif,3,3), FN(setvariable,2,2), FN(preservesinglequotes,1,1),
    FN(writeoutput,1,1), FN(createuuid,0,0), FN(gettickcount,0,0), FN(getbasetemplatepath,0,0),
    {"gettemplatepath", fn_getbasetemplatepath, 0, 0}, FN(getcurrenttemplatepath,0,0),
    FN(getdirectoryfrompath,1,1), FN(getfilefrompath,1,1), FN(expandpath,1,1), FN(fileexists,1,1),
    FN(directoryexists,1,1), FN(gettempdirectory,0,0), FN(gettempfile,2,2), FN(getbasetaglist,0,0),
    FN(getbasetagdata,1,2), FN(getprofilestring,3,3), FN(setprofilestring,4,4), FN(getmetricdata,1,1),
    FN(getclientvariableslist,0,0), FN(deleteclientvariable,1,1), FN(setlocale,1,1), FN(getlocale,0,0),
    FN(createobject,1,-1), FN(javacast,2,2), FN(getfunctionlist,0,0),
    FN(isauthenticated,0,1), FN(isauthorized,2,3), FN(isprotected,2,3), FN(authenticateduser,0,0),
    FN(authenticatedcontext,0,0),
    {NULL, NULL, 0, 0}
};

extern const FuncDef ADMIN_FUNCS[];
extern const FuncDef FUNCS3[];        /* func3.c */
BuiltinFn func_lookup(const char *name, int *minargs, int *maxargs) {
    for (int i = 0; FUNCS3[i].name; i++)
        if (!kf_stricmp(FUNCS3[i].name, name)) { *minargs = FUNCS3[i].minargs; *maxargs = FUNCS3[i].maxargs; return FUNCS3[i].fn; }
    if (!kf_strnicmp(name, "kfusion_", 8)) {
        for (int i = 0; ADMIN_FUNCS[i].name; i++)
            if (!kf_stricmp(ADMIN_FUNCS[i].name, name)) { *minargs = ADMIN_FUNCS[i].minargs; *maxargs = ADMIN_FUNCS[i].maxargs; return ADMIN_FUNCS[i].fn; }
        return NULL;
    }
    for (int i = 0; FUNCS[i].name; i++) {
        if (!kf_stricmp(FUNCS[i].name, name)) {
            *minargs = FUNCS[i].minargs; *maxargs = FUNCS[i].maxargs;
            return FUNCS[i].fn;
        }
    }
    return NULL;
}

int func_is_lazy(BuiltinFn fn) {
    return fn == fn_parameterexists || fn == fn_valuelist || fn == fn_quotedvaluelist;
}

Query *func_list_all(void) {
    const char *cols[] = {"Name", "MinArgs", "MaxArgs"};
    Query *q = query_new(3, cols);
    for (int i = 0; FUNCS[i].name; i++) {
        int r = query_add_row(q);
        query_set(q, 0, r, v_strdup(FUNCS[i].name));
        query_set(q, 1, r, v_num(FUNCS[i].minargs));
        query_set(q, 2, r, v_num(FUNCS[i].maxargs));
    }
    for (int i = 0; FUNCS3[i].name; i++) {
        if (!kf_strnicmp(FUNCS3[i].name, "kfusion_", 8)) continue;
        int r = query_add_row(q);
        query_set(q, 0, r, v_strdup(FUNCS3[i].name));
        query_set(q, 1, r, v_num(FUNCS3[i].minargs));
        query_set(q, 2, r, v_num(FUNCS3[i].maxargs));
    }
    return q;
}
