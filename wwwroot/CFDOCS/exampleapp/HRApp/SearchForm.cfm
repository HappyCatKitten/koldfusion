<!---
	SearchForm.cfm - search for employees. Results appear on SearchAction.cfm.
--->
<CFSET PageTitle = "Search for Employees">
<CFQUERY NAME="GetDepartments" DATASOURCE="#Request.DSN#">
	SELECT Department_ID, Department_Name FROM Departments ORDER BY Department_Name
</CFQUERY>

<CFINCLUDE TEMPLATE="toolbar.cfm">

<CFOUTPUT>
<FONT FACE="#Request.Font#" SIZE=2>Leave a field blank to ignore it.</FONT>
<FORM ACTION="SearchAction.cfm" METHOD="POST">
<!--- the salary fields must be numbers if they are filled in --->
<INPUT TYPE="Hidden" NAME="MinSalary_float" VALUE="Minimum salary must be a number.">
<INPUT TYPE="Hidden" NAME="MaxSalary_float" VALUE="Maximum salary must be a number.">
<INPUT TYPE="Hidden" NAME="StartedAfter_date" VALUE="Started-after must be a date.">
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>Last name begins with:</FONT></TD>
	<TD><INPUT TYPE="Text" NAME="LastName" SIZE=20 MAXLENGTH=30></TD></TR>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>Department:</FONT></TD>
	<TD><SELECT NAME="Department_ID">
		<OPTION VALUE="">All departments
		<CFLOOP QUERY="GetDepartments"><OPTION VALUE="#Department_ID#">#Department_Name#</CFLOOP>
	</SELECT></TD></TR>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>Salary between:</FONT></TD>
	<TD><INPUT TYPE="Text" NAME="MinSalary" SIZE=8> <FONT FACE="#Request.Font#" SIZE=2>and</FONT> <INPUT TYPE="Text" NAME="MaxSalary" SIZE=8></TD></TR>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>Started after:</FONT></TD>
	<TD><INPUT TYPE="Text" NAME="StartedAfter" SIZE=10> <FONT FACE="#Request.Font#" SIZE=1>mm/dd/yyyy</FONT></TD></TR>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>Contractors:</FONT></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2>
	<INPUT TYPE="Radio" NAME="Contract" VALUE="" CHECKED> Everyone
	<INPUT TYPE="Radio" NAME="Contract" VALUE="Yes"> Contractors only
	<INPUT TYPE="Radio" NAME="Contract" VALUE="No"> Staff only</FONT></TD></TR>
<TR><TD></TD><TD><INPUT TYPE="Submit" VALUE="Search"> <INPUT TYPE="Reset" VALUE="Clear"></TD></TR>
</TABLE>
</FORM>
</CFOUTPUT>

<CFINCLUDE TEMPLATE="footer.cfm">
