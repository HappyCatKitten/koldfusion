<!---
	UpdateList.cfm - pick an employee to update
--->
<CFSET PageTitle = "Update an Employee">
<CFQUERY NAME="GetEmployees" DATASOURCE="#Request.DSN#">
	SELECT e.Employee_ID, e.FirstName, e.LastName, d.Department_Name
	FROM Employees e, Departments d
	WHERE e.Department_ID = d.Department_ID
	ORDER BY e.LastName, e.FirstName
</CFQUERY>

<CFINCLUDE TEMPLATE="toolbar.cfm">

<CFOUTPUT><FONT FACE="#Request.Font#" SIZE=2>Choose an employee, then press <B>Edit</B>.</FONT></CFOUTPUT>
<FORM ACTION="UpdateForm.cfm" METHOD="GET">
<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=0>
<CFOUTPUT QUERY="GetEmployees">
<TR BGCOLOR="###IIf(CurrentRow MOD 2, DE('FFFFFF'), DE('EEEEEE'))#">
	<TD><INPUT TYPE="Radio" NAME="Employee_ID" VALUE="#Employee_ID#"<CFIF CurrentRow EQ 1> CHECKED</CFIF>></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2>#LastName#, #FirstName#</FONT></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2>#Department_Name#</FONT></TD>
</TR>
</CFOUTPUT>
</TABLE>
<P><INPUT TYPE="Submit" VALUE="Edit"></P>
</FORM>

<CFINCLUDE TEMPLATE="footer.cfm">
