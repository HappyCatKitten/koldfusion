<CFQUERY NAME="GetPay" DATASOURCE="cfsnippets" MAXROWS="5">
SELECT FirstName, LastName, Salary FROM Employees ORDER BY LastName
</CFQUERY>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Employee</TH><TH>Salary</TH><TH>Above (below) $50,000</TH></TR>
<CFOUTPUT QUERY="GetPay">
<TR><TD>#FirstName# #LastName#</TD>
    <TD ALIGN="right">#DollarFormat(Salary)#</TD>
    <TD ALIGN="right">#DollarFormat(Salary - 50000)#</TD></TR>
</CFOUTPUT>
</TABLE>
