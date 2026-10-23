<CFSILENT>
  This text, the blank lines below and even the CFOUTPUT are discarded.
  <CFQUERY NAME="Staff" DATASOURCE="cfsnippets">
  SELECT Department, Salary FROM Employees
  </CFQUERY>
  <CFSET Payroll = ArraySum(ListToArray(ValueList(Staff.Salary)))>
  <CFSET Average = Payroll / Staff.RecordCount>
  <CFOUTPUT>You will never see this line.</CFOUTPUT>
</CFSILENT>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>Employees</TD><TD ALIGN=RIGHT>#Staff.RecordCount#</TD></TR>
<TR><TD>Annual payroll</TD><TD ALIGN=RIGHT>#DollarFormat(Payroll)#</TD></TR>
<TR><TD>Average salary</TD><TD ALIGN=RIGHT>#DollarFormat(Average)#</TD></TR>
</TABLE>
<P>The variables set inside CFSILENT are available afterwards.</P>
</CFOUTPUT>
