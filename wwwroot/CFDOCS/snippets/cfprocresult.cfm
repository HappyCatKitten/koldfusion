<CFSTOREDPROC PROCEDURE="CountByDept" DATASOURCE="cfsnippets">
  <CFPROCPARAM TYPE="In" CFSQLTYPE="CF_SQL_VARCHAR" VALUE="Engineering">
  <CFPROCPARAM TYPE="Out" CFSQLTYPE="CF_SQL_INTEGER" VARIABLE="Total">
  <CFPROCRESULT NAME="Depts" RESULTSET="1">
  <CFPROCRESULT NAME="Offices" RESULTSET="2" MAXROWS="1">
  <CFPROCRESULT NAME="Third" RESULTSET="3">
</CFSTOREDPROC>
<CFOUTPUT>
<P>Engineering has #Total# employees and a payroll of #DollarFormat(Depts.Payroll)#.
It is based in #Offices.Location#.</P>
<P>IsDefined("Third"): #IsDefined("Third")# (CountByDept returns two result sets).</P>
</CFOUTPUT>

<!--- The same procedure's first result set, through CFQUERY --->
<CFQUERY NAME="ViaQuery" DATASOURCE="cfsnippets">
EXEC CountByDept @Department = 'Sales', @Total = NULL
</CFQUERY>
<CFOUTPUT QUERY="ViaQuery"><P>Via CFQUERY: #Department#, #Employees# employees.</P></CFOUTPUT>
