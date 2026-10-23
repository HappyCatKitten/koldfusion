<!--- Department head counts: two result sets, an output parameter and a status code --->
<CFSTOREDPROC PROCEDURE="CountByDept" DATASOURCE="cfsnippets" RETURNCODE="Yes">
  <CFPROCPARAM TYPE="In" CFSQLTYPE="CF_SQL_VARCHAR" DBVARNAME="@Department" NULL="Yes">
  <CFPROCPARAM TYPE="Out" CFSQLTYPE="CF_SQL_INTEGER" DBVARNAME="@Total" VARIABLE="TotalStaff">
  <CFPROCRESULT NAME="HeadCount" RESULTSET="1">
  <CFPROCRESULT NAME="Offices" RESULTSET="2">
</CFSTOREDPROC>

<CFOUTPUT>
<P>CountByDept returned status #CFSTOREDPROC.StatusCode# in #CFSTOREDPROC.ExecutionTime# ms:
#TotalStaff# employees in #HeadCount.RecordCount# departments.</P>
</CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR BGCOLOR="#CCCCCC"><TH>Department</TH><TH>Employees</TH><TH>Payroll</TH></TR>
<CFOUTPUT QUERY="HeadCount">
<TR><TD>#Department#</TD><TD ALIGN="right">#Employees#</TD><TD ALIGN="right">#DollarFormat(Payroll)#</TD></TR>
</CFOUTPUT>
</TABLE>
<P>Offices:
<CFOUTPUT QUERY="Offices">#Dept_Name# (#Location#)<CFIF CurrentRow LT RecordCount>, </CFIF></CFOUTPUT></P>
