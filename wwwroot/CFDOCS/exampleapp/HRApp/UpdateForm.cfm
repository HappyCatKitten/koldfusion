<!---
	UpdateForm.cfm - edit an employee. The primary key travels in a hidden
	field named Employee_ID, which is how CFUPDATE knows which row to change.
	  ?Employee_ID=n
--->
<CFPARAM NAME="URL.Employee_ID" DEFAULT="0">
<CFSET PageTitle = "Update an Employee">
<CFQUERY NAME="GetEmployee" DATASOURCE="#Request.DSN#">
	SELECT * FROM Employees WHERE Employee_ID = #Val(URL.Employee_ID)#
</CFQUERY>
<CFIF GetEmployee.RecordCount EQ 0>
	<CFLOCATION URL="UpdateList.cfm" ADDTOKEN="No">
</CFIF>
<CFQUERY NAME="GetDepartments" DATASOURCE="#Request.DSN#">
	SELECT Department_ID, Department_Name FROM Departments ORDER BY Department_Name
</CFQUERY>

<CFINCLUDE TEMPLATE="toolbar.cfm">

<CFFORM ACTION="UpdateAction.cfm" METHOD="POST" NAME="UpdateForm">
<INPUT TYPE="Hidden" NAME="FirstName_required" VALUE="First name is required.">
<INPUT TYPE="Hidden" NAME="LastName_required" VALUE="Last name is required.">
<INPUT TYPE="Hidden" NAME="StartDate_required" VALUE="Start date is required.">
<INPUT TYPE="Hidden" NAME="StartDate_date" VALUE="Start date must be a valid date.">
<INPUT TYPE="Hidden" NAME="Salary_required" VALUE="Salary is required.">
<INPUT TYPE="Hidden" NAME="Salary_float" VALUE="Salary must be a number (no dollar sign or commas).">
<CFOUTPUT QUERY="GetEmployee">
<INPUT TYPE="Hidden" NAME="Employee_ID" VALUE="#Employee_ID#">
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>Employee ID:</FONT></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2><B>#Employee_ID#</B></FONT></TD></TR>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>First Name:</FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="FirstName" VALUE="#FirstName#" SIZE="20" MAXLENGTH="30" REQUIRED="Yes" MESSAGE="First name is required."></TD></TR>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>Last Name:</FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="LastName" VALUE="#LastName#" SIZE="25" MAXLENGTH="30" REQUIRED="Yes" MESSAGE="Last name is required."></TD></TR>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>Department:</FONT></TD>
	<TD><CFSELECT NAME="Department_ID" QUERY="GetDepartments" VALUE="Department_ID" DISPLAY="Department_Name" SELECTED="#Department_ID#"></CFSELECT></TD></TR>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>Start Date:</FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="StartDate" VALUE="#DateFormat(StartDate, 'mm/dd/yyyy')#" SIZE="12" MAXLENGTH="10" REQUIRED="Yes" VALIDATE="date" MESSAGE="Start date must be a valid date (mm/dd/yyyy)."></TD></TR>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>Salary:</FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="Salary" VALUE="#Salary#" SIZE="10" MAXLENGTH="10" REQUIRED="Yes" VALIDATE="float" MESSAGE="Salary must be a number."></TD></TR>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>Contract:</FONT></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2>
	<CFINPUT TYPE="Radio" NAME="Contract" VALUE="Yes" CHECKED="#YesNoFormat(Contract)#"> Yes
	<CFINPUT TYPE="Radio" NAME="Contract" VALUE="No" CHECKED="#YesNoFormat(NOT Contract)#"> No</FONT></TD></TR>
<TR><TD></TD><TD><INPUT TYPE="Submit" VALUE="Update Employee"> <INPUT TYPE="Button" VALUE="Cancel" onClick="location.href='UpdateList.cfm'"></TD></TR>
</TABLE>
</CFOUTPUT>
</CFFORM>

<CFINCLUDE TEMPLATE="footer.cfm">
