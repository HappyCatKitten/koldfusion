<cfset d = CreateODBCDate(CreateDate(2026,10,1))>
<cfquery name="q1" datasource="demos">SELECT COUNT(*) AS n FROM event WHERE EventDate > #d#</cfquery>
<cfquery name="q2" datasource="demos">SELECT COUNT(*) AS n FROM event WHERE EventDate > #CreateODBCDate(Now())#</cfquery>
<cfoutput>#q1.n# #q2.n#</cfoutput>
