<CFQUERY NAME="GetPay" DATASOURCE="cfsnippets" MAXROWS="6">
SELECT LastName, Salary FROM Employees ORDER BY LastName
</CFQUERY>
<PRE>
<CFOUTPUT QUERY="GetPay">#LJustify(LastName, 14)##RJustify(DollarFormat(Salary), 12)#
</CFOUTPUT></PRE>
