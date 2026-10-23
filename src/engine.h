/*
 * engine.h - the CFML engine: expressions, templates, runtime context
 */
#ifndef ENGINE_H
#define ENGINE_H

#include "kf.h"
#include <setjmp.h>
#include <pthread.h>

/* ============================================================ expressions */
typedef enum {
    E_LIT,      /* literal value */
    E_STRI,     /* interpolated string: args = parts (E_LIT or expr) */
    E_VAR,      /* bare identifier: name */
    E_DOT,      /* a.name */
    E_INDEX,    /* a[b] */
    E_CALL,     /* name(args) */
    E_BIN,      /* a op b */
    E_UN,       /* op a */
    E_ASSIGN,   /* a = b (cfset / cfscript); op holds compound operator or 0 */
    E_POSTINC,  /* a++ / a-- (cfscript only); op = '+' or '-' */
    E_PREINC
} EKind;

enum {
    OP_ADD = 1, OP_SUB, OP_MUL, OP_DIV, OP_IDIV, OP_MOD, OP_POW, OP_CAT,
    OP_EQ, OP_NEQ, OP_LT, OP_LTE, OP_GT, OP_GTE, OP_CONTAINS, OP_NCONTAINS,
    OP_AND, OP_OR, OP_XOR, OP_EQV, OP_IMP, OP_NOT, OP_NEG, OP_POS
};

typedef struct Expr Expr;
struct Expr {
    EKind k;
    int op;
    Val lit;
    const char *name;
    Expr *a, *b;
    Expr **args; int nargs;
    const char *src; int srclen;   /* source text, for error messages */
    int line, col;
    void *fn;                      /* cached builtin function pointer for E_CALL */
};

/* ============================================================ cfscript */
typedef enum {
    S_EXPR, S_IF, S_WHILE, S_DO, S_FOR, S_FORIN, S_SWITCH, S_BREAK,
    S_CONTINUE, S_BLOCK, S_RETURN, S_EMPTY
} SKind;
typedef struct Stmt Stmt;
struct Stmt {
    SKind k;
    Expr *e, *e2, *e3;             /* expression / cond / init,cond,step */
    const char *var;               /* for-in variable */
    Stmt *body, *els;
    Stmt **kids; int nkids;        /* block, or switch cases */
    Expr **caseval; int *isdefault;/* switch: per-kid case values */
    int line, col;
};

/* ============================================================ templates */
typedef enum { N_TEXT, N_EXPR, N_TAG, N_END } NKind;

typedef struct Attr { const char *name; Expr *val; const char *raw; } Attr;

typedef struct Node Node;
typedef struct Template Template;
struct Node {
    NKind k;
    const char *text; size_t len;  /* N_TEXT */
    Expr *expr;                    /* N_EXPR; also cfset/cfif/cfelseif expression */
    const char *tag;               /* lowercase full name e.g. "cfoutput", "cf_mytag" */
    Attr *attrs; int nattrs;
    Node **kids; int nkids, kcap;
    int has_end;                   /* closed with an end tag */
    int selfclose;                 /* <cf_tag /> */
    Stmt *script;                  /* cfscript body */
    const char *rawsrc; int rawlen;/* tag source for error messages */
    int line, col, eline, ecol;
    Template *tpl;
    void *fn;                      /* cached tag handler */
};

struct Template {
    char *path;                    /* filesystem path */
    char *src; size_t srclen;
    Node *root;
    Arena *arena;
    long mtime;
    double loaded_at;
    int refs;
    int stale;
    double last_used;
    Template *next;                /* cache chain */
};

/* ============================================================ errors */
typedef struct KfError {
    const char *type;              /* Expression, Database, Template, Application,
                                      Security, Object, MissingInclude, Lock,
                                      Custom type, Any */
    const char *message;
    const char *detail;
    const char *extended;          /* ExtendedInfo / custom errorcode */
    const char *errorcode;
    const char *sqlstate;
    const char *nativecode;
    const char *sql;               /* for database errors */
    const char *datasource;
    const char *heading;           /* e.g. "An error occurred while evaluating the expression:" */
    const char *snippet;           /* the expression/tag text */
    const char *tplpath;
    int line, col;
    const char *tagname;
    Val custom;                    /* cfthrow extras */
} KfError;

typedef struct JmpFrame { jmp_buf jb; struct JmpFrame *prev; } JmpFrame;

/* ============================================================ runtime */
typedef struct HttpReq HttpReq;
typedef struct AppState AppState;
typedef struct SessState SessState;

typedef struct DebugQuery {
    const char *name, *datasource, *sql, *template;
    double ms; int records;
    struct DebugQuery *next;
} DebugQuery;

typedef struct DebugTpl { const char *path; double ms; struct DebugTpl *next; } DebugTpl;

/* per-request state */
typedef struct RState {
    HttpReq *http;
    Buf *out;                      /* current output target */
    Buf  page;                     /* root page output */
    Struct *form, *url, *cgi, *cookie, *client, *session, *application, *server, *request;
    AppState *app;                 /* cfapplication */
    SessState *sess;
    int client_enabled, client_dirty;
    const char *client_storage;
    const char *cfid, *cftoken;

    /* response */
    int status; const char *status_text;
    Struct *headers;               /* extra response headers */
    Array *setcookies;             /* Set-Cookie header values */
    const char *content_type;
    const char *location;          /* cflocation */
    const char *content_file;      /* cfcontent file="" */
    int content_delete;
    int content_reset;
    Buf htmlhead;                  /* cfhtmlhead */

    /* control */
    JmpFrame *jf;                  /* exception handlers */
    KfError *err;                  /* current error being thrown */
    int aborting;                  /* cfabort */
    double start_ms, deadline_ms;
    int enablecfoutputonly;
    int show_debug;                /* debug output for this request */
    int debug_override;            /* cfsetting showdebugoutput */
    Node *cur_node;
    Template *cur_tpl;
    int depth;                     /* include/custom tag depth */

    DebugQuery *dq, *dq_tail;
    DebugTpl *dt;
    Arena *arena;
    int is_admin;                  /* request under /CFIDE/administrator */
    int locks_held;
    void *held_locks[32];
    int nformfiles;
    Struct *formfiles;             /* name -> struct(tmpfile, clientfile, contenttype, size) */
    int internal;                  /* scheduler / internal request */
    const char *auth_user;         /* advanced security: cfauthenticate */
    Struct *auth;
    Struct *cferror;               /* cferror type -> struct(template, mailto) */
    Template **tpl_used; int ntpl_used, captpl_used;
    int suppress_ws;
    int show_query_info, show_proc_time, show_vars, show_sql, show_tpl_path, detail_view;
    const char *base_template;     /* GetBaseTemplatePath() */
    const char *appname;
    double timeout_s;
    Array *tagstack;               /* custom tag names for GetBaseTagList */
    Array *tagdata;                /* parallel ThisTag/attributes structs */
    int in_error_handler;
    const char *held_lock_names[32];
    const char *cache_file;        /* CFCACHE: write page output here at the end */
    const char *cache_key;
    int strict_attrs;
    void *ftp;                     /* open CFFTP connections */
    const char *locale;
    const char *validation_errors;   /* <LI> list from hidden-field form validation */
    int in_txn;                    /* CFTRANSACTION depth */
    Struct *txn;                   /* db directory -> snapshot directory */
    char lockmode_server, lockmode_app, lockmode_session;   /* 'n'one, 'f'ull, 'r'eadlock */
} RState;

typedef struct QLoop { Query *q; struct QLoop *prev; } QLoop;

/* per-page context (a custom tag or cfmodule gets a fresh one) */
typedef struct Ctx {
    RState *rs;
    Template *tpl;
    Struct *variables;
    Struct *attributes;            /* custom tag */
    Struct *caller;                /* caller's Variables */
    Struct *thistag;
    struct Ctx *parent;
    QLoop *qloop;                  /* active query loops */
    int in_output;                 /* inside cfoutput */
    int sql_mode;                  /* building cfquery SQL: escape quotes */
    Array *sqlparams;              /* cfqueryparam values (not used: inlined) */
    int loopdepth;
    const char *tagdir;            /* directory of current template */
    /* grouped CFOUTPUT */
    Query *grp_q; int grp_start, grp_end, grp_active;
    /* CFFORM being built */
    struct FormCtx *form;
    Node *custom_body;             /* body nodes of the custom tag call */
    struct Ctx *custom_body_ctx;
} Ctx;

typedef struct FormCtx {
    const char *name;
    Buf checks;                    /* JavaScript validation statements */
    int count;
} FormCtx;

/* control flow results */
enum { FL_OK = 0, FL_BREAK, FL_CONTINUE, FL_EXIT_TAG, FL_EXIT_TEMPLATE, FL_EXIT_LOOP };

/* ---------- expr.c */
Expr *expr_parse(const char *src, int *pos, int len, int script, int line0, int col0,
                 const char **err, int stop_at_hash);
Expr *expr_parse_string(const char *s, const char **err);   /* whole string must parse */
Expr *expr_parse_strlit(const char *src, int *pos, int len, const char **err);
Val   eval(Ctx *c, Expr *e);
Val   eval_to_simple(Ctx *c, Expr *e);
const char *eval_str(Ctx *c, Expr *e);
Val  *lvalue(Ctx *c, Expr *e, int create, int *is_new);
void  assign(Ctx *c, Expr *lhs, Val v);
void  assign_path(Ctx *c, const char *path, Val v);          /* SetVariable() */
int   resolve_path(Ctx *c, const char *path, Val *out);      /* IsDefined() */
Struct *scope_by_name(Ctx *c, const char *name, int for_write);
Val   op_binary(Ctx *c, int op, Val a, Val b, Expr *where);
int   val_truth(Ctx *c, Val v, Expr *where);
double val_number(Ctx *c, Val v, Expr *where);
const char *val_simple_str(Ctx *c, Val v, Expr *where);

/* ---------- parse.c */
Template *template_parse(const char *path, char *src, size_t len, Arena *a, KfError **perr);
void pos_to_linecol(const char *src, size_t off, int *line, int *col);

/* ---------- interp.c */
void  exec_nodes(Ctx *c, Node **kids, int n, int *flow);
void  exec_template(Ctx *c, Template *t);
int   run_request(RState *rs, const char *tplpath);          /* returns 0 ok */
Template *template_get(RState *rs, const char *path, KfError **perr);
const char *resolve_template_path(Ctx *c, const char *tpl, int for_module);
void  kf_throw(Ctx *c, const char *type, const char *msg, const char *detail) __attribute__((noreturn));
void  kf_throw_err(RState *rs, KfError *e) __attribute__((noreturn));
void  kf_throw_at(Ctx *c, Expr *where, const char *type, const char *msg, const char *detail) __attribute__((noreturn));
KfError *kf_error_new(const char *type, const char *msg, const char *detail);
Val   error_to_cfcatch(KfError *e);
void  out_puts(Ctx *c, const char *s);
void  out_put(Ctx *c, const char *s, size_t n);
const char *attr_str(Ctx *c, Node *n, const char *name, const char *def);
Val   attr_val(Ctx *c, Node *n, const char *name, int *present);
int   attr_bool(Ctx *c, Node *n, const char *name, int def);
double attr_num(Ctx *c, Node *n, const char *name, double def);
int   has_attr(Node *n, const char *name);
const char *require_attr(Ctx *c, Node *n, const char *name);
void  render_error_page(RState *rs, KfError *e);
void  render_debug(RState *rs, Ctx *c);
Ctx  *ctx_new(RState *rs, Template *t);
void  check_timeout(Ctx *c);
extern __thread RState *t_rs;
const char *kf_html_escape(const char *s);
const char *kf_template_dir(const char *path);
void  tag_security_check(Ctx *c, const char *tagname);
void  strict_check(Ctx *c, Node *n);

/* ---------- tags.c */
typedef void (*TagFn)(Ctx *c, Node *n, int *flow);
TagFn tag_lookup(const char *name);
int   tag_is_paired(const char *name);   /* 2 = must, 1 = optional, 0 = void */
void  call_custom_tag(Ctx *c, Node *n, const char *path, Struct *attrs, int *flow);

/* ---------- func.c */
typedef Val (*BuiltinFn)(Ctx *c, int argc, Val *argv, Expr *call);
typedef struct FuncDef { const char *name; BuiltinFn fn; int minargs, maxargs; } FuncDef;
BuiltinFn func_lookup(const char *name, int *minargs, int *maxargs);
int   func_is_lazy(BuiltinFn fn);
Query *func_list_all(void);

/* ---------- script.c */
Stmt *script_parse(const char *src, int len, int line0, int col0, const char **err, int *eline, int *ecol);
void  script_exec(Ctx *c, Stmt *s, int *flow);

/* ---------- formatting helpers (func.c) */
char *kf_dateformat(double dt, const char *mask);
char *kf_timeformat(double dt, const char *mask);
char *kf_numberformat(double n, const char *mask);
char *kf_dollarformat(double n);
char *kf_urlencode(const char *s);
char *kf_urldecode(const char *s, size_t n);
char *kf_htmleditformat(const char *s);
char *kf_create_uuid(void);
char *list_get_at(const char *list, int idx, const char *delims);
int   list_len(const char *list, const char *delims);
Array *list_to_array_k(const char *list, const char *delims);

/* ============================================================ server-wide */
#include <time.h>
typedef struct Globals {
    char *root;              /* KoldFusion install dir ("C:\CFUSION") */
    char *webroot;           /* document root */
    char *bind; int port;
    char *exe_path;
    double started_at;       /* date_now() at startup */
    double started_ms;
    long requests_served;
    int  active_requests;
    int  queued_requests;
    long cfid_counter;
    int  restart_requested;
    int  unresponsive;
    char **argv;
} Globals;
extern Globals G;

/* ---------- registry.c  (REGEDIT4 format file in <root>/registry/kf.registry) */
void  reg_init(const char *path);
char *reg_get(const char *key, const char *entry, const char *def);   /* arena copy, NULL if absent and def NULL */
int   reg_get_int(const char *key, const char *entry, int def);
int   reg_exists(const char *key, const char *entry);                  /* entry NULL = key */
void  reg_set(const char *key, const char *entry, const char *value, int dword);
void  reg_delete_entry(const char *key, const char *entry);
void  reg_delete_key(const char *key);                                 /* recursive */
Query *reg_list(const char *key, int want_keys, int want_values);      /* Entry, Type, Value */
void  reg_save(void);
long  reg_version(void);
/* shorthands rooted at KF_REG_ROOT */
char *cfg(const char *sub, const char *entry, const char *def);
int   cfg_int(const char *sub, const char *entry, int def);
void  cfg_set(const char *sub, const char *entry, const char *value);
char *cfg_key(const char *sub);                                        /* full key path */
#define REG_SERVER "Server"

/* ---------- crypto.c */
char *cfmx_compat_encrypt(const char *plain, size_t len, const char *key);  /* uuencoded */
char *cfmx_compat_decrypt(const char *uu, const char *key, size_t *outlen);
void  cfmx_compat_transform(unsigned char *buf, size_t len, const char *key);
char *uu_encode(const unsigned char *p, size_t n);
unsigned char *uu_decode(const char *s, size_t *outlen);
void  md5(const unsigned char *data, size_t len, unsigned char out[16]);
char *md5_hex_upper(const char *s, size_t len);
char *base64_encode(const unsigned char *p, size_t n);
unsigned char *base64_decode(const char *s, size_t *outlen);
#define KF_REGISTRY_KEY "4llair!kf"          /* the fixed "secret" (only bytes 4..7 matter!) */
char *kf_scramble(const char *pw);           /* store a secret the 1999 way */
char *kf_unscramble(const char *s);

/* ---------- log.c */
void  kf_log(const char *file, const char *severity, const char *fmt, ...) __attribute__((format(printf, 3, 4)));
char *kf_log_dir(void);

/* ---------- session.c */
struct AppState {
    char *name;
    Arena *arena;
    Struct *scope;
    double last_access;      /* date_now() */
    double timeout_days;
    double created;
    AppState *next;
};
struct SessState {
    char *key;               /* APPNAME_CFID_CFTOKEN */
    char *app;
    Arena *arena;
    Struct *scope;
    double last_access;
    double timeout_days;
    double created;
    int refs;
    pthread_mutex_t mu;      /* single-threaded sessions */
    SessState *next;
};
void session_init(void);
AppState  *app_get(const char *name, double timeout_days, int *created);
SessState *sess_get(const char *app, const char *cfid, const char *cftoken, double timeout_days, int *created);
void sess_release(SessState *s);
void session_housekeeping(void);
Query *session_stats(void);
void client_load(RState *rs, const char *appname);
void client_save(RState *rs, const char *appname);
long next_cfid(void);
int  named_lock(const char *name, int exclusive, double timeout_s);   /* returns handle >=0 or -1 */
void named_unlock(int handle);

/* ---------- http.c */
struct HttpReq {
    int fd;
    char *method, *uri, *path, *query, *version;
    Struct *headers;         /* lower-case names */
    char *body; size_t bodylen;
    char *remote_addr; int remote_port;
    char *server_name; int server_port;
    char *content_type;
    double started_ms;
    int internal;
};
int  http_serve(void);
int  http_client(const char *method, const char *url, Struct *hdrs, const char *body, size_t bodylen,
                 int timeout_s, const char *proxy, int proxyport, const char *user, const char *pass,
                 Buf *resp_body, int *status, char **status_line, Struct **resp_headers, char *err, size_t errlen);
char *http_date(time_t t);
const char *mime_type_for(const char *path);

/* ---------- mail.c */
int  mail_spool(Struct *msg, char *err, size_t el);   /* from,to,cc,bcc,subject,body,type,server,port,timeout,headers(struct),attachments(array) */
void mail_spooler_start(void);
int  smtp_verify(const char *server, int port, int timeout, char *msg, size_t msglen);

/* ---------- sched.c */
void sched_start(void);
int  sched_run_task(const char *name, char *msg, size_t msglen);

/* ---------- verity.c */
int  verity_create(const char *name, const char *path, const char *lang, char *err, size_t el);
int  verity_delete(const char *name, char *err, size_t el);
int  verity_purge(const char *name, char *err, size_t el);
int  verity_optimize(const char *name, char *err, size_t el);
int  verity_update(const char *collection, const char *key, const char *title, const char *body,
                   const char *url, const char *custom1, const char *custom2, char *err, size_t el);
int  verity_remove(const char *collection, const char *key, char *err, size_t el);
int  verity_index_path(const char *collection, const char *dir, const char *exts, int recurse,
                       const char *urlpath, long *count, char *err, size_t el);
Query *verity_search(const char *collections, const char *criteria, int maxrows, int startrow, char *err, size_t el);
Query *verity_list(void);

/* ---------- cfx.c */
void cfx_call(Ctx *c, Node *n, const char *name);

/* ---------- datasources (dsn.c) */
typedef struct Dsn {
    const char *name, *driver, *kind, *path, *description, *username, *password;
    int login_timeout, maintain, disabled, restrict_select, restrict_insert, restrict_update, restrict_delete, restrict_sp;
} Dsn;
int  dsn_lookup(const char *name, Dsn *out);         /* 1 found */
int  dsn_verify(const char *name, char *msg, size_t msglen);
Query *dsn_list(void);

#endif
