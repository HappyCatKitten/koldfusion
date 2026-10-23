<!---
	InsertForm.cfm - add an employee.
	The form field names match the column names in the Employees table,
	so InsertAction.cfm can save everything with one CFINSERT tag.
	Validation:
	  browser - CFINPUT REQUIRED / VALIDATE generate JavaScript
	  server  - the hidden _required, _date and _float fields
--->
<CFSET PageTitle = "Add an Employee">
<CFQUERY NAME="GetDepartments" DATASOURCE="#Request.DSN#">
	SELECT Department_ID, Department_Name FROM Departments ORDER BY Department_Name
</CFQUERY>

<CFINCLUDE TEMPLATE="toolbar.cfm">

<CFFORM ACTION="InsertAction.cfm" METHOD="POST" NAME="InsertForm">
<INPUT TYPE="Hidden" NAME="FirstName_required" VALUE="First name is required.">
<INPUT TYPE="Hidden" NAME="LastName_required" VALUE="Last name is required.">
<INPUT TYPE="Hidden" NAME="StartDate_required" VALUE="Start date is required.">
<INPUT TYPE="Hidden" NAME="StartDate_date" VALUE="Start date must be a valid date.">
<INPUT TYPE="Hidden" NAME="Salary_required" VALUE="Salary is required.">
<INPUT TYPE="Hidden" NAME="Salary_float" VALUE="Salary must be a number (no dollar sign or commas).">
<CFOUTPUT>
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>First Name:</FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="FirstName" SIZE="20" MAXLENGTH="30" REQUIRED="Yes" MESSAGE="First name is required."></TD></TR>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>Last Name:</FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="LastName" SIZE="25" MAXLENGTH="30" REQUIRED="Yes" MESSAGE="Last name is required."></TD></TR>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>Department:</FONT></TD>
	<TD><CFSELECT NAME="Department_ID" QUERY="GetDepartments" VALUE="Department_ID" DISPLAY="Department_Name" REQUIRED="Yes" MESSAGE="Please choose a department."></CFSELECT></TD></TR>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>Start Date:</FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="StartDate" VALUE="#DateFormat(Now(), 'mm/dd/yyyy')#" SIZE="12" MAXLENGTH="10" REQUIRED="Yes" VALIDATE="date" MESSAGE="Start date must be a valid date (mm/dd/yyyy)."></TD></TR>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>Salary:</FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="Salary" SIZE="10" MAXLENGTH="10" REQUIRED="Yes" VALIDATE="float" MESSAGE="Salary must be a number."></TD></TR>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>Contract:</FONT></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2>
	<CFINPUT TYPE="Radio" NAME="Contract" VALUE="Yes"> Yes
	<CFINPUT TYPE="Radio" NAME="Contract" VALUE="No" CHECKED="Yes"> No</FONT></TD></TR>
<TR><TD></TD><TD><INPUT TYPE="Submit" VALUE="Add Employee"> <INPUT TYPE="Reset" VALUE="Clear Form"></TD></TR>
</TABLE>
</CFOUTPUT>
</CFFORM>

<CFINCLUDE TEMPLATE="footer.cfm">
