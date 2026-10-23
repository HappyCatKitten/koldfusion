<CFQUERY NAME="Staff" DATASOURCE="cfsnippets">
SELECT FirstName, LastName, Department, Salary, Contract
FROM Employees WHERE Department IN ('Sales', 'Engineering')
ORDER BY Salary DESC
</CFQUERY>

<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Name</TH><TH>Salary</TH><TH>Band</TH><TH>Notes</TH></TR>
<CFOUTPUT QUERY="Staff">
<TR>
  <TD>#FirstName# #LastName#</TD>
  <TD ALIGN="RIGHT">#DollarFormat(Salary)#</TD>
  <CFIF Salary GTE 75000>
    <TD BGCOLOR="##CCFFCC">Senior</TD>
  <CFELSEIF Salary GTE 55000>
    <TD BGCOLOR="##FFFFCC">Regular</TD>
  <CFELSE>
    <TD BGCOLOR="##FFE0E0">Junior</TD>
  </CFIF>
  <TD><CFIF Contract>Contractor</CFIF><CFIF Department IS "Sales" AND LastName CONTAINS "a"> Sales, with an "a"</CFIF>&nbsp;</TD>
</TR>
</CFOUTPUT>
</TABLE>
