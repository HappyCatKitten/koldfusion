<!--- Pay employees in order of seniority until the budget runs out --->
<CFSET Budget = 500000>
<CFSET Spent = 0>
<CFQUERY NAME="Staff" DATASOURCE="cfsnippets">
SELECT FirstName, LastName, Salary FROM Employees ORDER BY StartDate
</CFQUERY>

<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Employee</TH><TH>Salary</TH><TH>Spent so far</TH></TR>
<CFLOOP QUERY="Staff">
  <CFIF Spent + Salary GT Budget>
    </TABLE>
    <CFOUTPUT><P><B>Budget of #DollarFormat(Budget)# exhausted at row #CurrentRow#.
    #FirstName# #LastName# and the rest will have to wait.</B></P></CFOUTPUT>
    <CFABORT>
  </CFIF>
  <CFSET Spent = Spent + Salary>
  <CFOUTPUT><TR><TD>#FirstName# #LastName#</TD><TD>#DollarFormat(Salary)#</TD><TD>#DollarFormat(Spent)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<P>Everybody got paid. (You will not see this line: the budget is too small.)</P>
