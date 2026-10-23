<!---
	EmpList.cfm - every employee, with department and location
	  ?sort=name|dept|start|salary
--->
<CFPARAM NAME="URL.sort" DEFAULT="name">
<CFSET PageTitle = "Employee List">
<CFSWITCH EXPRESSION="#URL.sort#">
	<CFCASE VALUE="dept"><CFSET OrderBy = "d.Department_Name, e.LastName"></CFCASE>
	<CFCASE VALUE="start"><CFSET OrderBy = "e.StartDate, e.LastName"></CFCASE>
	<CFCASE VALUE="salary"><CFSET OrderBy = "e.Salary DESC, e.LastName"></CFCASE>
	<CFDEFAULTCASE><CFSET OrderBy = "e.LastName, e.FirstName"></CFDEFAULTCASE>
</CFSWITCH>

<CFQUERY NAME="GetEmployees" DATASOURCE="#Request.DSN#">
	SELECT e.Employee_ID, e.FirstName, e.LastName, e.StartDate, e.Salary, e.Contract,
	       d.Department_Name, d.Location
	FROM Employees e, Departments d
	WHERE e.Department_ID = d.Department_ID
	ORDER BY #OrderBy#
</CFQUERY>

<CFINCLUDE TEMPLATE="toolbar.cfm">

<CFSET Payroll = 0>
<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0>
<CFOUTPUT>
<TR BGCOLOR="##CCCCCC">
	<TD><FONT FACE="#Request.Font#" SIZE=2><B><A HREF="EmpList.cfm?sort=name">Name</A></B></FONT></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2><B><A HREF="EmpList.cfm?sort=dept">Department</A></B></FONT></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2><B>Location</B></FONT></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2><B><A HREF="EmpList.cfm?sort=start">Start Date</A></B></FONT></TD>
	<TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B><A HREF="EmpList.cfm?sort=salary">Salary</A></B></FONT></TD>
	<TD ALIGN=CENTER><FONT FACE="#Request.Font#" SIZE=2><B>Contract</B></FONT></TD>
</TR>
</CFOUTPUT>
<CFOUTPUT QUERY="GetEmployees">
<CFSET Payroll = Payroll + Salary>
<TR BGCOLOR="###IIf(CurrentRow MOD 2, DE('FFFFFF'), DE('EEEEEE'))#">
	<TD><FONT FACE="#Request.Font#" SIZE=2><A HREF="UpdateForm.cfm?Employee_ID=#Employee_ID#">#LastName#, #FirstName#</A></FONT></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2>#Department_Name#</FONT></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2>#Location#</FONT></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2>#DateFormat(StartDate, "mm/dd/yyyy")#</FONT></TD>
	<TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2>#DollarFormat(Salary)#</FONT></TD>
	<TD ALIGN=CENTER><FONT FACE="#Request.Font#" SIZE=2>#YesNoFormat(Contract)#</FONT></TD>
</TR>
</CFOUTPUT>
<CFOUTPUT>
<TR><TD COLSPAN=4><FONT FACE="#Request.Font#" SIZE=2><B>#GetEmployees.RecordCount# employees</B></FONT></TD>
	<TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>#DollarFormat(Payroll)#</B></FONT></TD><TD></TD></TR>
</CFOUTPUT>
</TABLE>

<CFINCLUDE TEMPLATE="footer.cfm">
