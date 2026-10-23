<CFSET Wanted = ListQualify("Sales,Marketing", "'")>
<CFSET Where = "Department IN (#Wanted#)">
<CFQUERY NAME="Staff" DATASOURCE="cfsnippets">
SELECT FirstName, LastName, Department FROM Employees
WHERE #PreserveSingleQuotes(Where)#
ORDER BY Department, LastName
</CFQUERY>
<CFOUTPUT><P>WHERE #Where# finds #Staff.RecordCount# people:</CFOUTPUT>
<UL>
<CFOUTPUT QUERY="Staff">
  <LI>#FirstName# #LastName# (#Department#)
</CFOUTPUT>
</UL>
