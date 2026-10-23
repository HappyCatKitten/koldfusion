/*
 * core.c - arenas, buffers, values, structs, arrays, queries, dates, utils
 */
#define _GNU_SOURCE
#include "kf.h"
#include <stdlib.h>
#include <ctype.h>
#include <math.h>
#include <time.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>

/* ================================================================ arena */
#define CHUNK_MIN (64 * 1024)

typedef struct Chunk { struct Chunk *next; size_t size, used; char data[]; } Chunk;
#include <pthread.h>
typedef struct Cleanup { void (*fn)(void *); void *arg; struct Cleanup *next; } Cleanup;
struct Arena { Chunk *head; size_t total; size_t limit; int shared; pthread_mutex_t mu; Cleanup *cleanups; };

__thread Arena *g_arena;

extern void kf_out_of_memory(void);   /* interp.c: throws a CF error */

Arena *arena_new(void) {
    Arena *a = calloc(1, sizeof *a);
    return a;
}
Arena *arena_new_shared(void) {
    Arena *a = calloc(1, sizeof *a);
    a->shared = 1;
    pthread_mutex_init(&a->mu, NULL);
    return a;
}

/* external resources (Java object references) that live as long as the arena */
void arena_on_free(Arena *a, void (*fn)(void *), void *arg) {
    if (!a) return;
    Cleanup *c = arena_alloc(a, sizeof *c);
    c->fn = fn; c->arg = arg;
    if (a->shared) pthread_mutex_lock(&a->mu);
    c->next = a->cleanups; a->cleanups = c;
    if (a->shared) pthread_mutex_unlock(&a->mu);
}

void arena_free(Arena *a) {
    if (!a) return;
    for (Cleanup *k = a->cleanups; k; k = k->next) k->fn(k->arg);
    Chunk *c = a->head;
    while (c) { Chunk *n = c->next; free(c); c = n; }
    if (a->shared) pthread_mutex_destroy(&a->mu);
    free(a);
}

size_t arena_used(Arena *a) { return a ? a->total : 0; }
void arena_set_limit(Arena *a, size_t bytes) { a->limit = bytes; }

static void *arena_alloc_unlocked(Arena *a, size_t n);
void *arena_alloc(Arena *a, size_t n) {
    if (a && a->shared) {
        pthread_mutex_lock(&a->mu);
        void *p = arena_alloc_unlocked(a, n);
        pthread_mutex_unlock(&a->mu);
        return p;
    }
    return arena_alloc_unlocked(a, n);
}
static void *arena_alloc_unlocked(Arena *a, size_t n) {
    n = (n + 15) & ~(size_t)15;
    if (!a) { void *p = calloc(1, n ? n : 1); return p; }
    Chunk *c = a->head;
    if (!c || c->used + n > c->size) {
        size_t sz = n > CHUNK_MIN ? n : CHUNK_MIN;
        if (c && c->size * 2 > sz && c->size < 8 * 1024 * 1024) sz = c->size * 2 > n ? c->size * 2 : sz;
        if (a->limit && a->total + sz > a->limit) {
            a->limit = 0;                 /* allow the error page to render */
            if (a->shared) pthread_mutex_unlock(&a->mu);
            kf_out_of_memory();
        }
        Chunk *nc = malloc(sizeof(Chunk) + sz);
        if (!nc) { fprintf(stderr, "KoldFusion: out of memory\n"); abort(); }
        nc->size = sz; nc->used = 0; nc->next = a->head;
        a->head = nc; a->total += sz;
        c = nc;
    }
    void *p = c->data + c->used;
    c->used += n;
    memset(p, 0, n);
    return p;
}

void *kmalloc(size_t n) { return arena_alloc(g_arena, n); }

char *kstrndup(const char *s, size_t n) {
    char *p = kmalloc(n + 1);
    if (n) memcpy(p, s, n);
    p[n] = 0;
    return p;
}
char *kstrdup(const char *s) { return kstrndup(s ? s : "", s ? strlen(s) : 0); }

char *kvprintf(const char *fmt, va_list ap) {
    va_list ap2; va_copy(ap2, ap);
    char tmp[512];
    int n = vsnprintf(tmp, sizeof tmp, fmt, ap);
    if (n < (int)sizeof tmp) { va_end(ap2); return kstrndup(tmp, n); }
    char *p = kmalloc(n + 1);
    vsnprintf(p, n + 1, fmt, ap2);
    va_end(ap2);
    return p;
}
char *kprintf(const char *fmt, ...) {
    va_list ap; va_start(ap, fmt);
    char *r = kvprintf(fmt, ap);
    va_end(ap);
    return r;
}

/* ================================================================== buf */
void buf_init(Buf *b) { b->s = NULL; b->len = b->cap = 0; }
static void buf_grow(Buf *b, size_t need) {
    if (b->len + need + 1 <= b->cap) return;
    size_t nc = b->cap ? b->cap * 2 : 64;
    while (nc < b->len + need + 1) nc *= 2;
    char *ns = kmalloc(nc);
    if (b->len) memcpy(ns, b->s, b->len);
    b->s = ns; b->cap = nc;
}
void buf_putc(Buf *b, char c) { buf_grow(b, 1); b->s[b->len++] = c; b->s[b->len] = 0; }
void buf_put(Buf *b, const char *s, size_t n) {
    if (!n) return;
    buf_grow(b, n); memcpy(b->s + b->len, s, n); b->len += n; b->s[b->len] = 0;
}
void buf_puts(Buf *b, const char *s) { if (s) buf_put(b, s, strlen(s)); }
void buf_printf(Buf *b, const char *fmt, ...) {
    va_list ap; va_start(ap, fmt);
    char *s = kvprintf(fmt, ap);
    va_end(ap);
    buf_puts(b, s);
}
char *buf_cstr(Buf *b) { if (!b->s) { buf_grow(b, 0); b->s[0] = 0; } return b->s; }

/* =============================================================== values */
Val v_null(void) { Val v; memset(&v, 0, sizeof v); return v; }
Val v_strn(const char *s, size_t n) { Val v; v.t = VT_STR; v.u.str.s = s ? s : ""; v.u.str.len = s ? n : 0; return v; }
Val v_str(const char *s) { return v_strn(s, s ? strlen(s) : 0); }
Val v_strdup(const char *s) { size_t n = s ? strlen(s) : 0; return v_strn(kstrndup(s ? s : "", n), n); }
Val v_num(double n) { Val v; v.t = VT_NUM; v.u.n = n; return v; }
Val v_bool(int b) { Val v; v.t = VT_BOOL; v.u.b = b ? 1 : 0; return v; }
Val v_date(double d) { Val v; v.t = VT_DATE; v.u.n = d; return v; }
Val v_arr(Array *a) { Val v; v.t = VT_ARRAY; v.u.a = a; return v; }
Val v_struct(Struct *s) { Val v; v.t = VT_STRUCT; v.u.st = s; return v; }
Val v_query(Query *q) { Val v; v.t = VT_QUERY; v.u.q = q; return v; }
Val v_binary(const char *p, size_t n) { Val v; v.t = VT_BINARY; v.u.str.s = p; v.u.str.len = n; return v; }
Val v_object(KfObject *o) { Val v; memset(&v, 0, sizeof v); v.t = VT_OBJECT; v.u.obj = o; return v; }

int v_is_simple(Val v) { return v.t <= VT_DATE; }

const char *v_typename(Val v) {
    switch (v.t) {
    case VT_NULL: return "null"; case VT_STR: return "string"; case VT_NUM: return "number";
    case VT_BOOL: return "boolean"; case VT_DATE: return "date"; case VT_ARRAY: return "array";
    case VT_STRUCT: return "structure"; case VT_QUERY: return "query"; case VT_BINARY: return "binary";
    case VT_OBJECT: return "object";
    }
    return "unknown";
}

/* CF 4.5 displayed numbers with up to 12 significant digits and never used
 * exponent notation for ordinary magnitudes. */
char *fmt_number(double n) {
    if (isnan(n)) return kstrdup("NaN");
    if (isinf(n)) return kstrdup(n > 0 ? "INF" : "-INF");
    if (n == floor(n) && fabs(n) < 1e15) {
        if (n == 0) return kstrdup("0");
        return kprintf("%.0f", n);
    }
    char tmp[64];
    double a = fabs(n);
    if (a >= 1e15 || a < 1e-10) {
        snprintf(tmp, sizeof tmp, "%.11E", n);
        /* trim mantissa zeros: 1.50000000000E+020 -> 1.5E+020 */
        char *e = strchr(tmp, 'E');
        char *m = e - 1;
        while (m > tmp && *m == '0') m--;
        if (*m == '.') m++;
        char out[64];
        size_t ml = (size_t)(m - tmp + 1);
        memcpy(out, tmp, ml); out[ml] = 0;
        int ex = atoi(e + 1);
        snprintf(out + ml, sizeof out - ml, "E%c%03d", ex < 0 ? '-' : '+', abs(ex));
        return kstrdup(out);
    }
    snprintf(tmp, sizeof tmp, "%.12g", n);
    if (strchr(tmp, 'e')) snprintf(tmp, sizeof tmp, "%.12f", n);
    if (strchr(tmp, '.')) {
        char *e = tmp + strlen(tmp) - 1;
        while (*e == '0') *e-- = 0;
        if (*e == '.') *e = 0;
    }
    return kstrdup(tmp);
}

const char *v_tostr(Val v) {
    switch (v.t) {
    case VT_NULL: return "";
    case VT_STR: case VT_BINARY: return v.u.str.s;
    case VT_NUM: return fmt_number(v.u.n);
    case VT_BOOL: return v.u.b ? "YES" : "NO";
    case VT_DATE: return date_odbc(v.u.n);
    default: return "";
    }
}
size_t v_strlen(Val v) {
    if (v.t == VT_STR || v.t == VT_BINARY) return v.u.str.len;
    return strlen(v_tostr(v));
}

int v_isnumeric_str(const char *s, double *out) {
    while (*s == ' ' || *s == '\t' || *s == '\n' || *s == '\r') s++;
    if (!*s) return 0;
    const char *p = s;
    if (*p == '+' || *p == '-') p++;
    int digits = 0;
    while (isdigit((unsigned char)*p)) { p++; digits++; }
    if (*p == '.') { p++; while (isdigit((unsigned char)*p)) { p++; digits++; } }
    if (!digits) return 0;
    if (*p == 'e' || *p == 'E') {
        const char *q = p + 1;
        if (*q == '+' || *q == '-') q++;
        if (isdigit((unsigned char)*q)) { while (isdigit((unsigned char)*q)) q++; p = q; }
    }
    while (*p == ' ' || *p == '\t' || *p == '\n' || *p == '\r') p++;
    if (*p) return 0;
    if (out) *out = strtod(s, NULL);
    return 1;
}

int v_tonum(Val v, double *out) {
    switch (v.t) {
    case VT_NUM: case VT_DATE: *out = v.u.n; return 1;
    case VT_BOOL: *out = v.u.b; return 1;
    case VT_STR: {
        if (v_isnumeric_str(v.u.str.s, out)) return 1;
        const char *s = v.u.str.s;
        if (!kf_stricmp(s, "yes") || !kf_stricmp(s, "true")) { *out = 1; return 1; }
        if (!kf_stricmp(s, "no") || !kf_stricmp(s, "false")) { *out = 0; return 1; }
        return 0;
    }
    default: return 0;
    }
}

int v_tobool(Val v, int *out) {
    switch (v.t) {
    case VT_BOOL: *out = v.u.b; return 1;
    case VT_NUM: case VT_DATE: *out = v.u.n != 0; return 1;
    case VT_STR: {
        const char *s = v.u.str.s; double d;
        while (*s == ' ') s++;
        if (!kf_stricmp(s, "yes") || !kf_stricmp(s, "true")) { *out = 1; return 1; }
        if (!kf_stricmp(s, "no") || !kf_stricmp(s, "false")) { *out = 0; return 1; }
        if (v_isnumeric_str(s, &d)) { *out = d != 0; return 1; }
        return 0;
    }
    default: return 0;
    }
}

int v_todate(Val v, double *out) {
    switch (v.t) {
    case VT_DATE: case VT_NUM: *out = v.u.n; return 1;
    case VT_STR: return v_isnumeric_str(v.u.str.s, out) || date_parse(v.u.str.s, out);
    default: return 0;
    }
}

int v_compare_nocase_str(const char *a, const char *b) {
    for (;; a++, b++) {
        int ca = tolower((unsigned char)*a), cb = tolower((unsigned char)*b);
        if (ca != cb || !ca) return ca - cb;
    }
}

int v_compare(Val a, Val b) {
    double x, y;
    int an = (a.t == VT_NUM || a.t == VT_BOOL || (a.t == VT_STR && v_isnumeric_str(a.u.str.s, NULL)));
    int bn = (b.t == VT_NUM || b.t == VT_BOOL || (b.t == VT_STR && v_isnumeric_str(b.u.str.s, NULL)));
    if (an && bn && v_tonum(a, &x) && v_tonum(b, &y)) return x < y ? -1 : x > y ? 1 : 0;
    if ((a.t == VT_DATE || b.t == VT_DATE) && v_todate(a, &x) && v_todate(b, &y))
        return x < y ? -1 : x > y ? 1 : 0;
    if (a.t == VT_BOOL || b.t == VT_BOOL) {
        int p, q;
        if (v_tobool(a, &p) && v_tobool(b, &q)) return p - q;
    }
    const char *sa = v_tostr(a), *sb = v_tostr(b);
    /* two strings that are both dates compare as dates ("10/22/1999" EQ "1999-10-22") */
    if (a.t == VT_STR && b.t == VT_STR && strpbrk(sa, "0123456789") && strpbrk(sb, "0123456789") &&
        strpbrk(sa, "/-:, ") && strpbrk(sb, "/-:, ") && v_compare_nocase_str(sa, sb) &&
        date_parse(sa, &x) && date_parse(sb, &y))
        return x < y ? -1 : x > y ? 1 : 0;
    return v_compare_nocase_str(sa, sb);
}

/* ============================================================== struct */
uint32_t kf_hash_nocase(const char *s) {
    uint32_t h = 2166136261u;
    for (; *s; s++) { h ^= (uint32_t)toupper((unsigned char)*s); h *= 16777619u; }
    return h;
}

Struct *struct_new(void) { Struct *s = kmalloc(sizeof(Struct)); s->arena = g_arena; return s; }

#define WITH_ARENA(ar, body) do { Arena *_sv = g_arena; if (ar) g_arena = (ar); body; g_arena = _sv; } while (0)

Val v_copy_into(Arena *a, Val v) {
    Val r;
    WITH_ARENA(a, r = v_deepcopy(v));
    return r;
}

static void struct_reindex(Struct *s) {
    int cap = 16;
    while (cap < s->n * 2 + 2) cap *= 2;
    int *ni;
    WITH_ARENA(s->arena, ni = kmalloc(sizeof(int) * cap));
    s->idx = ni;
    s->idxcap = cap;
    for (int i = 0; i < cap; i++) s->idx[i] = -1;
    for (int i = 0; i < s->n; i++) {
        uint32_t h = kf_hash_nocase(s->e[i].key) & (cap - 1);
        while (s->idx[h] >= 0) h = (h + 1) & (cap - 1);
        s->idx[h] = i;
    }
}

static int struct_find(Struct *s, const char *key) {
    if (!s->n) return -1;
    if (s->n < 8) {
        for (int i = 0; i < s->n; i++) if (!kf_stricmp(s->e[i].key, key)) return i;
        return -1;
    }
    if (!s->idx || s->idxcap < s->n * 2) struct_reindex(s);
    uint32_t h = kf_hash_nocase(key) & (s->idxcap - 1);
    while (s->idx[h] >= 0) {
        int i = s->idx[h];
        if (!kf_stricmp(s->e[i].key, key)) return i;
        h = (h + 1) & (s->idxcap - 1);
    }
    return -1;
}

Val *struct_get(Struct *s, const char *key) {
    if (!s) return NULL;
    int i = struct_find(s, key);
    return i < 0 ? NULL : &s->e[i].v;
}

void struct_set(Struct *s, const char *key, Val v) {
    /* storing into a container owned by another (longer-lived) arena:
     * deep copy so the value outlives the current request */
    if (s->arena && s->arena != g_arena) v = v_copy_into(s->arena, v);
    int i = struct_find(s, key);
    if (i >= 0) { s->e[i].v = v; return; }
    if (s->n == s->cap) {
        int nc = s->cap ? s->cap * 2 : 8;
        SEnt *ne;
        WITH_ARENA(s->arena, ne = kmalloc(sizeof(SEnt) * nc));
        if (s->n) memcpy(ne, s->e, sizeof(SEnt) * s->n);
        s->e = ne; s->cap = nc;
    }
    const char *k;
    WITH_ARENA(s->arena, k = kstrdup(key));
    s->e[s->n].key = k;
    s->e[s->n].v = v;
    __sync_synchronize();
    s->n++;
    if (s->idx) {
        if (s->idxcap < s->n * 2) struct_reindex(s);
        else {
            uint32_t h = kf_hash_nocase(key) & (s->idxcap - 1);
            while (s->idx[h] >= 0) h = (h + 1) & (s->idxcap - 1);
            s->idx[h] = s->n - 1;
        }
    }
}

int struct_delete(Struct *s, const char *key) {
    int i = struct_find(s, key);
    if (i < 0) return 0;
    memmove(&s->e[i], &s->e[i + 1], sizeof(SEnt) * (s->n - i - 1));
    s->n--;
    s->idx = NULL; s->idxcap = 0;
    return 1;
}

void struct_clear(Struct *s) { s->n = 0; s->idx = NULL; s->idxcap = 0; }

Struct *struct_copy(Struct *s, int deep) {
    Struct *r = struct_new();
    for (int i = 0; i < s->n; i++) {
        Val v = s->e[i].v;
        if (deep) v = v_deepcopy(v);
        else if (v.t == VT_ARRAY) v = v_arr(array_copy(v.u.a, 0));   /* StructCopy: arrays by value */
        struct_set(r, s->e[i].key, v);
    }
    return r;
}

/* =============================================================== array */
Array *array_new(void) { Array *a = kmalloc(sizeof(Array)); a->arena = g_arena; return a; }
static void array_reserve(Array *a, int n) {
    if (n <= a->cap) return;
    int nc = a->cap ? a->cap * 2 : 8;
    while (nc < n) nc *= 2;
    Val *nv;
    WITH_ARENA(a->arena, nv = kmalloc(sizeof(Val) * nc));
    if (a->n) memcpy(nv, a->v, sizeof(Val) * a->n);
    a->v = nv; a->cap = nc;
}
#define ARR_OWN(a, v) do { if ((a)->arena && (a)->arena != g_arena) v = v_copy_into((a)->arena, v); } while (0)
void array_push(Array *a, Val v) { ARR_OWN(a, v); array_reserve(a, a->n + 1); a->v[a->n++] = v; }
void array_resize(Array *a, int n) {
    if (n < 0) n = 0;
    array_reserve(a, n);
    for (int i = a->n; i < n; i++) a->v[i] = v_null();
    a->n = n;
}
void array_set(Array *a, int idx1, Val v) {
    if (idx1 < 1) return;
    ARR_OWN(a, v);
    if (idx1 > a->n) array_resize(a, idx1);
    a->v[idx1 - 1] = v;
}
Val *array_get(Array *a, int idx1) {
    if (idx1 < 1 || idx1 > a->n) return NULL;
    return &a->v[idx1 - 1];
}
void array_insert(Array *a, int idx1, Val v) {
    if (idx1 < 1) idx1 = 1;
    if (idx1 > a->n + 1) idx1 = a->n + 1;
    ARR_OWN(a, v);
    array_reserve(a, a->n + 1);
    memmove(&a->v[idx1], &a->v[idx1 - 1], sizeof(Val) * (a->n - idx1 + 1));
    a->v[idx1 - 1] = v;
    a->n++;
}
void array_delete(Array *a, int idx1) {
    if (idx1 < 1 || idx1 > a->n) return;
    memmove(&a->v[idx1 - 1], &a->v[idx1], sizeof(Val) * (a->n - idx1));
    a->n--;
}
Array *array_copy(Array *a, int deep) {
    Array *r = array_new();
    r->dims = a->dims;
    array_reserve(r, a->n);
    for (int i = 0; i < a->n; i++) r->v[i] = deep ? v_deepcopy(a->v[i]) : a->v[i];
    r->n = a->n;
    return r;
}

Val v_deepcopy(Val v) {
    switch (v.t) {
    case VT_STR: case VT_BINARY: { char *p = kmalloc(v.u.str.len + 1); memcpy(p, v.u.str.s, v.u.str.len); v.u.str.s = p; return v; }
    case VT_ARRAY: return v_arr(array_copy(v.u.a, 1));
    case VT_STRUCT: return v_struct(struct_copy(v.u.st, 1));
    case VT_QUERY: return v_query(query_copy(v.u.q));
    case VT_OBJECT: return kfobj_copy(v);
    default: return v;
    }
}

/* =============================================================== query */
Query *query_new(int ncols, const char **names) {
    Query *q = kmalloc(sizeof(Query));
    for (int i = 0; i < ncols; i++) query_add_column(q, names[i]);
    return q;
}

int query_add_column(Query *q, const char *name) {
    int i = query_col_index(q, name);
    if (i >= 0) return i;
    char **nc = kmalloc(sizeof(char *) * (q->ncols + 1));
    Val **nd = kmalloc(sizeof(Val *) * (q->ncols + 1));
    if (q->ncols) { memcpy(nc, q->cols, sizeof(char *) * q->ncols); memcpy(nd, q->data, sizeof(Val *) * q->ncols); }
    nc[q->ncols] = kstrdup(name);
    nd[q->ncols] = kmalloc(sizeof(Val) * (q->rowcap ? q->rowcap : 1));
    for (int r = 0; r < q->nrows; r++) nd[q->ncols][r] = v_str("");
    q->cols = nc; q->data = nd;
    return q->ncols++;
}

int query_add_row(Query *q) {
    if (q->nrows == q->rowcap) {
        int nc = q->rowcap ? q->rowcap * 2 : 16;
        for (int c = 0; c < q->ncols; c++) {
            Val *nd = kmalloc(sizeof(Val) * nc);
            if (q->nrows) memcpy(nd, q->data[c], sizeof(Val) * q->nrows);
            q->data[c] = nd;
        }
        q->rowcap = nc;
    }
    for (int c = 0; c < q->ncols; c++) q->data[c][q->nrows] = v_str("");
    return q->nrows++;
}

void query_set(Query *q, int col, int row, Val v) {
    if (col < 0 || col >= q->ncols || row < 0 || row >= q->nrows) return;
    q->data[col][row] = v;
}
Val query_get(Query *q, int col, int row) {
    if (col < 0 || col >= q->ncols || row < 0 || row >= q->nrows) return v_str("");
    return q->data[col][row];
}
int query_col_index(Query *q, const char *name) {
    for (int i = 0; i < q->ncols; i++) if (!kf_stricmp(q->cols[i], name)) return i;
    return -1;
}
const char *query_column_list(Query *q) {
    Buf b; buf_init(&b);
    for (int i = 0; i < q->ncols; i++) { if (i) buf_putc(&b, ','); buf_puts(&b, kf_upper(q->cols[i])); }
    return buf_cstr(&b);
}
Query *query_copy(Query *q) {
    Query *r = query_new(0, NULL);
    for (int c = 0; c < q->ncols; c++) query_add_column(r, q->cols[c]);
    for (int i = 0; i < q->nrows; i++) {
        int row = query_add_row(r);
        for (int c = 0; c < q->ncols; c++) r->data[c][row] = v_deepcopy(q->data[c][i]);
    }
    r->name = q->name ? kstrdup(q->name) : NULL;
    r->sql = q->sql ? kstrdup(q->sql) : NULL;
    r->datasource = q->datasource ? kstrdup(q->datasource) : NULL;
    r->exectime_ms = q->exectime_ms;
    return r;
}

/* =============================================================== dates */
int is_leap(int y) { return (y % 4 == 0 && y % 100 != 0) || y % 400 == 0; }
int days_in_month(int y, int m) {
    static const int dm[] = {31,28,31,30,31,30,31,31,30,31,30,31};
    if (m < 1 || m > 12) return 30;
    return m == 2 && is_leap(y) ? 29 : dm[m - 1];
}

/* days from civil (Howard Hinnant) relative to 1970-01-01 */
static long days_from_civil(long y, unsigned m, unsigned d) {
    y -= m <= 2;
    long era = (y >= 0 ? y : y - 399) / 400;
    unsigned yoe = (unsigned)(y - era * 400);
    unsigned doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1;
    unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    return era * 146097 + (long)doe - 719468;
}
static void civil_from_days(long z, int *y, int *m, int *d) {
    z += 719468;
    long era = (z >= 0 ? z : z - 146096) / 146097;
    unsigned doe = (unsigned)(z - era * 146097);
    unsigned yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    long yy = (long)yoe + era * 400;
    unsigned doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    unsigned mp = (5 * doy + 2) / 153;
    unsigned dd = doy - (153 * mp + 2) / 5 + 1;
    unsigned mm = mp + (mp < 10 ? 3 : -9);
    *y = (int)(yy + (mm <= 2)); *m = (int)mm; *d = (int)dd;
}
#define OLE_EPOCH_OFFSET 25569L   /* days from 1899-12-30 to 1970-01-01 */

double date_from_parts(int y, int mo, int d, int h, int mi, int s) {
    /* normalise month overflow */
    while (mo > 12) { mo -= 12; y++; }
    while (mo < 1) { mo += 12; y--; }
    long days = days_from_civil(y, (unsigned)mo, 1) + (d - 1) + OLE_EPOCH_OFFSET;
    return (double)days + (h * 3600.0 + mi * 60.0 + s) / 86400.0;
}

void date_to_parts(double dt, int *y, int *mo, int *d, int *h, int *mi, int *s) {
    double fl = floor(dt);
    long days = (long)fl;
    long secs = (long)floor((dt - fl) * 86400.0 + 0.5);
    if (secs >= 86400) { secs -= 86400; days++; }
    int yy, mm, dd;
    civil_from_days(days - OLE_EPOCH_OFFSET, &yy, &mm, &dd);
    if (y) *y = yy;
    if (mo) *mo = mm;
    if (d) *d = dd;
    if (h) *h = (int)(secs / 3600);
    if (mi) *mi = (int)(secs / 60 % 60);
    if (s) *s = (int)(secs % 60);
}

int date_dow(double dt) {
    long days = (long)floor(dt);
    /* 1899-12-30 was a Saturday (7) */
    long r = ((days % 7) + 7) % 7;  /* 0 -> Saturday */
    return (int)((r + 6) % 7) + 1;
}

double date_now(void) {
    time_t t = time(NULL);
    struct tm tm; localtime_r(&t, &tm);
    return date_from_parts(tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec);
}

char *date_odbc(double dt) {
    int y, mo, d, h, mi, s;
    date_to_parts(dt, &y, &mo, &d, &h, &mi, &s);
    return kprintf("{ts '%04d-%02d-%02d %02d:%02d:%02d'}", y, mo, d, h, mi, s);
}

static const char *MONTHS[] = {"january","february","march","april","may","june","july",
                               "august","september","october","november","december"};
static int month_from_name(const char *p, int len) {
    if (len < 3) return 0;
    for (int i = 0; i < 12; i++) if (!kf_strnicmp(p, MONTHS[i], 3) && (len == 3 || !kf_strnicmp(p, MONTHS[i], len))) return i + 1;
    return 0;
}
static const char *DAYS[] = {"sunday","monday","tuesday","wednesday","thursday","friday","saturday"};

int date_parse(const char *str, double *out) {
    if (!str) return 0;
    const char *p = str;
    while (*p == ' ' || *p == '\t') p++;
    if (!*p) return 0;
    /* ODBC canonical {ts '...'} {d '...'} {t '...'} */
    if (*p == '{') {
        const char *q = strchr(p, '\'');
        if (!q) return 0;
        char tmp[64]; size_t n = 0; q++;
        while (*q && *q != '\'' && n < 63) tmp[n++] = *q++;
        tmp[n] = 0;
        return date_parse(tmp, out);
    }
    /* tokenise into numbers, words and separators */
    int nums[8]; int nn = 0; int numlen[8];
    int month = 0, hour = -1, min = 0, sec = 0, ampm = 0, have_time = 0;
    int seps_dash = 0, seps_slash = 0;
    int iso = 0;
    while (*p) {
        if (isdigit((unsigned char)*p)) {
            const char *s = p; long v = 0;
            while (isdigit((unsigned char)*p)) v = v * 10 + (*p++ - '0');
            if (*p == ':') {
                /* time */
                hour = (int)v; p++;
                if (!isdigit((unsigned char)*p)) return 0;
                min = (int)strtol(p, (char **)&p, 10);
                if (*p == ':') { p++; sec = (int)strtol(p, (char **)&p, 10); }
                if (*p == '.') { p++; while (isdigit((unsigned char)*p)) p++; }
                have_time = 1;
                continue;
            }
            if (nn >= 8) return 0;
            numlen[nn] = (int)(p - s);
            nums[nn++] = (int)v;
            if (nn == 1 && numlen[0] == 4 && *p == '-') iso = 1;
        } else if (isalpha((unsigned char)*p)) {
            const char *s = p;
            while (isalpha((unsigned char)*p)) p++;
            int len = (int)(p - s);
            int m = month_from_name(s, len);
            if (m) { if (month) return 0; month = m; continue; }
            if ((len == 2 || len == 1) && (tolower((unsigned char)*s) == 'a' || tolower((unsigned char)*s) == 'p') &&
                (len == 1 || tolower((unsigned char)s[1]) == 'm')) { ampm = tolower((unsigned char)*s) == 'a' ? 1 : 2; continue; }
            if (len == 1 && toupper((unsigned char)*s) == 'T') continue;
            int isday = 0;
            for (int i = 0; i < 7; i++) if (len >= 3 && !kf_strnicmp(s, DAYS[i], len < 3 ? 3 : (size_t)len) ) isday = 1;
            if (len == 3) for (int i = 0; i < 7; i++) if (!kf_strnicmp(s, DAYS[i], 3)) isday = 1;
            if (isday) continue;
            return 0;
        } else if (*p == '-') { seps_dash++; p++; }
        else if (*p == '/') { seps_slash++; p++; }
        else if (*p == ',' || *p == ' ' || *p == '.' || *p == '\t') p++;
        else return 0;
    }
    int y = 0, mo = 0, d = 0;
    if (month) {
        mo = month;
        if (nn == 2) {
            /* "Oct 22, 1999" or "22 Oct 1999" or "22-Oct-99" */
            if (numlen[0] == 4) { y = nums[0]; d = nums[1]; }
            else { d = nums[0]; y = nums[1]; if (numlen[1] <= 2) y += y < 30 ? 2000 : 1900; }
        } else if (nn == 1) {
            if (numlen[0] == 4) { y = nums[0]; d = 1; }
            else return 0;
        } else return 0;
    } else if (nn == 3) {
        if (iso || numlen[0] == 4) { y = nums[0]; mo = nums[1]; d = nums[2]; }
        else {
            mo = nums[0]; d = nums[1]; y = nums[2];
            if (numlen[2] <= 2) y += y < 30 ? 2000 : 1900;
        }
    } else if (nn == 0 && have_time) {
        y = 1899; mo = 12; d = 30;
    } else return 0;
    (void)seps_dash; (void)seps_slash;
    if (mo < 1 || mo > 12 || d < 1 || d > days_in_month(y, mo) || y < 100 || y > 9999) return 0;
    if (hour < 0) hour = 0;
    if (ampm == 2 && hour < 12) hour += 12;
    if (ampm == 1 && hour == 12) hour = 0;
    if (hour > 23 || min > 59 || sec > 59) return 0;
    *out = date_from_parts(y, mo, d, hour, min, sec);
    return 1;
}

/* =============================================================== utils */
int kf_stricmp(const char *a, const char *b) { return v_compare_nocase_str(a, b); }
int kf_strnicmp(const char *a, const char *b, size_t n) {
    for (size_t i = 0; i < n; i++) {
        int ca = tolower((unsigned char)a[i]), cb = tolower((unsigned char)b[i]);
        if (ca != cb || !ca) return ca - cb;
    }
    return 0;
}
const char *kf_stristr(const char *hay, const char *needle) {
    size_t n = strlen(needle);
    if (!n) return hay;
    for (; *hay; hay++) if (!kf_strnicmp(hay, needle, n)) return hay;
    return NULL;
}
char *kf_upper(const char *s) { char *r = kstrdup(s); for (char *p = r; *p; p++) *p = (char)toupper((unsigned char)*p); return r; }
char *kf_lower(const char *s) { char *r = kstrdup(s); for (char *p = r; *p; p++) *p = (char)tolower((unsigned char)*p); return r; }
char *kf_trim(const char *s) {
    while (*s && isspace((unsigned char)*s)) s++;
    size_t n = strlen(s);
    while (n && isspace((unsigned char)s[n - 1])) n--;
    return kstrndup(s, n);
}
int kf_is_ident_start(int c) { return isalpha(c) || c == '_'; }
int kf_is_ident_char(int c) { return isalnum(c) || c == '_'; }

char *kf_read_file(const char *path, size_t *len) {
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    struct stat st;
    if (fstat(fileno(f), &st) != 0 || S_ISDIR(st.st_mode)) { fclose(f); return NULL; }
    size_t cap = st.st_size > 0 ? (size_t)st.st_size + 1 : 4096, n = 0;
    char *buf = malloc(cap);
    size_t r;
    while ((r = fread(buf + n, 1, cap - n - 1, f)) > 0) {
        n += r;
        if (n + 1 >= cap) { cap *= 2; buf = realloc(buf, cap); }
    }
    fclose(f);
    buf[n] = 0;
    if (len) *len = n;
    return buf;
}

int kf_write_file(const char *path, const char *data, size_t len, int append) {
    FILE *f = fopen(path, append ? "ab" : "wb");
    if (!f) return 0;
    size_t w = fwrite(data, 1, len, f);
    fclose(f);
    return w == len;
}

int kf_mkdirs(const char *path) {
    char tmp[4096];
    snprintf(tmp, sizeof tmp, "%s", path);
    for (char *p = tmp + 1; *p; p++) {
        if (*p == '/') { *p = 0; mkdir(tmp, 0755); *p = '/'; }
    }
    return mkdir(tmp, 0755) == 0 || errno == EEXIST;
}

char *kf_path_join(const char *a, const char *b) {
    if (!a || !*a) return kstrdup(b);
    if (!b || !*b) return kstrdup(a);
    size_t la = strlen(a);
    int sa = a[la - 1] == '/', sb = b[0] == '/';
    if (sa && sb) return kprintf("%s%s", a, b + 1);
    if (sa || sb) return kprintf("%s%s", a, b);
    return kprintf("%s/%s", a, b);
}

double kf_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1e6;
}

/* Windows-style case-insensitive path lookup: returns an existing path whose
 * components match `path` ignoring case, or NULL. */
#include <dirent.h>
char *kf_resolve_ci(const char *path) {
    struct stat st;
    if (stat(path, &st) == 0) return kstrdup(path);
    if (path[0] != '/') return NULL;
    char *cur = kstrdup("/");
    const char *p = path + 1;
    while (*p) {
        const char *e = strchr(p, '/');
        size_t len = e ? (size_t)(e - p) : strlen(p);
        if (len == 0) { p = e + 1; continue; }
        char *comp = kstrndup(p, len);
        char *cand = kf_path_join(cur, comp);
        if (stat(cand, &st) != 0) {
            DIR *d = opendir(cur);
            if (!d) return NULL;
            struct dirent *de;
            cand = NULL;
            while ((de = readdir(d))) if (!kf_stricmp(de->d_name, comp)) { cand = kf_path_join(cur, de->d_name); break; }
            closedir(d);
            if (!cand) return NULL;
        }
        cur = cand;
        if (!e) break;
        p = e + 1;
    }
    return cur;
}

extern char *kf_global_root(void), *kf_global_webroot(void);
/* map DOS-style paths (C:\CFUSION\..., C:\Inetpub\wwwroot\...) onto the install */
char *kf_native_path(const char *p) {
    if (!p) return NULL;
    int dos = isalpha((unsigned char)p[0]) && p[1] == ':' && (p[2] == '\\' || p[2] == '/');
    if (!dos && !strchr(p, '\\')) return (char *)p;
    char *r = kstrdup(dos ? p + 2 : p);
    for (char *q = r; *q; q++) if (*q == '\\') *q = '/';
    if (!dos) return r;
    const char *root = kf_global_root(), *web = kf_global_webroot();
    if (!kf_strnicmp(r, "/CFUSION/WWWROOT", 16)) { char *x = kf_path_join(web, r + 16), *ci = kf_resolve_ci(x); return ci ? ci : x; }
    if (!kf_strnicmp(r, "/Inetpub/wwwroot", 16)) return kf_path_join(web, r + 16);
    if (!kf_strnicmp(r, "/CFUSION", 8) && (r[8] == '/' || !r[8])) return kf_path_join(root, r + 8);
    char *drive = kf_path_join(root, kprintf("drive_%c", tolower((unsigned char)p[0])));
    kf_mkdirs(drive);
    char *full = kf_path_join(drive, r);
    char *ci = kf_resolve_ci(full);
    return ci ? ci : full;
}

/* convert a local OLE date to UTC using the DST rules in force on that date */
double date_local_to_utc(double dt) {
    int y, mo, d, h, mi, se;
    date_to_parts(dt, &y, &mo, &d, &h, &mi, &se);
    struct tm tm = {0};
    tm.tm_year = y - 1900; tm.tm_mon = mo - 1; tm.tm_mday = d; tm.tm_hour = h; tm.tm_min = mi; tm.tm_sec = se;
    tm.tm_isdst = -1;
    time_t t = mktime(&tm);
    if (t == (time_t)-1) return dt;
    struct tm g; gmtime_r(&t, &g);
    return date_from_parts(g.tm_year + 1900, g.tm_mon + 1, g.tm_mday, g.tm_hour, g.tm_min, g.tm_sec);
}
double date_utc_to_local(double dt) {
    int y, mo, d, h, mi, se;
    date_to_parts(dt, &y, &mo, &d, &h, &mi, &se);
    struct tm tm = {0};
    tm.tm_year = y - 1900; tm.tm_mon = mo - 1; tm.tm_mday = d; tm.tm_hour = h; tm.tm_min = mi; tm.tm_sec = se;
    time_t t = timegm(&tm);
    struct tm l; localtime_r(&t, &l);
    return date_from_parts(l.tm_year + 1900, l.tm_mon + 1, l.tm_mday, l.tm_hour, l.tm_min, l.tm_sec);
}
