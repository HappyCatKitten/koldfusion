/*
 * KoldFusion Application Server 4.5
 *
 * sql.h - the "KoldFusion Flat-File Driver": a small built-in SQL engine
 *         over human-readable text tables, one <table>.tbl file per table
 *         inside a database directory. Speaks the Access/ODBC flavoured SQL
 *         that 1999 CFML applications sent through <CFQUERY>.
 */
#ifndef KF_SQL_H
#define KF_SQL_H

#include "kf.h"

/* Execute ONE SQL statement against the database directory dbdir.
 * SELECT -> *out = result Query (allocated with kmalloc in g_arena), *affected = rowcount.
 * Others -> *out = NULL, *affected = rows changed.
 * out / affected may be NULL when the caller does not care.
 * A ;-separated batch is also accepted ("INSERT ...; SELECT @@IDENTITY AS ID"):
 * statements run in order (each atomic on its own, the batch is not), *out is
 * the last result set produced and *affected the count of the last statement.
 * Returns 1 on success; 0 on error with a message in err (CF/ODBC-flavoured, e.g.
 * "[Gibson][KoldFusion Flat-File Driver] Table 'FOO' not found."). */
int sql_exec(const char *dbdir, const char *sql, Query **out, long *affected, char *err, size_t errlen);

/* Run a script of ;-separated statements (-- and slash-star comments are
 * skipped). Stops at the first error; the message names the statement number. */
int sql_exec_script(const char *dbdir, const char *script, char *err, size_t errlen);

/* List tables: query with columns TABLE_NAME, COLUMN_COUNT, ROW_COUNT (sorted by name). */
int sql_list_tables(const char *dbdir, Query **out, char *err, size_t errlen);

/* Describe a table: columns COLUMN_NAME, TYPE_NAME, ORDINAL, plus IS_NULLABLE,
 * IS_PRIMARY_KEY, IS_AUTOINCREMENT ("YES"/"NO") and COLUMN_DEFAULT. */
int sql_describe(const char *dbdir, const char *table, Query **out, char *err, size_t errlen);

/* Last auto-increment value generated (or explicitly stored) by an INSERT on
 * this thread - what SELECT @@IDENTITY returns. 0 if none yet. */
int sql_last_identity(double *out);

/* 1 if name is acceptable as a table name (letters, digits, _ $ - and inner spaces). */
int sql_valid_table_name(const char *name);

/* Drop every cached parsed table (they are re-read from disk on next use). */
void sql_cache_flush(void);

/* Execute exactly ONE statement (no batch splitting, no procedure handling).
 * typed != 0 keeps SQL NULLs (VT_NULL) and dates (VT_DATE) in the result
 * instead of the CF forms "" and "yyyy-mm-dd hh:mm:ss". */
int sql_exec1(const char *dbdir, const char *sql, Query **out, long *affected, int typed, char *err, size_t errlen);

/* ------------------------------------------------ stored procedures (sqlproc.c)
 * CREATE PROCEDURE name (@p type [= default] [OUTPUT], ...) AS <statements>
 * is stored as <dbdir>/<name>.prc. Bodies are T-SQL flavoured: DECLARE, SET,
 * SELECT @v = ..., IF/ELSE, WHILE, BEGIN/END, RETURN, EXEC, RAISERROR. */
#define SQL_PARAM_IN    1
#define SQL_PARAM_OUT   2
#define SQL_PARAM_INOUT 3

typedef struct SqlParam {
    const char *name;     /* "@Dept" / "Dept" for named binding, NULL = positional */
    int   dir;            /* SQL_PARAM_IN / OUT / INOUT */
    int   use_default;    /* pass DEFAULT */
    Val   value;          /* input value; VT_NULL is SQL NULL */
    Val   out;            /* OUT/INOUT: value after the call (VT_NULL = NULL) */
    int   has_out;
} SqlParam;

typedef struct SqlProcResult {
    Query **sets; int nsets;   /* every result set, in order */
    double  status;            /* RETURN value (0 when the procedure has none) */
    long    affected;          /* rows affected by the last statement */
} SqlProcResult;

/* Call a stored procedure. Result sets and OUT values are allocated in g_arena. */
int sql_call_procedure(const char *dbdir, const char *proc, SqlParam *params, int nparams,
                       SqlProcResult *res, char *err, size_t errlen);

/* PROCEDURE_NAME, PARAMETERS ("@Dept VARCHAR(30), @Count INT OUTPUT"), PARAMETER_COUNT, SOURCE */
int sql_list_procedures(const char *dbdir, Query **out, char *err, size_t errlen);

/* Install every CREATE PROCEDURE of a seed script whose procedure does not exist yet. */
int sql_seed_procedures(const char *dbdir, const char *script, char *err, size_t errlen);

/* hooks used by sql.c: */
size_t sqlproc_extent(const char *text);                 /* length of a CREATE PROCEDURE statement, 0 = not one */
int    sqlproc_statement(const char *dbdir, const char *stmt, Query **out, long *affected,
                         char *err, size_t errlen);      /* -1 = not a procedure statement */
int    sqlproc_batch(const char *dbdir, const char *sql, Query **out, long *affected,
                     char *err, size_t errlen);          /* -1 = not a T-SQL batch */

#endif
