<CFQUERY NAME="Staff" DATASOURCE="cfsnippets" MAXROWS="6">
SELECT FirstName, LastName, Department, Salary
FROM Employees
ORDER BY LastName
</CFQUERY>

<H4>HTML table</H4>
<CFTABLE QUERY="Staff" HTMLTABLE BORDER COLHEADERS>
  <CFCOL HEADER="Name" TEXT="#FirstName# #LastName#">
  <CFCOL HEADER="Department" TEXT="#Department#">
  <CFCOL HEADER="Salary" ALIGN="Right" TEXT="#DollarFormat(Salary)#">
</CFTABLE>

<H4>Preformatted text, rows 2 to 4</H4>
<CFTABLE QUERY="Staff" COLHEADERS STARTROW="2" MAXROWS="3" COLSPACING="3">
  <CFCOL HEADER="Last name" WIDTH="12" TEXT="#LastName#">
  <CFCOL HEADER="Department" WIDTH="12" TEXT="#Department#">
  <CFCOL HEADER="Salary" WIDTH="12" ALIGN="Right" TEXT="#DollarFormat(Salary)#">
</CFTABLE>
