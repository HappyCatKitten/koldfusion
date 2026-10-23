<cfsetting enablecfoutputonly="yes">
<cfset q = QueryNew("name,dept")>
<cfset QueryAddRow(q, 4)>
<cfset QuerySetCell(q, "name", "Ann", 1)><cfset QuerySetCell(q, "dept", "IT", 1)>
<cfset QuerySetCell(q, "name", "Bob", 2)><cfset QuerySetCell(q, "dept", "IT", 2)>
<cfset QuerySetCell(q, "name", "Cy", 3)><cfset QuerySetCell(q, "dept", "HR", 3)>
<cfset QuerySetCell(q, "name", "Di", 4)><cfset QuerySetCell(q, "dept", "HR", 4)>
<cfoutput query="q" group="dept">[#dept#:<cfoutput>#name#</cfoutput>]</cfoutput>
<cfoutput>|#q.RecordCount#|#q.ColumnList#|#ValueList(q.name)#|#QuotedValueList(q.dept)#|#q.name[3]#
</cfoutput>
<cfloop query="q" startrow="2" endrow="3"><cfoutput>#CurrentRow#=#name# </cfoutput></cfloop>
<cfquery name="db" datasource="cfsnippets">SELECT COUNT(*) AS N, MAX(Emp_ID) AS M FROM Employees WHERE Department = 'Sales'</cfquery>
<cfoutput>|#db.N GT 0#
</cfoutput>
