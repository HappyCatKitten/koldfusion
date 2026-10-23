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
 * "[Allair][KoldFusion Flat-File Driver] Table 'FOO' not found."). */
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

#endif
