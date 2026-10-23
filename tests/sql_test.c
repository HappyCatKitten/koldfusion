/*
 * sql_test.c - exercises the KoldFusion Flat-File Driver (src/sql.c).
 *
 * build: gcc -std=gnu99 -O1 -g -Wall -I src src/core.c src/sql.c tests/sql_test.c -lpthread -lm -o /tmp/sql_test
 * run:   /tmp/sql_test [scratch-dir] [seed-dir]     (run from the project root)
 */
#define _GNU_SOURCE
#include "sql.h"
#include <stdlib.h>
#include <math.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/stat.h>

void kf_out_of_memory(void) { fprintf(stderr, "kf_out_of_memory called\n"); abort(); }

static int passes, fails;
static const char *DB;                 /* current database directory */
static int verbose = 1;

#define CHECK(cond, ...) do {                                                 \
        if (cond) passes++;                                                   \
        else { fails++; printf("  FAIL %s:%d: ", __FILE__, __LINE__);         \
               printf(__VA_ARGS__); printf("\n"); }                           \
    } while (0)

static void dump(Query *q) {
    if (!verbose || !q) return;
    printf("    | ");
    for (int c = 0; c < q->ncols; c++) printf("%s%s", c ? " | " : "", q->cols[c]);
    printf("\n");
    for (int r = 0; r < q->nrows && r < 12; r++) {
        printf("    | ");
        for (int c = 0; c < q->ncols; c++) printf("%s%s", c ? " | " : "", v_tostr(q->data[c][r]));
        printf("\n");
    }
    if (q->nrows > 12) printf("    | ... (%d rows)\n", q->nrows);
}

/* run a SELECT that must succeed */
static Query *Q(const char *sql) {
    Query *q; long n; char err[1024];
    if (verbose) printf("  > %s\n", sql);
    if (!sql_exec(DB, sql, &q, &n, err, sizeof err)) {
        fails++;
        printf("  FAIL: %s\n     -> %s\n", sql, err);
        return NULL;
    }
    passes++;
    if (q && n != q->nrows) { fails++; printf("  FAIL: affected %ld != rows %d\n", n, q->nrows); }
    dump(q);
    return q;
}

/* run a statement that must succeed; returns rows affected */
static long X(const char *sql) {
    Query *q; long n; char err[1024];
    if (verbose) printf("  > %s\n", sql);
    if (!sql_exec(DB, sql, &q, &n, err, sizeof err)) {
        fails++;
        printf("  FAIL: %s\n     -> %s\n", sql, err);
        return -1;
    }
    passes++;
    return n;
}

/* run a statement that must fail with a message containing want */
static void E(const char *sql, const char *want) {
    Query *q; long n; char err[1024];
    if (verbose) printf("  > %s\n", sql);
    int ok = sql_exec(DB, sql, &q, &n, err, sizeof err);
    if (ok) { fails++; printf("  FAIL (expected error '%s'): %s\n", want, sql); return; }
    if (verbose) printf("    ! %s\n", err);
    CHECK(strstr(err, "[Allair][KoldFusion Flat-File Driver] ") == err, "error prefix: %s", err);
    CHECK(strstr(err, want) != NULL, "error for [%s] should contain [%s] but was [%s]", sql, want, err);
}

static const char *S(Query *q, int row, const char *col) {
    if (!q) return "<noquery>";
    int c = query_col_index(q, col);
    if (c < 0) return "<nocol>";
    if (row < 0 || row >= q->nrows) return "<norow>";
    return v_tostr(q->data[c][row]);
}
static double N(Query *q, int row, const char *col) {
    double d = NAN;
    if (!q) return d;
    int c = query_col_index(q, col);
    if (c < 0 || row < 0 || row >= q->nrows) return d;
    if (q->data[c][row].t != VT_NUM) return NAN;
    return q->data[c][row].u.n;
}
static int ROWS(Query *q) { return q ? q->nrows : -1; }
static const char *COLS(Query *q) { return q ? query_column_list(q) : "<noquery>"; }
#define EQS(a, b) CHECK(!strcmp((a), (b)), "expected '%s' got '%s'", (b), (a))
#define EQN(a, b) CHECK(fabs((a) - (b)) < 1e-9, "expected %g got %g", (double)(b), (double)(a))

static void section(const char *name) { printf("\n== %s\n", name); }

/* ------------------------------------------------------------------ */
static void test_ddl_and_insert(void) {
    section("CREATE / INSERT / @@IDENTITY");
    X("CREATE TABLE Departments (Dept_ID INT PRIMARY KEY, Dept_Name VARCHAR(30) NOT NULL, Location TEXT(40))");
    X("CREATE TABLE Employees ("
      " Emp_ID COUNTER PRIMARY KEY, FirstName VARCHAR(25) NOT NULL, LastName VARCHAR(25) NOT NULL,"
      " Email VARCHAR(60), Dept_ID INTEGER, StartDate DATE, Salary MONEY, Contract BIT DEFAULT 0, Notes MEMO)");
    E("CREATE TABLE employees (x INT)", "already exists");
    X("CREATE TABLE IF NOT EXISTS employees (x INT)");
    X("INSERT INTO Departments VALUES (1, 'Sales', 'Boston'), (2, 'Engineering', 'Cambridge'),"
      " (3, 'Marketing', 'Boston'), (4, 'Training', NULL)");
    long n = X("INSERT INTO Employees (FirstName, LastName, Email, Dept_ID, StartDate, Salary, Contract)"
               " VALUES ('Carol', 'Reardon', 'creardon@example.com', 1, #3/14/1997#, 52000, 1)");
    CHECK(n == 1, "insert affected %ld", n);
    Query *q = Q("SELECT @@IDENTITY AS NewID");
    EQN(N(q, 0, "NewID"), 1);
    X("INSERT INTO Employees (FirstName, LastName, Email, Dept_ID, StartDate, Salary)"
      " VALUES ('Doug', 'Whitfield', 'dwhitfield@example.com', 2, {d '1998-06-01'}, 61000.5)");
    X("INSERT INTO Employees (FirstName, LastName, Email, Dept_ID, StartDate, Salary, Contract)"
      " VALUES ('Ellen', 'O''Malley', NULL, 2, '1999-10-22', 72500, 0)");
    X("INSERT INTO Employees (FirstName, LastName, Dept_ID, StartDate, Salary, Contract)"
      " VALUES ('Frank', 'Ngata', 3, {ts '1996-01-02 09:30:00'}, 48000, TRUE)");
    X("INSERT INTO Employees (FirstName, LastName, Dept_ID, StartDate, Salary)"
      " VALUES ('Gina', 'Alvarez', 1, 'Oct 22, 1999', 45000)");
    X("INSERT INTO Employees (FirstName, LastName, Dept_ID, StartDate, Salary)"
      " VALUES ('Hank', 'Brewster', NULL, NULL, NULL)");
    q = Q("SELECT @@IDENTITY");
    EQN(N(q, 0, "EXPR1"), 6);
    /* explicit id beyond counter moves the counter */
    X("INSERT INTO Employees (Emp_ID, FirstName, LastName, Dept_ID, Salary) VALUES (10, 'Ida', 'Kowalski', 4, 39000)");
    X("INSERT INTO Employees (FirstName, LastName, Dept_ID, Salary) VALUES ('Jack', 'Lindqvist', 2, 88000)");
    q = Q("INSERT INTO Departments (Dept_ID, Dept_Name) VALUES (99, 'Temp'); SELECT @@IDENTITY AS NewID;  -- batch");
    EQN(N(q, 0, "NewID"), 11);                      /* Departments has no counter: Jack's id stays */
    CHECK(X("DELETE FROM Departments WHERE Dept_ID = 99; ") == 1, "batch of one with trailing ;");
    q = Q("SELECT SCOPE_IDENTITY() AS id, LAST_INSERT_ID() AS id2");
    EQN(N(q, 0, "id"), 11);
    EQN(N(q, 0, "id2"), 11);
    q = Q("SELECT Emp_ID, Contract FROM Employees WHERE FirstName = 'Gina'");
    EQN(N(q, 0, "Contract"), 0);                   /* DEFAULT 0 applied */
    q = Q("SELECT Contract FROM Employees WHERE Emp_ID = 6");
    EQN(N(q, 0, "Contract"), 0);
}

static void test_basic_select(void) {
    section("basic SELECT");
    Query *q = Q("SELECT * FROM employees ORDER BY Emp_ID");
    CHECK(ROWS(q) == 8, "8 rows, got %d", ROWS(q));
    EQS(COLS(q), "EMP_ID,FIRSTNAME,LASTNAME,EMAIL,DEPT_ID,STARTDATE,SALARY,CONTRACT,NOTES");
    EQS(q->cols[1], "FirstName");                  /* name as defined */
    EQS(S(q, 0, "StartDate"), "1997-03-14 00:00:00");
    EQS(S(q, 3, "StartDate"), "1996-01-02 09:30:00");
    EQS(S(q, 2, "LastName"), "O'Malley");
    EQS(S(q, 2, "Email"), "");                     /* NULL shows as "" */
    CHECK(q && q->data[3][2].t == VT_STR, "NULL is a string");
    EQN(N(q, 1, "Salary"), 61000.5);
    EQN(N(q, 0, "Contract"), 1);
    EQN(N(q, 3, "Contract"), 1);

    q = Q("SELECT FirstName AS fn, [LastName], \"Email\" FROM Employees WHERE Emp_ID = 1");
    EQS(COLS(q), "FN,LASTNAME,EMAIL");
    EQS(S(q, 0, "fn"), "Carol");
    q = Q("SELECT 1 + 2 * 3, 'x' AS y, (7 - 2) / 2 AS z, 10 % 4 AS m, 7 MOD 3 AS m2, -Salary AS neg FROM Employees WHERE Emp_ID = 1");
    EQS(COLS(q), "EXPR1,Y,Z,M,M2,NEG");
    EQN(N(q, 0, "EXPR1"), 7);
    EQN(N(q, 0, "z"), 2.5);
    EQN(N(q, 0, "m"), 2);
    EQN(N(q, 0, "m2"), 1);
    EQN(N(q, 0, "neg"), -52000);
    q = Q("SELECT FirstName + ' ' + LastName AS Full, FirstName & '-' & Emp_ID AS a, LastName || '!' AS b, '1' + '2' AS c FROM Employees WHERE Emp_ID = 2");
    EQS(S(q, 0, "Full"), "Doug Whitfield");
    EQS(S(q, 0, "a"), "Doug-2");
    EQS(S(q, 0, "b"), "Whitfield!");
    EQN(N(q, 0, "c"), 3);
    q = Q("SELECT e.FirstName, e.* FROM Employees AS e WHERE e.Emp_ID = 3");
    CHECK(q && q->ncols == 10, "e.FirstName + e.* = 10 cols, got %d", q ? q->ncols : -1);
    EQS(q ? q->cols[2] : "", "FirstName_2");       /* duplicate names are made unique */
    q = Q("SELECT FirstName FROM Employees WHERE LastName = 'o''malley'");   /* case-insensitive = */
    EQS(S(q, 0, "FirstName"), "Ellen");
    q = Q("SELECT FirstName FROM Employees WHERE FirstName = 'carol   '");  /* trailing blanks ignored */
    CHECK(ROWS(q) == 1, "trailing blank compare");
    q = Q("SELECT FirstName FROM Employees WHERE Contract = TRUE ORDER BY FirstName");
    CHECK(ROWS(q) == 2, "2 contractors, got %d", ROWS(q));
    q = Q("SELECT FirstName FROM Employees WHERE Contract = 'Yes'");
    CHECK(ROWS(q) == 2, "Contract = 'Yes'");
    q = Q("SELECT FirstName FROM Employees WHERE Contract");
    CHECK(ROWS(q) == 2, "bare BIT condition");
    q = Q("SELECT FirstName FROM Employees WHERE NOT Contract AND Dept_ID = 2");
    CHECK(ROWS(q) == 3, "NOT Contract AND dept 2, got %d", ROWS(q));
    q = Q("SELECT 'no from' AS a, 2 * 21 AS b");
    EQS(S(q, 0, "a"), "no from");
    EQN(N(q, 0, "b"), 42);
    q = Q("SELECT {fn UCASE(FirstName)} AS u FROM Employees WHERE Emp_ID = 1");
    EQS(S(q, 0, "u"), "CAROL");
    q = Q("select firstname from EMPLOYEES where emp_id = 1;");
    EQS(S(q, 0, "firstname"), "Carol");
    q = Q("SELECT Emp_ID FROM Employees WHERE Emp_ID = 1 -- trailing comment");
    CHECK(ROWS(q) == 1, "comment");
    q = Q("SELECT /* inline */ Emp_ID FROM Employees WHERE Emp_ID = 2");
    CHECK(ROWS(q) == 1, "inline comment");
}

static void test_where(void) {
    section("WHERE predicates");
    Query *q;
    q = Q("SELECT LastName FROM Employees WHERE LastName LIKE 'w%'");
    EQS(S(q, 0, "LastName"), "Whitfield");
    q = Q("SELECT LastName FROM Employees WHERE LastName LIKE '*ew*' ORDER BY 1");   /* Access wildcards */
    CHECK(ROWS(q) == 1 && !strcmp(S(q, 0, "LastName"), "Brewster"), "*ew* got %d", ROWS(q));
    q = Q("SELECT LastName FROM Employees WHERE FirstName LIKE '_ack'");
    EQS(S(q, 0, "LastName"), "Lindqvist");
    q = Q("SELECT LastName FROM Employees WHERE FirstName LIKE '?ina'");
    EQS(S(q, 0, "LastName"), "Alvarez");
    q = Q("SELECT FirstName FROM Employees WHERE FirstName LIKE '[c-e]%' ORDER BY FirstName");
    CHECK(ROWS(q) == 3, "[c-e]%% got %d", ROWS(q));
    q = Q("SELECT FirstName FROM Employees WHERE FirstName NOT LIKE '%a%' ORDER BY FirstName");
    CHECK(ROWS(q) == 2 && !strcmp(S(q, 0, "FirstName"), "Doug") && !strcmp(S(q, 1, "FirstName"), "Ellen"), "NOT LIKE");
    q = Q("SELECT FirstName FROM Employees WHERE Dept_ID IN (1, 3) ORDER BY FirstName");
    CHECK(ROWS(q) == 3, "IN list got %d", ROWS(q));
    q = Q("SELECT FirstName FROM Employees WHERE Dept_ID NOT IN (1, 3) ORDER BY FirstName");
    CHECK(ROWS(q) == 4, "NOT IN list got %d (NULL dept excluded)", ROWS(q));
    q = Q("SELECT FirstName FROM Employees WHERE LastName IN ('REARDON', 'ngata')");
    CHECK(ROWS(q) == 2, "IN strings ci");
    q = Q("SELECT FirstName FROM Employees WHERE Salary BETWEEN 45000 AND 61000.5 ORDER BY Salary");
    CHECK(ROWS(q) == 4, "BETWEEN got %d", ROWS(q));
    q = Q("SELECT FirstName FROM Employees WHERE Salary NOT BETWEEN 45000 AND 61000.5");
    CHECK(ROWS(q) == 3, "NOT BETWEEN got %d", ROWS(q));
    q = Q("SELECT FirstName FROM Employees WHERE Email IS NULL ORDER BY 1");
    CHECK(ROWS(q) == 6, "IS NULL got %d", ROWS(q));
    q = Q("SELECT FirstName FROM Employees WHERE Email IS NOT NULL");
    CHECK(ROWS(q) == 2, "IS NOT NULL got %d", ROWS(q));
    q = Q("SELECT FirstName FROM Employees WHERE StartDate > #1/1/1998#  ORDER BY StartDate");
    CHECK(ROWS(q) == 3 && !strcmp(S(q, 0, "FirstName"), "Doug"), "date > #..#");
    q = Q("SELECT FirstName FROM Employees WHERE StartDate = {d '1999-10-22'} ORDER BY FirstName");
    CHECK(ROWS(q) == 2, "date = {d}: %d", ROWS(q));
    q = Q("SELECT FirstName FROM Employees WHERE StartDate = '10/22/1999'");
    CHECK(ROWS(q) == 2, "date = 'mm/dd/yyyy' string: %d", ROWS(q));
    q = Q("SELECT FirstName FROM Employees WHERE StartDate BETWEEN {ts '1996-01-01 00:00:00'} AND {ts '1997-12-31 23:59:59'}");
    CHECK(ROWS(q) == 2, "date BETWEEN {ts}: %d", ROWS(q));
    q = Q("SELECT FirstName FROM Employees WHERE StartDate < '1997-01-01'");
    EQS(S(q, 0, "FirstName"), "Frank");
    q = Q("SELECT FirstName FROM Employees WHERE (Dept_ID = 1 OR Dept_ID = 3) AND NOT Salary < 46000");
    CHECK(ROWS(q) == 2, "AND/OR/NOT got %d", ROWS(q));
    q = Q("SELECT FirstName FROM Employees WHERE Dept_ID = NULL");
    CHECK(ROWS(q) == 0, "= NULL is unknown");
    q = Q("SELECT FirstName FROM Employees WHERE Dept_ID <> 2 AND Dept_ID != 4 ORDER BY FirstName");
    CHECK(ROWS(q) == 3, "<> and != got %d", ROWS(q));
    q = Q("SELECT FirstName FROM Employees WHERE Salary >= 72500 OR Salary <= 39000 ORDER BY Salary");
    CHECK(ROWS(q) == 3, ">= <= got %d", ROWS(q));
    q = Q("SELECT FirstName FROM Employees WHERE Emp_ID = '2'");
    EQS(S(q, 0, "FirstName"), "Doug");
}

static void test_aggregates(void) {
    section("aggregates / GROUP BY / HAVING");
    Query *q;
    q = Q("SELECT COUNT(*) AS n, COUNT(Email) AS ne, COUNT(Dept_ID) AS nd, COUNT(DISTINCT Dept_ID) AS dd,"
          " SUM(Salary) AS total, AVG(Salary) AS av, MIN(Salary) AS lo, MAX(Salary) AS hi, MIN(StartDate) AS first FROM Employees");
    EQN(N(q, 0, "n"), 8);
    EQN(N(q, 0, "ne"), 2);
    EQN(N(q, 0, "nd"), 7);
    EQN(N(q, 0, "dd"), 4);
    EQN(N(q, 0, "total"), 52000 + 61000.5 + 72500 + 48000 + 45000 + 39000 + 88000);
    EQN(N(q, 0, "av"), (52000 + 61000.5 + 72500 + 48000 + 45000 + 39000 + 88000) / 7.0);
    EQN(N(q, 0, "lo"), 39000);
    EQN(N(q, 0, "hi"), 88000);
    EQS(S(q, 0, "first"), "1996-01-02 09:30:00");
    q = Q("SELECT COUNT(*) AS n, SUM(Salary) AS s, MAX(LastName) AS m FROM Employees WHERE 1 = 0");
    CHECK(ROWS(q) == 1, "aggregate over nothing = 1 row");
    EQN(N(q, 0, "n"), 0);
    EQS(S(q, 0, "s"), "");
    q = Q("SELECT Dept_ID, COUNT(*) AS n FROM Employees WHERE 1 = 0 GROUP BY Dept_ID");
    CHECK(ROWS(q) == 0, "GROUP BY over nothing = 0 rows");
    q = Q("SELECT Dept_ID, COUNT(*) AS n, SUM(Salary) AS total FROM Employees GROUP BY Dept_ID ORDER BY Dept_ID");
    CHECK(ROWS(q) == 5, "5 groups (incl NULL) got %d", ROWS(q));
    EQS(S(q, 0, "Dept_ID"), "");                   /* NULL group sorts first */
    EQN(N(q, 2, "n"), 3);
    EQN(N(q, 2, "total"), 61000.5 + 72500 + 88000);
    q = Q("SELECT Dept_ID, COUNT(*) AS n FROM Employees GROUP BY Dept_ID HAVING COUNT(*) > 1 ORDER BY 2 DESC, Dept_ID");
    CHECK(ROWS(q) == 2, "HAVING got %d", ROWS(q));
    EQN(N(q, 0, "Dept_ID"), 2);
    EQN(N(q, 1, "Dept_ID"), 1);
    q = Q("SELECT Dept_ID AS d, AVG(Salary) AS avgsal FROM Employees WHERE Dept_ID IS NOT NULL GROUP BY Dept_ID ORDER BY avgsal DESC");
    EQN(N(q, 0, "d"), 2);
    EQN(N(q, 3, "d"), 4);
    q = Q("SELECT COUNT(*) FROM Employees");
    EQS(COLS(q), "EXPR1");
    q = Q("SELECT YEAR(StartDate) AS yr, COUNT(*) AS n FROM Employees WHERE StartDate IS NOT NULL GROUP BY YEAR(StartDate) ORDER BY yr");
    CHECK(ROWS(q) == 4, "group by expression got %d", ROWS(q));
    EQN(N(q, 3, "yr"), 1999);
    EQN(N(q, 3, "n"), 2);
    q = Q("SELECT Contract, COUNT(*) AS n FROM Employees GROUP BY Contract ORDER BY Contract");
    CHECK(ROWS(q) == 2, "group by bit");
    q = Q("SELECT SUM(Salary) / COUNT(*) AS x, MAX(Salary) - MIN(Salary) AS spread FROM Employees WHERE Dept_ID = 2");
    EQN(N(q, 0, "spread"), 88000 - 61000.5);
    q = Q("SELECT FIRST(FirstName) AS f, LAST(FirstName) AS l FROM Employees");
    EQS(S(q, 0, "f"), "Carol");
    EQS(S(q, 0, "l"), "Jack");
    q = Q("SELECT COUNT(DISTINCT Contract) AS n FROM Employees");
    EQN(N(q, 0, "n"), 2);
}

static void test_joins(void) {
    section("joins");
    Query *q;
    q = Q("SELECT e.FirstName, d.Dept_Name FROM Employees e INNER JOIN Departments d ON e.Dept_ID = d.Dept_ID ORDER BY e.Emp_ID");
    CHECK(ROWS(q) == 7, "inner join got %d", ROWS(q));
    EQS(S(q, 0, "Dept_Name"), "Sales");
    q = Q("SELECT e.FirstName, d.Dept_Name FROM Employees AS e LEFT OUTER JOIN Departments AS d ON e.Dept_ID = d.Dept_ID ORDER BY e.Emp_ID");
    CHECK(ROWS(q) == 8, "left join got %d", ROWS(q));
    EQS(S(q, 5, "FirstName"), "Hank");
    EQS(S(q, 5, "Dept_Name"), "");
    q = Q("SELECT d.Dept_Name, COUNT(e.Emp_ID) AS n FROM Departments d LEFT JOIN Employees e ON e.Dept_ID = d.Dept_ID AND e.Salary > 50000 GROUP BY d.Dept_Name ORDER BY d.Dept_Name");
    CHECK(ROWS(q) == 4, "left join + group got %d", ROWS(q));
    EQS(S(q, 0, "Dept_Name"), "Engineering");
    EQN(N(q, 0, "n"), 3);
    EQS(S(q, 3, "Dept_Name"), "Training");
    EQN(N(q, 3, "n"), 0);
    q = Q("SELECT d.Dept_Name, e.LastName FROM Employees e RIGHT JOIN Departments d ON e.Dept_ID = d.Dept_ID WHERE e.Emp_ID IS NULL");
    CHECK(ROWS(q) == 0, "right join: every dept has someone");
    X("INSERT INTO Departments (Dept_ID, Dept_Name) VALUES (5, 'Accounting')");
    q = Q("SELECT d.Dept_Name FROM Employees e RIGHT JOIN Departments d ON e.Dept_ID = d.Dept_ID WHERE e.Emp_ID IS NULL");
    CHECK(ROWS(q) == 1 && !strcmp(S(q, 0, "Dept_Name"), "Accounting"), "right join finds empty dept");
    q = Q("SELECT Employees.LastName, Departments.Dept_Name FROM Employees, Departments"
          " WHERE Employees.Dept_ID = Departments.Dept_ID AND Departments.Location = 'boston' ORDER BY 1");
    CHECK(ROWS(q) == 3, "comma join got %d", ROWS(q));
    EQS(S(q, 0, "LastName"), "Alvarez");
    X("CREATE TABLE Locations (City VARCHAR(30), Region VARCHAR(20))");
    X("INSERT INTO Locations VALUES ('Boston', 'East'), ('Cambridge', 'East')");
    q = Q("SELECT e.LastName, d.Dept_Name, l.Region FROM (Employees e INNER JOIN Departments d ON e.Dept_ID = d.Dept_ID)"
          " INNER JOIN Locations l ON d.Location = l.City ORDER BY e.LastName");
    CHECK(ROWS(q) == 6, "Access nested join got %d", ROWS(q));
    EQS(S(q, 0, "Region"), "East");
    q = Q("SELECT * FROM Departments d JOIN Locations l ON l.City = d.Location WHERE d.Dept_ID = 2");
    EQS(COLS(q), "DEPT_ID,DEPT_NAME,LOCATION,CITY,REGION");
    q = Q("SELECT COUNT(*) AS n FROM Departments CROSS JOIN Locations");
    EQN(N(q, 0, "n"), 10);
    q = Q("SELECT a.FirstName AS a, b.FirstName AS b FROM Employees a, Employees b WHERE a.Dept_ID = b.Dept_ID AND a.Emp_ID < b.Emp_ID ORDER BY a.Emp_ID, b.Emp_ID");
    CHECK(ROWS(q) == 4, "self join pairs got %d", ROWS(q));
    E("SELECT Dept_ID FROM Employees, Departments", "could refer to more than one table");
}

static void test_subqueries(void) {
    section("subqueries");
    Query *q;
    q = Q("SELECT FirstName FROM Employees WHERE Dept_ID IN (SELECT Dept_ID FROM Departments WHERE Location = 'Boston') ORDER BY 1");
    CHECK(ROWS(q) == 3, "IN subquery got %d", ROWS(q));
    q = Q("SELECT Dept_Name FROM Departments WHERE Dept_ID NOT IN (SELECT Dept_ID FROM Employees WHERE Dept_ID IS NOT NULL)");
    CHECK(ROWS(q) == 1 && !strcmp(S(q, 0, "Dept_Name"), "Accounting"), "NOT IN subquery");
    q = Q("SELECT FirstName, Salary FROM Employees WHERE Salary = (SELECT MAX(Salary) FROM Employees)");
    EQS(S(q, 0, "FirstName"), "Jack");
    q = Q("SELECT (SELECT MAX(Emp_ID) FROM Employees) + 1 AS nextid");
    EQN(N(q, 0, "nextid"), 12);
    q = Q("SELECT d.Dept_Name FROM Departments d WHERE EXISTS (SELECT * FROM Employees e WHERE e.Dept_ID = d.Dept_ID AND e.Contract = 1) ORDER BY 1");
    CHECK(ROWS(q) == 2, "correlated EXISTS got %d", ROWS(q));
    q = Q("SELECT d.Dept_Name FROM Departments d WHERE NOT EXISTS (SELECT 1 FROM Employees e WHERE e.Dept_ID = d.Dept_ID)");
    CHECK(ROWS(q) == 1, "NOT EXISTS got %d", ROWS(q));
    q = Q("SELECT d.Dept_Name, (SELECT COUNT(*) FROM Employees e WHERE e.Dept_ID = d.Dept_ID) AS headcount FROM Departments d ORDER BY headcount DESC, d.Dept_Name");
    EQS(S(q, 0, "Dept_Name"), "Engineering");
    EQN(N(q, 0, "headcount"), 3);
    EQN(N(q, 4, "headcount"), 0);
    q = Q("SELECT e.FirstName FROM Employees e WHERE e.Salary > (SELECT AVG(x.Salary) FROM Employees x WHERE x.Dept_ID = e.Dept_ID) ORDER BY 1");
    CHECK(ROWS(q) == 2, "correlated scalar got %d", ROWS(q));
    q = Q("SELECT Emp_ID FROM Employees WHERE Salary = (SELECT MAX(Salary) FROM Employees e2 WHERE e2.Dept_ID = Employees.Dept_ID) ORDER BY 1");
    CHECK(ROWS(q) == 4, "aliased inner table hides its name, outer Employees.x correlates: %d", ROWS(q));
    q = Q("SELECT Employees.FirstName FROM Employees e WHERE e.Emp_ID = 1");      /* lenient fallback */
    EQS(S(q, 0, "FirstName"), "Carol");
    q = Q("SELECT t.Dept_ID, t.n FROM (SELECT Dept_ID, COUNT(*) AS n FROM Employees GROUP BY Dept_ID) AS t WHERE t.n > 1 ORDER BY t.Dept_ID");
    CHECK(ROWS(q) == 2, "derived table got %d", ROWS(q));
    q = Q("SELECT MAX(n) AS biggest FROM (SELECT COUNT(*) AS n FROM Employees GROUP BY Dept_ID) x");
    EQN(N(q, 0, "biggest"), 3);
    E("SELECT FirstName FROM Employees WHERE Salary = (SELECT Salary FROM Employees)", "At most one record");
    E("SELECT FirstName FROM Employees WHERE Dept_ID IN (SELECT Dept_ID, Dept_Name FROM Departments)", "more than one field");
}

static void test_functions(void) {
    section("scalar functions");
    Query *q;
    q = Q("SELECT UPPER(FirstName) AS u, UCASE('a') AS u2, LOWER(LastName) AS l, LCASE('B') AS l2, LEN(LastName) AS n, LENGTH('abc') AS n2,"
          " TRIM('  x  ') AS t, LTRIM('  x ') AS lt, RTRIM(' x  ') AS rt, LEFT(LastName, 3) AS le, RIGHT(LastName, 3) AS ri,"
          " MID(LastName, 2, 3) AS mi, SUBSTRING(LastName, 2, 2) AS su, MID(LastName, 4) AS mi2 FROM Employees WHERE Emp_ID = 2");
    EQS(S(q, 0, "u"), "DOUG"); EQS(S(q, 0, "u2"), "A"); EQS(S(q, 0, "l"), "whitfield"); EQS(S(q, 0, "l2"), "b");
    EQN(N(q, 0, "n"), 9); EQN(N(q, 0, "n2"), 3);
    EQS(S(q, 0, "t"), "x"); EQS(S(q, 0, "lt"), "x "); EQS(S(q, 0, "rt"), " x");
    EQS(S(q, 0, "le"), "Whi"); EQS(S(q, 0, "ri"), "eld"); EQS(S(q, 0, "mi"), "hit"); EQS(S(q, 0, "su"), "hi");
    EQS(S(q, 0, "mi2"), "tfield");
    q = Q("SELECT ROUND(2.675, 2) AS r, ROUND(-2.5) AS r2, ROUND(1234.5678, -2) AS r3, ABS(-3) AS a, INT(-2.5) AS i, FIX(-2.5) AS f,"
          " FLOOR(2.7) AS fl, CEILING(2.1) AS ce, SQRT(16) AS sq, POWER(2, 10) AS pw, SIGN(-5) AS sg, MOD(10, 3) AS md");
    EQN(N(q, 0, "r"), 2.68); EQN(N(q, 0, "r2"), -3); EQN(N(q, 0, "r3"), 1200); EQN(N(q, 0, "a"), 3);
    EQN(N(q, 0, "i"), -3); EQN(N(q, 0, "f"), -2); EQN(N(q, 0, "fl"), 2); EQN(N(q, 0, "ce"), 3);
    EQN(N(q, 0, "sq"), 4); EQN(N(q, 0, "pw"), 1024); EQN(N(q, 0, "sg"), -1); EQN(N(q, 0, "md"), 1);
    q = Q("SELECT YEAR(StartDate) AS y, MONTH(StartDate) AS m, DAY(StartDate) AS d, HOUR(StartDate) AS h, MINUTE(StartDate) AS mi"
          " FROM Employees WHERE Emp_ID = 4");
    EQN(N(q, 0, "y"), 1996); EQN(N(q, 0, "m"), 1); EQN(N(q, 0, "d"), 2); EQN(N(q, 0, "h"), 9); EQN(N(q, 0, "mi"), 30);
    q = Q("SELECT NOW() AS n, GETDATE() AS g, YEAR(NOW()) AS y, DATE() AS d");
    CHECK(q && strlen(S(q, 0, "n")) == 19, "NOW() formatted: %s", S(q, 0, "n"));
    CHECK(N(q, 0, "y") >= 2024, "YEAR(NOW())");
    EQS(S(q, 0, "d") + 11, "00:00:00");
    q = Q("SELECT COALESCE(Email, 'none') AS c, IFNULL(Email, 'n/a') AS i, ISNULL(Email, '-') AS s, NZ(Email, '?') AS z,"
          " ISNULL(Email) AS isn, IIF(Contract = 1, 'Contractor', 'Staff') AS kind, NULLIF(Dept_ID, 3) AS nd FROM Employees WHERE Emp_ID = 4");
    EQS(S(q, 0, "c"), "none"); EQS(S(q, 0, "i"), "n/a"); EQS(S(q, 0, "s"), "-"); EQS(S(q, 0, "z"), "?");
    EQN(N(q, 0, "isn"), 1); EQS(S(q, 0, "kind"), "Contractor"); EQS(S(q, 0, "nd"), "");
    q = Q("SELECT IIF(Salary > 60000, 'high', IIF(Salary > 45000, 'mid', 'low')) AS band, COUNT(*) AS n FROM Employees WHERE Salary IS NOT NULL"
          " GROUP BY IIF(Salary > 60000, 'high', IIF(Salary > 45000, 'mid', 'low')) ORDER BY 1");
    CHECK(ROWS(q) == 3, "group by IIF got %d", ROWS(q));
    EQS(S(q, 0, "band"), "high"); EQN(N(q, 0, "n"), 3);
    q = Q("SELECT REPLACE('Hello World', 'world', 'There') AS r, INSTR('abcabc', 'CA') AS i, INSTR(5, 'abcabc', 'b') AS i2,"
          " CHARINDEX('c', 'abcabc') AS ci, CONCAT('a', NULL, 'b', 3) AS cc, STR(42) AS s, VAL('12abc') AS v, CINT('3.6') AS ci2,"
          " ASCII('A') AS asc1, CHR(66) AS ch, SPACE(3) AS sp, REPLICATE('ab', 3) AS rp, REVERSE('abc') AS rv");
    EQS(S(q, 0, "r"), "Hello There"); EQN(N(q, 0, "i"), 3); EQN(N(q, 0, "i2"), 5); EQN(N(q, 0, "ci"), 3);
    EQS(S(q, 0, "cc"), "ab3"); EQS(S(q, 0, "s"), "42"); EQN(N(q, 0, "v"), 12); EQN(N(q, 0, "ci2"), 4);
    EQN(N(q, 0, "asc1"), 65); EQS(S(q, 0, "ch"), "B"); EQS(S(q, 0, "sp"), "   "); EQS(S(q, 0, "rp"), "ababab"); EQS(S(q, 0, "rv"), "cba");
    q = Q("SELECT DATEADD('d', 10, #10/22/1999#) AS a, DATEADD(month, 4, '1999-10-31') AS b, DATEADD('yyyy', 1, {d '2000-02-29'}) AS c,"
          " DATEDIFF('d', #1/1/1999#, #1/1/2000#) AS d, DATEDIFF(month, '1999-10-22', '2000-01-05') AS e, DATEDIFF('yyyy', #12/31/1999#, #1/1/2000#) AS f,"
          " DATEPART('q', #10/22/1999#) AS g, DATEPART(weekday, #10/22/1999#) AS h, DATESERIAL(1999, 14, 1) AS i, CDATE('Oct 22 1999') AS j,"
          " DATEDIFF('h', {ts '1999-10-22 10:59:00'}, {ts '1999-10-22 12:01:00'}) AS k, #10/22/1999# + 1 AS l, #10/23/1999# - #10/22/1999# AS m");
    EQS(S(q, 0, "a"), "1999-11-01 00:00:00"); EQS(S(q, 0, "b"), "2000-02-29 00:00:00"); EQS(S(q, 0, "c"), "2001-02-28 00:00:00");
    EQN(N(q, 0, "d"), 365); EQN(N(q, 0, "e"), 3); EQN(N(q, 0, "f"), 1); EQN(N(q, 0, "g"), 4); EQN(N(q, 0, "h"), 6);
    EQS(S(q, 0, "i"), "2000-02-01 00:00:00"); EQS(S(q, 0, "j"), "1999-10-22 00:00:00"); EQN(N(q, 0, "k"), 2);
    EQS(S(q, 0, "l"), "1999-10-23 00:00:00"); EQN(N(q, 0, "m"), 1);
    q = Q("SELECT CASE WHEN Salary > 60000 THEN 'big' WHEN Salary IS NULL THEN 'unknown' ELSE 'normal' END AS c,"
          " CASE Dept_ID WHEN 1 THEN 'S' WHEN 2 THEN 'E' END AS d FROM Employees ORDER BY Emp_ID");
    EQS(S(q, 0, "c"), "normal"); EQS(S(q, 1, "c"), "big"); EQS(S(q, 5, "c"), "unknown");
    EQS(S(q, 0, "d"), "S"); EQS(S(q, 3, "d"), "");
    q = Q("SELECT CAST(Salary AS INTEGER) AS i, CAST(Emp_ID AS VARCHAR(10)) + 'x' AS s, CAST('1999-10-22' AS DATETIME) AS d,"
          " CONVERT(VARCHAR(3), LastName) AS v FROM Employees WHERE Emp_ID = 2");
    EQN(N(q, 0, "i"), 61001); EQS(S(q, 0, "s"), "2x"); EQS(S(q, 0, "d"), "1999-10-22 00:00:00"); EQS(S(q, 0, "v"), "Whi");
    q = Q("SELECT UPPER(NULL) AS a, LEN(Email) AS b, Email + 'x' AS c, NULL & 'x' AS d FROM Employees WHERE Emp_ID = 4");
    EQS(S(q, 0, "a"), ""); EQS(S(q, 0, "b"), ""); EQS(S(q, 0, "c"), ""); EQS(S(q, 0, "d"), "x");
    E("SELECT FOOBAR(1)", "Undefined function 'FOOBAR'");
    E("SELECT LEFT('x')", "Wrong number of arguments");
}

static void test_order_distinct_top(void) {
    section("ORDER BY / DISTINCT / TOP / LIMIT / UNION");
    Query *q;
    q = Q("SELECT DISTINCT Dept_ID FROM Employees ORDER BY Dept_ID DESC");
    CHECK(ROWS(q) == 5, "distinct got %d", ROWS(q));
    EQN(N(q, 0, "Dept_ID"), 4);
    EQS(S(q, 4, "Dept_ID"), "");
    q = Q("SELECT DISTINCT Location FROM Departments WHERE Location IS NOT NULL");
    CHECK(ROWS(q) == 2, "distinct strings got %d", ROWS(q));
    q = Q("SELECT TOP 3 FirstName, Salary FROM Employees ORDER BY Salary DESC");
    CHECK(ROWS(q) == 3, "top 3");
    EQS(S(q, 0, "FirstName"), "Jack"); EQS(S(q, 2, "FirstName"), "Doug");
    q = Q("SELECT TOP 25 PERCENT FirstName FROM Employees ORDER BY Emp_ID");
    CHECK(ROWS(q) == 2, "top 25 percent of 8 = 2, got %d", ROWS(q));
    q = Q("SELECT FirstName FROM Employees ORDER BY Emp_ID LIMIT 2 OFFSET 3");
    CHECK(ROWS(q) == 2 && !strcmp(S(q, 0, "FirstName"), "Frank"), "limit/offset");
    q = Q("SELECT FirstName FROM Employees ORDER BY Emp_ID LIMIT 1, 2");
    CHECK(ROWS(q) == 2 && !strcmp(S(q, 0, "FirstName"), "Doug"), "limit a,b");
    q = Q("SELECT FirstName, LastName FROM Employees ORDER BY Dept_ID DESC, LastName ASC");
    EQS(S(q, 0, "LastName"), "Kowalski");
    EQS(S(q, 1, "LastName"), "Ngata");
    q = Q("SELECT FirstName AS name FROM Employees ORDER BY name DESC");
    EQS(S(q, 0, "name"), "Jack");
    q = Q("SELECT FirstName FROM Employees ORDER BY Salary * -1");      /* not in select list; NULL first */
    EQS(S(q, 0, "FirstName"), "Hank"); EQS(S(q, 1, "FirstName"), "Jack");
    q = Q("SELECT FirstName FROM Employees ORDER BY 1");
    EQS(S(q, 0, "FirstName"), "Carol");
    q = Q("SELECT LastName AS n FROM Employees WHERE Dept_ID = 1 UNION SELECT Dept_Name FROM Departments WHERE Dept_ID < 3 ORDER BY n");
    CHECK(ROWS(q) == 4, "union got %d", ROWS(q));
    EQS(S(q, 0, "n"), "Alvarez");
    q = Q("SELECT Location FROM Departments UNION SELECT Location FROM Departments");
    CHECK(ROWS(q) == 3, "union dedupes (Boston, Cambridge, NULL) got %d", ROWS(q));
    q = Q("SELECT Location FROM Departments UNION ALL SELECT Location FROM Departments ORDER BY 1 DESC");
    CHECK(ROWS(q) == 10, "union all got %d", ROWS(q));
    EQS(S(q, 0, "Location"), "Cambridge");
    E("SELECT a FROM (SELECT 1 AS a) x UNION SELECT 1, 2", "union query do not match");
    q = Q("SELECT UPPER(LastName) FROM Employees WHERE Dept_ID = 2 ORDER BY 1 DESC");
    EQS(S(q, 0, "EXPR1"), "WHITFIELD");
}

static void test_update_delete(void) {
    section("UPDATE / DELETE / INSERT..SELECT");
    long n;
    n = X("UPDATE Employees SET Salary = Salary * 1.1, Notes = 'Raise ' & YEAR(#1/1/2000#) WHERE Dept_ID = 2");
    CHECK(n == 3, "update affected %ld", n);
    Query *q = Q("SELECT Salary, Notes FROM Employees WHERE Emp_ID = 2");
    EQN(N(q, 0, "Salary"), round(61000.5 * 1.1 * 10000) / 10000);    /* MONEY keeps 4 places */
    EQS(S(q, 0, "Notes"), "Raise 2000");
    n = X("UPDATE Employees SET Email = LCASE(LEFT(FirstName, 1) & LastName) + '@example.com' WHERE Email IS NULL AND Dept_ID IS NOT NULL");
    CHECK(n == 5, "update emails %ld", n);
    q = Q("SELECT Email FROM Employees WHERE Emp_ID = 3");
    EQS(S(q, 0, "Email"), "eo'malley@example.com");
    n = X("UPDATE Employees SET Contract = 0");
    CHECK(n == 8, "update all %ld", n);
    n = X("UPDATE Employees e SET e.Contract = 1 WHERE e.Dept_ID IN (SELECT Dept_ID FROM Departments WHERE Location = 'Boston')");
    CHECK(n == 3, "update with subquery %ld", n);
    n = X("UPDATE Employees SET LastName = LastName WHERE 1 = 0");
    CHECK(n == 0, "update nothing");
    X("CREATE TABLE Alumni (ID COUNTER, Name VARCHAR(60), Left_On DATE DEFAULT #12/31/1999#, Tag VARCHAR(10) DEFAULT 'alum')");
    n = X("INSERT INTO Alumni (Name) SELECT FirstName + ' ' + LastName FROM Employees WHERE Contract = 1 ORDER BY LastName");
    CHECK(n == 3, "insert..select %ld", n);
    q = Q("SELECT * FROM Alumni ORDER BY ID");
    EQS(S(q, 0, "Name"), "Gina Alvarez"); EQS(S(q, 0, "Left_On"), "1999-12-31 00:00:00"); EQS(S(q, 2, "Tag"), "alum");
    EQN(N(q, 2, "ID"), 3);
    n = X("INSERT INTO Alumni (Name, Tag) VALUES ('Zed', NULL)");
    q = Q("SELECT Tag FROM Alumni WHERE Name = 'Zed'");
    EQS(S(q, 0, "Tag"), "");                       /* explicit NULL beats DEFAULT */
    n = X("DELETE FROM Alumni WHERE Name LIKE 'Z%'");
    CHECK(n == 1, "delete %ld", n);
    n = X("DELETE * FROM Alumni WHERE ID = 2");
    CHECK(n == 1, "Access DELETE * %ld", n);
    n = X("DELETE Alumni.* FROM Alumni WHERE ID = 999");
    CHECK(n == 0, "delete nothing");
    n = X("DELETE FROM Alumni");
    CHECK(n == 2, "delete all %ld", n);
    X("INSERT INTO Alumni (Name) VALUES ('After')");
    q = Q("SELECT ID FROM Alumni");
    EQN(N(q, 0, "ID"), 5);                         /* counters are never reused */
    n = X("DELETE FROM Employees WHERE Emp_ID NOT IN (SELECT MIN(Emp_ID) FROM Employees GROUP BY Dept_ID) AND Dept_ID = 2");
    CHECK(n == 2, "delete with self subquery %ld", n);
    q = Q("SELECT COUNT(*) AS n FROM Employees");
    EQN(N(q, 0, "n"), 6);
}

static void test_alter_drop(void) {
    section("ALTER / DROP / describe / list");
    X("ALTER TABLE Departments ADD COLUMN Budget CURRENCY DEFAULT 1000");
    X("ALTER TABLE Departments ADD Phone VARCHAR(20)");
    Query *q = Q("SELECT Dept_ID, Budget, Phone FROM Departments ORDER BY Dept_ID");
    EQN(N(q, 0, "Budget"), 1000);
    EQS(S(q, 0, "Phone"), "");
    X("UPDATE Departments SET Phone = '555-0100' WHERE Dept_ID = 1");
    X("ALTER TABLE Departments DROP COLUMN Budget");
    q = Q("SELECT * FROM Departments WHERE Dept_ID = 1");
    EQS(COLS(q), "DEPT_ID,DEPT_NAME,LOCATION,PHONE");
    EQS(S(q, 0, "Phone"), "555-0100");
    E("ALTER TABLE Departments DROP COLUMN Nope", "does not exist");
    E("ALTER TABLE Departments ADD Phone INT", "already exists");
    X("CREATE TABLE Scratch (a INT)");
    X("CREATE INDEX idx_a ON Scratch (a)");          /* accepted, ignored */
    X("DROP TABLE scratch");
    E("SELECT * FROM Scratch", "Table 'Scratch' not found.");
    E("DROP TABLE Scratch", "not found");
    X("DROP TABLE IF EXISTS Scratch");

    char err[512];
    q = NULL;
    CHECK(sql_describe(DB, "employees", &q, err, sizeof err), "describe: %s", err);
    dump(q);
    CHECK(q && q->nrows == 9, "describe rows");
    EQS(S(q, 0, "COLUMN_NAME"), "Emp_ID"); EQS(S(q, 0, "TYPE_NAME"), "COUNTER"); EQN(N(q, 0, "ORDINAL"), 1);
    EQS(S(q, 0, "IS_AUTOINCREMENT"), "YES"); EQS(S(q, 0, "IS_PRIMARY_KEY"), "YES");
    EQS(S(q, 1, "TYPE_NAME"), "VARCHAR(25)"); EQS(S(q, 1, "IS_NULLABLE"), "NO");
    EQS(S(q, 7, "COLUMN_DEFAULT"), "0");
    CHECK(!sql_describe(DB, "Nope", &q, err, sizeof err) && strstr(err, "not found"), "describe missing: %s", err);
    q = NULL;
    CHECK(sql_list_tables(DB, &q, err, sizeof err), "list: %s", err);
    dump(q);
    CHECK(q && q->nrows == 4, "4 tables, got %d", q ? q->nrows : -1);
    EQS(S(q, 0, "TABLE_NAME"), "Alumni"); EQS(S(q, 2, "TABLE_NAME"), "Employees");
    EQN(N(q, 2, "COLUMN_COUNT"), 9); EQN(N(q, 2, "ROW_COUNT"), 6);
}

static void test_errors(void) {
    section("errors");
    E("SELECT * FROM Nope", "Table 'Nope' not found.");
    E("SELECT * FORM Employees", "Syntax error in SQL statement near 'FORM'.");
    E("SELECT FirstName FROM Employees WHERE", "unexpected end of statement");
    E("SELECT Bogus FROM Employees", "Unknown column 'Bogus'");
    E("SELECT e.Bogus FROM Employees e", "Unknown column 'e.Bogus'");
    E("INSERT INTO Employees (FirstName) VALUES ('NoLast')", "cannot contain a Null value");
    E("INSERT INTO Departments VALUES (1, 'Dup', 'X', NULL)", "duplicate values");
    E("UPDATE Departments SET Dept_ID = 2 WHERE Dept_ID = 1", "duplicate values");
    E("INSERT INTO Departments (Dept_ID, Dept_Name) VALUES (9, 'This name is far too long for thirty chars')", "too small");
    E("INSERT INTO Employees (FirstName, LastName, Salary) VALUES ('A', 'B', 'lots')", "Data type mismatch");
    E("INSERT INTO Employees (FirstName, LastName, StartDate) VALUES ('A', 'B', 'not a date')", "Data type mismatch");
    E("INSERT INTO Employees (Nope) VALUES (1)", "unknown field name: 'Nope'");
    E("INSERT INTO Departments VALUES (1, 'x')", "Number of query values and destination fields are not the same");
    E("SELECT 1 / 0", "Division by zero");
    E("SELECT 'abc' * 2", "Data type mismatch");
    E("SELECT FirstName FROM Employees WHERE COUNT(*) > 1", "aggregate function in WHERE");
    E("SELECT 'unterminated FROM Employees", "Unterminated string");
    E("SELECT * FROM Employees a FULL OUTER JOIN Departments b ON a.Dept_ID = b.Dept_ID", "FULL OUTER JOIN is not supported");
    E("SELECT #13/45/1999#", "Syntax error in date");
    E("GRANT ALL ON x TO y", "expected 'DELETE', 'INSERT', 'PROCEDURE', 'SELECT', or 'UPDATE'");
    E("", "empty");
    E("SELECT * FROM Employees ORDER BY 99", "out of range");
    E("SELECT * FROM [../etc/passwd]", "Invalid table name");
    E("CREATE TABLE Bad (x WIDGET)", "unknown data type 'WIDGET'");
    E("CREATE TABLE Bad2 (x INT, X TEXT)", "defined more than once");
    E("SELECT 1 AS a; SELECT * FROM Nope", "not found. (batch statement 2)");
    E("SELECT FirstName FROM Employees WHERE Emp_ID = 1 extra", "near 'extra'");
    E("SELECT SQRT(-1)", "SQRT");
    E("SELECT DATEADD('fortnight', 1, NOW())", "unknown date interval");
    /* failed statements must not have changed anything */
    Query *q = Q("SELECT COUNT(*) AS n FROM Departments");
    EQN(N(q, 0, "n"), 5);
}

static void test_storage(const char *base) {
    section("storage format / escaping / reload");
    X("CREATE TABLE [Odd Names] (ID AUTOINCREMENT(100, 1) PRIMARY KEY, [Long Text] MEMO, Price NUMERIC(10,2), Flag YESNO, Seen DATETIME)");
    X("INSERT INTO [Odd Names] ([Long Text], Price, Flag, Seen) VALUES ('tab\there' + CHR(10) + 'line2\\back\\N', 3.14159, 'yes', {ts '1999-12-31 23:59:59'})");
    X("INSERT INTO [Odd Names] ([Long Text], Price, Flag) VALUES ('', NULL, 0)");
    X("INSERT INTO [Odd Names] ([Long Text]) VALUES ('\\N')");
    char *path = kprintf("%s/Odd Names.tbl", DB);
    size_t len;
    char *data = kf_read_file(path, &len);
    CHECK(data != NULL, "table file exists at %s", path);
    if (data) {
        if (verbose) printf("    --- %s ---\n%s    ---\n", path, data);
        CHECK(!strncmp(data, "#KFTABLE 1\n", 11), "header");
        CHECK(strstr(data, "ID:AUTOINCREMENT:AUTOINC:PK\tLong Text:MEMO\tPrice:NUMERIC(10,2)\tFlag:YESNO\tSeen:DATETIME\n103\n") != NULL, "column line + next id");
        CHECK(strstr(data, "100\ttab\\there\\nline2\\\\back\\\\N\t3.14\t1\t1999-12-31 23:59:59\n") != NULL, "escaped row");
        CHECK(strstr(data, "101\t\t\\N\t0\t\\N\n") != NULL, "empty string vs NULL row");
        CHECK(strstr(data, "102\t\\\\N\t\\N\t\\N\t\\N\n") != NULL, "literal backslash-N text");
        free(data);
    }
    sql_cache_flush();                              /* force a re-read from disk */
    Query *q = Q("SELECT * FROM [odd names] ORDER BY ID");
    EQS(S(q, 0, "Long Text"), "tab\there\nline2\\back\\N");
    EQN(N(q, 0, "Price"), 3.14);
    EQN(N(q, 0, "Flag"), 1);
    EQS(S(q, 0, "Seen"), "1999-12-31 23:59:59");
    EQS(S(q, 1, "Long Text"), "");
    EQS(S(q, 2, "Long Text"), "\\N");
    q = Q("SELECT COUNT(*) AS n FROM [Odd Names] WHERE [Long Text] = ''");
    EQN(N(q, 0, "n"), 1);
    q = Q("SELECT COUNT(*) AS n FROM [Odd Names] WHERE Price IS NULL");
    EQN(N(q, 0, "n"), 2);

    /* hand-edited file: CRLF line endings, extra blank line, short row */
    char *hand = kprintf("%s/Handmade.tbl", DB);
    const char *txt = "#KFTABLE 1\r\nCode:CHAR(3):PK\tName:VARCHAR(40)\tQty:INT\r\n1\r\nABC\tWidget\t5\r\n\r\nXYZ\tGadget\r\n";
    CHECK(kf_write_file(hand, txt, strlen(txt), 0), "write hand file");
    q = Q("SELECT * FROM handmade ORDER BY Code");
    CHECK(ROWS(q) == 2, "hand-made rows %d", ROWS(q));
    EQS(S(q, 1, "Name"), "Gadget");
    EQS(S(q, 1, "Qty"), "");
    /* edits on disk are noticed (mtime/size/inode) without a flush */
    usleep(20000);
    const char *txt2 = "#KFTABLE 1\nCode:CHAR(3):PK\tName:VARCHAR(40)\tQty:INT\n1\nQQQ\tThing\t7\n";
    CHECK(kf_write_file(hand, txt2, strlen(txt2), 0), "rewrite hand file");
    q = Q("SELECT Name FROM Handmade");
    CHECK(ROWS(q) == 1 && !strcmp(S(q, 0, "Name"), "Thing"), "external edit seen");
    CHECK(kf_write_file(hand, "garbage\n", 8, 0), "corrupt file");
    E("SELECT * FROM Handmade", "corrupt");
    unlink(hand);
    (void)base;
}

/* ------------------------------------------------------------ threads */
#define NTHREADS 8
#define PER_THREAD 25
static int thread_errors;
static void *worker(void *arg) {
    long id = (long)arg;
    Arena *a = arena_new();
    g_arena = a;
    for (int i = 0; i < PER_THREAD; i++) {
        char sql[256], err[512];
        long n;
        Query *q;
        snprintf(sql, sizeof sql, "INSERT INTO Hits (Thread, Seq) VALUES (%ld, %d)", id, i);
        if (!sql_exec(DB, sql, NULL, &n, err, sizeof err) || n != 1) { __sync_fetch_and_add(&thread_errors, 1); fprintf(stderr, "%s\n", err); continue; }
        if (!sql_exec(DB, "SELECT @@IDENTITY AS id", &q, &n, err, sizeof err) || !q || q->nrows != 1) { __sync_fetch_and_add(&thread_errors, 1); continue; }
        double myid = q->data[0][0].u.n;
        snprintf(sql, sizeof sql, "SELECT Thread, Seq FROM Hits WHERE HitID = %.0f", myid);
        if (!sql_exec(DB, sql, &q, &n, err, sizeof err) || !q || q->nrows != 1 ||
            q->data[0][0].u.n != id || q->data[1][0].u.n != i) {
            __sync_fetch_and_add(&thread_errors, 1);
            fprintf(stderr, "thread %ld: identity %g does not point at my row\n", id, myid);
        }
        if (!sql_exec(DB, "SELECT COUNT(*) FROM Hits h, Departments d WHERE h.Thread = d.Dept_ID", &q, &n, err, sizeof err))
            __sync_fetch_and_add(&thread_errors, 1);
    }
    arena_free(a);
    return NULL;
}

static void test_threads(void) {
    section("threads");
    X("CREATE TABLE Hits (HitID COUNTER PRIMARY KEY, Thread INT NOT NULL, Seq INT)");
    int ov = verbose; verbose = 0;
    pthread_t th[NTHREADS];
    for (long i = 0; i < NTHREADS; i++) pthread_create(&th[i], NULL, worker, (void *)i);
    for (int i = 0; i < NTHREADS; i++) pthread_join(th[i], NULL);
    verbose = ov;
    CHECK(thread_errors == 0, "thread errors: %d", thread_errors);
    Query *q = Q("SELECT COUNT(*) AS n, COUNT(DISTINCT HitID) AS d, MAX(HitID) AS mx FROM Hits");
    EQN(N(q, 0, "n"), NTHREADS * PER_THREAD);
    EQN(N(q, 0, "d"), NTHREADS * PER_THREAD);
    EQN(N(q, 0, "mx"), NTHREADS * PER_THREAD);
}

/* ---------------------------------------------------------------- seeds */
static char *slurp(const char *path) {
    size_t len;
    return kf_read_file(path, &len);
}

static void test_seeds(const char *scratch, const char *seeddir) {
    section("seed scripts");
    char err[1024];
    char *script, *dir;

    dir = kprintf("%s/cfsnippets", scratch);
    script = slurp(kprintf("%s/cfsnippets.sql", seeddir));
    CHECK(script != NULL, "read cfsnippets.sql");
    if (script) {
        int ok = sql_exec_script(dir, script, err, sizeof err);
        CHECK(ok, "cfsnippets.sql: %s", err);
        free(script);
        DB = dir;
        Query *q = Q("SELECT COUNT(*) AS n FROM Employees");
        CHECK(N(q, 0, "n") >= 20, "employees seeded: %g", N(q, 0, "n"));
        q = Q("SELECT Department, COUNT(*) AS n, AVG(Salary) AS avgsal FROM Employees GROUP BY Department ORDER BY Department");
        CHECK(ROWS(q) == 6, "6 departments, got %d", ROWS(q));
        q = Q("SELECT e.FirstName, e.LastName, d.Location FROM Employees e INNER JOIN Departments d ON e.Department = d.Dept_Name WHERE d.Location LIKE 'B%' ORDER BY e.LastName");
        CHECK(ROWS(q) > 0, "employee/department join");
        q = Q("SELECT c.Number, c.Descript, d.Dept_Name FROM Courses c LEFT JOIN Departments d ON c.Dept_ID = d.Dept_ID ORDER BY c.Number");
        CHECK(ROWS(q) > 0, "courses");
        q = Q("SELECT TOP 3 Name, Price FROM Products ORDER BY Price DESC");
        CHECK(ROWS(q) == 3, "products");
        q = Q("SELECT Name, Posted FROM GuestBook ORDER BY Posted DESC");
        CHECK(ROWS(q) >= 3, "guestbook");
        q = Q("SELECT m.Subject, (SELECT COUNT(*) FROM Messages r WHERE r.ParentID = m.MsgID) AS replies FROM Messages m WHERE m.ParentID = 0 ORDER BY m.Posted");
        CHECK(ROWS(q) >= 2, "forum threads");
        q = Q("SELECT FirstName, LastName FROM Employees WHERE StartDate < #1/1/1995# AND Contract = 0 ORDER BY StartDate");
        CHECK(q != NULL, "date filter on seed data");
        CHECK(sql_list_tables(dir, &q, err, sizeof err), "list seeded tables: %s", err);
        dump(q);
        CHECK(q && q->nrows == 6, "cfsnippets has 6 tables, got %d", q ? q->nrows : -1);
    }

    dir = kprintf("%s/exampleapp", scratch);
    script = slurp(kprintf("%s/exampleapp.sql", seeddir));
    CHECK(script != NULL, "read exampleapp.sql");
    if (script) {
        int ok = sql_exec_script(dir, script, err, sizeof err);
        CHECK(ok, "exampleapp.sql: %s", err);
        free(script);
        DB = dir;
        Query *q = Q("SELECT TOP 5 Headline, Posted FROM News ORDER BY Posted DESC");
        CHECK(ROWS(q) == 5, "news");
        q = Q("SELECT d.Dept_Name, COUNT(e.Emp_ID) AS staff FROM Departments d LEFT JOIN Employees e ON e.Dept_ID = d.Dept_ID GROUP BY d.Dept_Name ORDER BY staff DESC");
        CHECK(ROWS(q) > 0, "exampleapp departments");
        q = Q("SELECT c.CourseNum, c.Title FROM Courses c ORDER BY c.CourseNum");
        CHECK(ROWS(q) > 0, "exampleapp courses");
        CHECK(sql_list_tables(dir, &q, err, sizeof err), "list exampleapp tables: %s", err);
        dump(q);
    }

    /* script error reporting */
    CHECK(!sql_exec_script(kprintf("%s/broken", scratch),
                           "CREATE TABLE T (a INT);\n-- comment; with semicolon\nINSERT INTO T VALUES (1);\nINSERT INTO T VALUES ('x;y');",
                           err, sizeof err), "broken script fails");
    CHECK(strstr(err, "statement 3") != NULL, "script error names statement: %s", err);
}

int main(int argc, char **argv) {
    const char *scratch = argc > 1 ? argv[1] : "/tmp";
    const char *seeddir = argc > 2 ? argv[2] : "kfroot/seed";
    if (getenv("QUIET")) verbose = 0;
    Arena *a = arena_new();
    g_arena = a;
    char *base = kprintf("%s/sqltest-%d", scratch, (int)getpid());
    kf_mkdirs(base);
    DB = kprintf("%s/main", base);
    printf("database dir: %s\n", DB);

    test_ddl_and_insert();
    test_basic_select();
    test_where();
    test_aggregates();
    test_joins();
    test_subqueries();
    test_functions();
    test_order_distinct_top();
    test_update_delete();
    test_alter_drop();
    test_errors();
    test_storage(base);
    test_threads();
    test_seeds(base, seeddir);

    printf("\n%d passed, %d failed\n", passes, fails);
    sql_cache_flush();
    if (!fails) { int rc = system(kprintf("rm -rf '%s'", base)); (void)rc; }
    arena_free(a);
    return fails ? 1 : 0;
}
