<CFTRY>
  <CFREPORT REPORT="c:\reports\salaries.rpt" ORDERBY="Department">
  </CFREPORT>
  <CFCATCH TYPE="Application">
    <CFOUTPUT><P><I>#CFCATCH.Detail#</I> Here is a home-made report instead.</P></CFOUTPUT>
    <CFQUERY NAME="Pay" DATASOURCE="cfsnippets">
    SELECT Department, Salary FROM Employees ORDER BY Department
    </CFQUERY>
    <TABLE BORDER=1 CELLPADDING=3>
    <TR BGCOLOR="#CCCCFF"><TH>Department</TH><TH>Staff</TH><TH>Payroll</TH></TR>
    <CFOUTPUT QUERY="Pay" GROUP="Department">
      <CFSET Total = 0><CFSET Staff = 0>
      <CFOUTPUT><CFSET Total = Total + Salary><CFSET Staff = Staff + 1></CFOUTPUT>
      <TR><TD>#Department#</TD><TD ALIGN=RIGHT>#Staff#</TD><TD ALIGN=RIGHT>#DollarFormat(Total)#</TD></TR>
    </CFOUTPUT>
    </TABLE>
  </CFCATCH>
</CFTRY>
