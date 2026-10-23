<cfsetting enablecfoutputonly="yes">
<!--- stored procedures (CFSTOREDPROC / CFPROCPARAM / CFPROCRESULT, EXEC, {call}, T-SQL batches) --->
<cfquery datasource="cfsnippets">DROP PROCEDURE IF EXISTS KfTestFlow, KfTestOuter</cfquery>
<cfquery datasource="cfsnippets">
CREATE PROCEDURE KfTestFlow
    @Limit INT,
    @Label VARCHAR(5) = 'abcdefgh',
    @Sum   INT OUTPUT,
    @Note  VARCHAR(40) OUTPUT
AS
    DECLARE @i INT, @odd INT
    SET @i = 0
    SET @Sum = 0
    SET @odd = 0
    WHILE @i < 100
    BEGIN
        SET @i += 1
        IF @i > @Limit BREAK
        IF @i % 2 = 0 CONTINUE
        SET @Sum = @Sum + @i
        SET @odd = @odd + 1
    END
    SELECT @i AS LastI, @odd AS Odds, @Label AS Label
    IF @Sum > 20
        SET @Note = 'big'
    ELSE
        SET @Note = 'small'
    RETURN @Sum * 2
</cfquery>
<cfquery datasource="cfsnippets">
CREATE PROCEDURE KfTestOuter @Limit INT AS
BEGIN
    DECLARE @s INT, @n VARCHAR(40), @rc INT;
    EXEC @rc = KfTestFlow @Limit, DEFAULT, @s OUTPUT, @Note = @n OUTPUT;
    SELECT @rc AS RC, @s AS S, @n AS N, @@NESTLEVEL AS Lvl;
END
</cfquery>

<!--- 1. positional binding, OUT params, return code, result sets --->
<cfstoredproc procedure="KfTestFlow" datasource="cfsnippets" returncode="yes">
    <cfprocparam type="in" cfsqltype="CF_SQL_INTEGER" value="7">
    <cfprocparam type="in" cfsqltype="CF_SQL_VARCHAR" value="xyz">
    <cfprocparam type="out" cfsqltype="CF_SQL_INTEGER" variable="theSum">
    <cfprocparam type="out" cfsqltype="CF_SQL_VARCHAR" variable="theNote">
    <cfprocresult name="r1">
    <cfprocresult name="r9" resultset="9">
</cfstoredproc>
<cfoutput>1|#theSum#|#theNote#|#CFSTOREDPROC.StatusCode#|#r1.LastI#|#r1.Odds#|#r1.Label#|#IsDefined("r9")#|#IsNumeric(CFSTOREDPROC.ExecutionTime)#
</cfoutput>

<!--- 2. named binding with DBVARNAME, defaults, truncation to VARCHAR(5), no RETURNCODE --->
<cfstoredproc procedure="dbo.KfTestFlow" datasource="cfsnippets">
    <cfprocparam type="out" cfsqltype="CF_SQL_VARCHAR" variable="n2" dbvarname="@Note">
    <cfprocparam type="inout" cfsqltype="CF_SQL_INTEGER" variable="s2" value="5" dbvarname="@Sum">
    <cfprocparam cfsqltype="CF_SQL_INTEGER" value="3" dbvarname="Limit">
    <cfprocresult name="r2">
</cfstoredproc>
<cfoutput>2|#s2#|#n2#|#r2.Label#|#IsDefined("CFSTOREDPROC.StatusCode")#
</cfoutput>

<!--- 3. nested EXEC with OUTPUT and a return code --->
<cfstoredproc procedure="KfTestOuter" datasource="cfsnippets">
    <cfprocparam cfsqltype="CF_SQL_INTEGER" value="10">
    <cfprocresult name="inner" resultset="1">
    <cfprocresult name="outer" resultset="2">
</cfstoredproc>
<cfoutput>3|#inner.LastI#|#outer.RC#|#outer.S#|#outer.N#|#outer.Lvl#
</cfoutput>

<!--- 4. the seeded cfsnippets procedures --->
<cfstoredproc procedure="GetEmployeesByDept" datasource="cfsnippets" returncode="yes">
    <cfprocparam cfsqltype="CF_SQL_VARCHAR" value="Training">
    <cfprocresult name="tr" maxrows="2">
</cfstoredproc>
<cfoutput>4|#tr.RecordCount#|#CFSTOREDPROC.StatusCode GT 2#|#tr.ColumnList#
</cfoutput>
<cfstoredproc procedure="CountByDept" datasource="cfsnippets">
    <cfprocparam cfsqltype="CF_SQL_VARCHAR" value="Engineering">
    <cfprocparam type="out" cfsqltype="CF_SQL_INTEGER" variable="total">
    <cfprocresult name="c1">
    <cfprocresult name="c2" resultset="2">
</cfstoredproc>
<cfoutput>4|#c1.Department#|#c1.Employees EQ total#|#c2.Location#
</cfoutput>
<cftransaction>
    <cfstoredproc procedure="AddEmployee" datasource="cfsnippets" returncode="yes">
        <cfprocparam cfsqltype="CF_SQL_VARCHAR" value="Ada" dbvarname="@FirstName">
        <cfprocparam cfsqltype="CF_SQL_VARCHAR" value="Testcase" dbvarname="@LastName">
        <cfprocparam cfsqltype="CF_SQL_VARCHAR" value="Training" dbvarname="@Department">
        <cfprocparam type="out" cfsqltype="CF_SQL_INTEGER" variable="newID" dbvarname="@NewID">
    </cfstoredproc>
    <cfset firstStatus = CFSTOREDPROC.StatusCode>
    <cfquery name="chk" datasource="cfsnippets">SELECT LastName, Department FROM Employees WHERE Emp_ID = #newID#</cfquery>
    <cfstoredproc procedure="AddEmployee" datasource="cfsnippets" returncode="yes">
        <cfprocparam cfsqltype="CF_SQL_VARCHAR" value="Ada" dbvarname="@FirstName">
        <cfprocparam cfsqltype="CF_SQL_VARCHAR" value="Testcase" dbvarname="@LastName">
        <cfprocparam type="out" cfsqltype="CF_SQL_INTEGER" variable="againID" dbvarname="@NewID">
    </cfstoredproc>
    <cfoutput>4|#firstStatus#|#chk.LastName#|#chk.Department#|#CFSTOREDPROC.StatusCode#|#againID EQ newID#
</cfoutput>
    <cfstoredproc procedure="AddEmployee" datasource="cfsnippets" returncode="yes">
        <cfprocparam cfsqltype="CF_SQL_VARCHAR" value="Bo">
        <cfprocparam cfsqltype="CF_SQL_VARCHAR" value="Testcase">
        <cfprocparam cfsqltype="CF_SQL_VARCHAR" null="yes">
        <cfprocparam cfsqltype="CF_SQL_VARCHAR" null="yes">
        <cfprocparam cfsqltype="CF_SQL_VARCHAR" value="Nowhere">
        <cfprocparam cfsqltype="CF_SQL_MONEY" value="1">
        <cfprocparam type="out" cfsqltype="CF_SQL_INTEGER" variable="noID">
    </cfstoredproc>
    <cfoutput>4|#CFSTOREDPROC.StatusCode#|#noID#
</cfoutput>
    <cftransaction action="rollback"/>
</cftransaction>
<cfquery name="gone" datasource="cfsnippets">SELECT COUNT(*) AS n FROM Employees WHERE LastName = 'Testcase'</cfquery>
<cfoutput>4|#gone.n#
</cfoutput>

<!--- 5. CFQUERY: EXEC, {call}, T-SQL batches --->
<cfquery name="q5" datasource="cfsnippets">EXEC GetEmployeesByDept 'Training'</cfquery>
<cfquery name="q5b" datasource="cfsnippets">{call GetEmployeesByDept('Training')}</cfquery>
<cfquery name="q5c" datasource="cfsnippets">EXECUTE GetEmployeesByDept @Department = 'Training'</cfquery>
<cfoutput>5|#q5.RecordCount EQ q5b.RecordCount#|#q5.RecordCount EQ q5c.RecordCount#
</cfoutput>
<cfquery name="q6" datasource="cfsnippets">
DECLARE @d VARCHAR(30), @n INT, @when DATETIME;
SET @d = 'Engin' + 'eering';
SELECT @n = COUNT(*) FROM Employees WHERE Department = @d;
SET @when = {d '1999-12-31'};
IF @n > 0 AND @when IS NOT NULL
    SELECT @d AS Dept, @n AS N, @when AS W, NULL AS Nothing;
ELSE
    SELECT 'none' AS Dept
</cfquery>
<cfoutput>5|#q6.Dept#|#q6.N GT 0#|#q6.W#|[#q6.Nothing#]
</cfoutput>
<cfquery name="q7" datasource="cfsnippets">DECLARE @t INT; EXEC KfTestFlow 4, 'ab', @t OUTPUT, NULL; SELECT @t AS T, @@ROWCOUNT AS RC</cfquery>
<cfoutput>5|#q7.T#|#q7.RC#
</cfoutput>

<!--- 6. errors --->
<cfset tests = ArrayNew(1)>
<cfset ArrayAppend(tests, "EXEC NoSuchProc")>
<cfset ArrayAppend(tests, "EXEC KfTestFlow")>
<cfset ArrayAppend(tests, "EXEC KfTestFlow 1, 'a', 1, 'b', 5")>
<cfset ArrayAppend(tests, "DECLARE @x INT; EXEC KfTestFlow @x OUTPUT")>
<cfset ArrayAppend(tests, "EXEC KfTestFlow @Bogus = 1")>
<cfset ArrayAppend(tests, "EXEC KfTestFlow @Limit = 1, 'x'")>
<cfset ArrayAppend(tests, "SELECT @undeclared AS X")>
<cfset ArrayAppend(tests, "DECLARE @i INT; SET @i = 'abc'")>
<cfset ArrayAppend(tests, "DECLARE @i INT; DECLARE @i INT")>
<cfset ArrayAppend(tests, "{call GetEmployeesByDept(?)}")>
<cfset ArrayAppend(tests, "DROP PROCEDURE NoSuchProc")>
<cfset ArrayAppend(tests, "CREATE PROCEDURE Employees AS SELECT 1 AS X")>
<cfset ArrayAppend(tests, "CREATE PROCEDURE KfTestFlow AS SELECT 1 AS X")>
<cfset ArrayAppend(tests, "CREATE PROCEDURE KfBad @a FOOTYPE AS SELECT 1 AS X")>
<cfset ArrayAppend(tests, "CREATE PROCEDURE KfBad AS BEGIN SELECT 1 AS X")>
<cfset ArrayAppend(tests, "CREATE PROCEDURE KfBad AS BREAK")>
<cfset ArrayAppend(tests, "RAISERROR('Custom failure %s/%d', 16, 1, 'abc', 42)")>
<cfloop from="1" to="#ArrayLen(tests)#" index="i">
    <cftry>
        <cfquery name="e" datasource="cfsnippets">#PreserveSingleQuotes(tests[i])#</cfquery>
        <cfoutput>6|#i#|no error
</cfoutput>
        <cfcatch type="database"><cfoutput>6|#i#|#cfcatch.sqlstate#|#Replace(cfcatch.message, "[Gibson][KoldFusion Flat-File Driver] ", "")#
</cfoutput></cfcatch>
    </cftry>
</cfloop>
<cftry>
    <cfstoredproc procedure="GetEmployee" datasource="cfsnippets"><cfprocparam cfsqltype="CF_SQL_INTEGER" value="99999"></cfstoredproc>
    <cfcatch type="database"><cfoutput>6|#cfcatch.message#|#cfcatch.NativeErrorCode#
</cfoutput></cfcatch>
</cftry>
<cftry>
    <cfstoredproc procedure="KfTestFlow" datasource="cfsnippets">
        <cfprocparam cfsqltype="CF_SQL_INTEGER" value="1.5">
    </cfstoredproc>
    <cfcatch><cfoutput>6|#cfcatch.message#
</cfoutput></cfcatch>
</cftry>
<cftry>
    <cfstoredproc procedure="KfTestFlow" datasource="cfsnippets">
        <cfprocparam cfsqltype="CF_SQL_STRING" value="1">
    </cfstoredproc>
    <cfcatch><cfoutput>6|#cfcatch.message#
</cfoutput></cfcatch>
</cftry>
<cftry>
    <cfstoredproc procedure="KfTestFlow" datasource="cfsnippets">
        <cfprocparam type="out" cfsqltype="CF_SQL_INTEGER">
    </cfstoredproc>
    <cfcatch><cfoutput>6|#cfcatch.message#|#cfcatch.detail#
</cfoutput></cfcatch>
</cftry>
<cftry>
    <cfprocparam cfsqltype="CF_SQL_INTEGER" value="1">
    <cfcatch><cfoutput>6|#cfcatch.message#
</cfoutput></cfcatch>
</cftry>
<cftry>
    <cfstoredproc procedure="KfTestFlow" datasource="cfsnippets" blockfactor="500"></cfstoredproc>
    <cfcatch><cfoutput>6|#cfcatch.detail#
</cfoutput></cfcatch>
</cftry>
<cfquery datasource="cfsnippets">DROP PROCEDURE KfTestFlow, KfTestOuter</cfquery>
<cftry>
    <cfstoredproc procedure="KfTestFlow" datasource="cfsnippets"></cfstoredproc>
    <cfcatch type="database"><cfoutput>7|dropped|#cfcatch.sqlstate#
</cfoutput></cfcatch>
</cftry>

<!--- 8. GetHttpRequestData and the K2 Server functions --->
<cfset req = GetHttpRequestData()>
<cfoutput>8|#req.Method#|#Left(req.Protocol, 5)#|#Len(req.Content)#|#IsStruct(req.Headers)#
8|#IsBoolean(IsK2ServerOnline())#|#IsK2ServerABroker()#|#IsNumeric(GetK2ServerDocCount())#|#GetK2ServerDocCountLimit() GT 0#|#IsBoolean(IsK2ServerDocCountExceeded())#|#ListLen(GetK2ServerCollections()) GTE 0#
</cfoutput>
