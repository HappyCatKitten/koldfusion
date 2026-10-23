/*
 * KoldFusion Application Server 4.5
 * Copyright (c) 1995-1999 Gibson Mainframe Co. All rights reserved. (not really)
 *
 * kf.h - core types shared by every module: arenas, strings, values,
 *        structures, arrays and query objects.
 */
#ifndef KF_H
#define KF_H

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>

#define KF_PRODUCT       "KoldFusion"
#define KF_VENDOR        "Gibson"
#define KF_VERSION       "4, 5, 1, 2"
#define KF_VERSION_STR   "4.5.1 SP2"
#define KF_EDITION       "Enterprise"
#define KF_BUILD         "4.5.1.2001"
#define KF_REG_ROOT      "HKEY_LOCAL_MACHINE\\SOFTWARE\\Gibson\\KoldFusion\\CurrentVersion"

/* ------------------------------------------------------------------ arena */
/* Every request runs inside its own arena. Nothing allocated from an arena
 * is ever freed individually; the whole arena goes away when the request
 * (or scheduled task, or template cache entry) is done. */
typedef struct Arena Arena;
Arena  *arena_new(void);
void    arena_free(Arena *a);
void   *arena_alloc(Arena *a, size_t n);          /* zeroed */
size_t  arena_used(Arena *a);
void    arena_set_limit(Arena *a, size_t bytes);  /* 0 = unlimited */
Arena  *arena_new_shared(void);                   /* mutex-protected, for shared scopes */


extern __thread Arena *g_arena;                   /* current thread's arena */
void   *kmalloc(size_t n);                        /* zeroed, from g_arena */
char   *kstrdup(const char *s);
char   *kstrndup(const char *s, size_t n);
char   *kprintf(const char *fmt, ...) __attribute__((format(printf, 1, 2)));
char   *kvprintf(const char *fmt, va_list ap);

/* ------------------------------------------------------------ string buf */
typedef struct Buf { char *s; size_t len, cap; } Buf;
void  buf_init(Buf *b);
void  buf_putc(Buf *b, char c);
void  buf_put(Buf *b, const char *s, size_t n);
void  buf_puts(Buf *b, const char *s);
void  buf_printf(Buf *b, const char *fmt, ...) __attribute__((format(printf, 2, 3)));
char *buf_cstr(Buf *b);                           /* NUL-terminated, never NULL */

/* --------------------------------------------------------------- values */
typedef enum {
    VT_NULL = 0, VT_STR, VT_NUM, VT_BOOL, VT_DATE,
    VT_ARRAY, VT_STRUCT, VT_QUERY, VT_BINARY
} VType;

typedef struct Array  Array;
typedef struct Struct Struct;
typedef struct Query  Query;

typedef struct Val {
    VType t;
    union {
        double n;                                 /* VT_NUM, VT_DATE (OLE days) */
        int    b;                                 /* VT_BOOL */
        struct { const char *s; size_t len; } str;/* VT_STR, VT_BINARY */
        Array  *a;
        Struct *st;
        Query  *q;
    } u;
} Val;

Val v_null(void);
Val v_str(const char *s);                         /* copies nothing: s must live in arena */
Val v_strn(const char *s, size_t n);
Val v_strdup(const char *s);                      /* copies into arena */
Val v_num(double n);
Val v_bool(int b);
Val v_date(double d);
Val v_arr(Array *a);
Val v_struct(Struct *s);
Val v_query(Query *q);
Val v_binary(const char *p, size_t n);

int  v_is_simple(Val v);                          /* str/num/bool/date/null */
const char *v_tostr(Val v);                       /* never NULL, simple values only */
size_t v_strlen(Val v);
int  v_tonum(Val v, double *out);                 /* 1 if numeric */
int  v_tobool(Val v, int *out);                   /* 1 if boolean-convertible */
int  v_todate(Val v, double *out);                /* 1 if date-convertible */
int  v_isnumeric_str(const char *s, double *out);
const char *v_typename(Val v);
char *fmt_number(double n);                       /* CF 4.5 style number display */

/* compare: returns <0,0,>0. numeric/date compare if both convertible, else
 * case-insensitive string compare */
int  v_compare(Val a, Val b);
int  v_compare_nocase_str(const char *a, const char *b);

/* ------------------------------------------------------------ structures */
typedef struct SEnt { const char *key; Val v; } SEnt;
struct Struct {
    Arena *arena;                                  /* owning arena for growth (NULL = g_arena) */
    int n, cap;
    SEnt *e;
    int *idx; int idxcap;                          /* open addressing, -1 empty */
};
Struct *struct_new(void);
Val    *struct_get(Struct *s, const char *key);    /* case-insensitive, NULL if absent */
void    struct_set(Struct *s, const char *key, Val v);
int     struct_delete(Struct *s, const char *key);
void    struct_clear(Struct *s);
Struct *struct_copy(Struct *s, int deep);

/* --------------------------------------------------------------- arrays */
struct Array { Arena *arena; int n, cap; Val *v; int dims; };
Array *array_new(void);
void   array_push(Array *a, Val v);
void   array_set(Array *a, int idx1, Val v);       /* 1-based, grows */
Val   *array_get(Array *a, int idx1);              /* 1-based, NULL if out of range */
void   array_insert(Array *a, int idx1, Val v);
void   array_delete(Array *a, int idx1);
void   array_resize(Array *a, int n);
Array *array_copy(Array *a, int deep);

Val v_deepcopy(Val v);
/* deep copy v into arena a (used when storing into Session/Application) */
Val v_copy_into(Arena *a, Val v);

/* -------------------------------------------------------------- queries */
struct Query {
    int    ncols, nrows, rowcap;
    char **cols;                                   /* column names as given */
    Val  **data;                                   /* data[col][row], rows 0-based */
    int    currentrow;                             /* 1-based; 0 when not looping */
    /* debug info */
    const char *name, *sql, *datasource;
    double exectime_ms;
    int    cached;
};
Query *query_new(int ncols, const char **names);
int    query_add_column(Query *q, const char *name);   /* returns col index */
int    query_add_row(Query *q);                        /* returns new 0-based row */
void   query_set(Query *q, int col, int row, Val v);
Val    query_get(Query *q, int col, int row);
int    query_col_index(Query *q, const char *name);    /* -1 if none */
const char *query_column_list(Query *q);               /* "A,B,C" uppercased */
Query *query_copy(Query *q);

/* ------------------------------------------------------------- dates */
/* Dates are OLE automation dates: days since 1899-12-30, fractional = time */
double date_from_parts(int y, int mo, int d, int h, int mi, int s);
void   date_to_parts(double dt, int *y, int *mo, int *d, int *h, int *mi, int *s);
int    date_dow(double dt);                            /* 1 = Sunday */
double date_now(void);
double date_local_to_utc(double dt);
double date_utc_to_local(double dt);
int    date_parse(const char *s, double *out);         /* 1 on success */
char  *date_odbc(double dt);                           /* {ts '1999-10-22 21:42:00'} */
int    days_in_month(int y, int m);
int    is_leap(int y);

/* ------------------------------------------------------------- utils */
int    kf_stricmp(const char *a, const char *b);
int    kf_strnicmp(const char *a, const char *b, size_t n);
const char *kf_stristr(const char *hay, const char *needle);
char  *kf_upper(const char *s);
char  *kf_lower(const char *s);
char  *kf_trim(const char *s);
uint32_t kf_hash_nocase(const char *s);
int    kf_is_ident_start(int c);
int    kf_is_ident_char(int c);
char  *kf_read_file(const char *path, size_t *len);    /* malloc'd, caller frees */
int    kf_write_file(const char *path, const char *data, size_t len, int append);
int    kf_mkdirs(const char *path);
char  *kf_path_join(const char *a, const char *b);     /* arena */
double kf_time_ms(void);                               /* monotonic ms */
char  *kf_resolve_ci(const char *path);                 /* case-insensitive existing path or NULL */
char  *kf_native_path(const char *p);                   /* map C:\\... paths into the install */

#endif
