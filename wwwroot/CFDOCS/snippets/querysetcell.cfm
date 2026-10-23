<CFQUERY NAME="GetStaff" DATASOURCE="cfsnippets">
SELECT TOP 4 FirstName, LastName, Salary
FROM Employees
ORDER BY LastName
</CFQUERY>
<!--- Give everybody a Y2K bonus (in memory only!) --->
<CFLOOP QUERY="GetStaff">
  <CFSET Temp = QuerySetCell(GetStaff, "Salary", Salary + 2000, CurrentRow)>
</CFLOOP>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Name</TH><TH>Salary with bonus</TH></TR>
<CFOUTPUT QUERY="GetStaff">
<TR><TD>#FirstName# #LastName#</TD><TD ALIGN="RIGHT">#DollarFormat(Salary)#</TD></TR>
</CFOUTPUT>
</TABLE>
