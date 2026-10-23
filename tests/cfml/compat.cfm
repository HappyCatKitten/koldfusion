<cfsetting enablecfoutputonly="yes">
<cfset a = 1 /><cfset b = 4/2 />
<cfoutput>#a#|#b#|[#Evaluate("")#]|[#IIf(1 IS 2, DE("s"), "")#]|#("10/22/1999" EQ "1999-10-22")#|#("10 - 22 - 2026" EQ "10-22-2026")#|#("abc" EQ "ABC")#
</cfoutput>
<cfset attributes = "local"><cfoutput>#attributes#
</cfoutput>
<cfquery name="q" datasource="cfsnippets">SELECT COUNT(*) AS n FROM Employees WHERE StartDate < #CreateODBCDate(CreateDate(2030,1,1))#</cfquery>
<cfset nm = "O'Malley"><cfquery name="q2" datasource="cfsnippets">SELECT COUNT(*) AS n FROM Employees WHERE LastName = '#nm#'</cfquery>
<cfoutput>#q.n GT 0#|#q2.n#|#FileExists("C:\CFUSION\registry\kf.registry")#
</cfoutput>
