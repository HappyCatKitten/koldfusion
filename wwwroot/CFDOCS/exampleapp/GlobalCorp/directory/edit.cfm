<!---
	directory/edit.cfm - add or update a directory entry (admins only)
	  edit.cfm            blank form, adds a new employee
	  edit.cfm?Emp_ID=n   form filled in with an existing entry
	Validation happens twice:
	  * in the browser, by the JavaScript CFFORM generates for CFINPUT
	  * on the server, by the hidden _required and _date fields, which
	    work even when JavaScript is turned off
--->
<CFPARAM NAME="URL.Emp_ID" DEFAULT="0">
<CFSET Section = "directory">

<CFIF NOT Request.IsAdmin>
	<CFSET PageTitle = "Not Authorized">
	<CFINCLUDE TEMPLATE="../header.cfm">
	<P>Only directory administrators can add or change entries.
	Log out and log back in as <B>mfeld</B> or <B>lybarra</B> to try this page.</P>
	<CFINCLUDE TEMPLATE="../footer.cfm">
	<CFABORT>
</CFIF>

<CFQUERY NAME="GetDepartments" DATASOURCE="#Request.DSN#">
	SELECT Dept_ID, DeptName FROM Departments ORDER BY DeptName
</CFQUERY>

<CFQUERY NAME="GetEmployee" DATASOURCE="#Request.DSN#">
	SELECT * FROM Employees WHERE Emp_ID = #Val(URL.Emp_ID)#
</CFQUERY>

<CFIF GetEmployee.RecordCount>
	<CFSET PageTitle = "Update Directory Entry">
	<CFSET f_Emp_ID = GetEmployee.Emp_ID>
	<CFSET f_FirstName = GetEmployee.FirstName>
	<CFSET f_LastName = GetEmployee.LastName>
	<CFSET f_Title = GetEmployee.Title>
	<CFSET f_Dept_ID = GetEmployee.Dept_ID>
	<CFSET f_Email = GetEmployee.Email>
	<CFSET f_Phone = GetEmployee.Phone>
	<CFSET f_Office = GetEmployee.Office>
	<CFSET f_StartDate = DateFormat(GetEmployee.StartDate, "mm/dd/yyyy")>
	<CFSET f_Photo = GetEmployee.Photo>
	<CFSET f_Notes = GetEmployee.Notes>
<CFELSE>
	<CFSET PageTitle = "Add a New Employee">
	<CFSET f_Emp_ID = 0>
	<CFSET f_FirstName = "">
	<CFSET f_LastName = "">
	<CFSET f_Title = "">
	<CFSET f_Dept_ID = GetDepartments.Dept_ID>
	<CFSET f_Email = "">
	<CFSET f_Phone = "555-0100 x">
	<CFSET f_Office = "">
	<CFSET f_StartDate = DateFormat(Now(), "mm/dd/yyyy")>
	<CFSET f_Photo = "photo_1.gif">
	<CFSET f_Notes = "">
</CFIF>

<CFINCLUDE TEMPLATE="../header.cfm">

<CFOUTPUT>
<P>Fields marked <FONT COLOR="##CC0000">*</FONT> are required.</P>
</CFOUTPUT>
<CFFORM ACTION="save.cfm" METHOD="POST" NAME="EmployeeForm">
<CFOUTPUT>
<INPUT TYPE="Hidden" NAME="Emp_ID" VALUE="#f_Emp_ID#">
<!--- server-side validation rules --->
<INPUT TYPE="Hidden" NAME="FirstName_required" VALUE="First name is required.">
<INPUT TYPE="Hidden" NAME="LastName_required" VALUE="Last name is required.">
<INPUT TYPE="Hidden" NAME="StartDate_required" VALUE="Start date is required.">
<INPUT TYPE="Hidden" NAME="StartDate_date" VALUE="Start date must be a date, like 06/15/1999.">
<INPUT TYPE="Hidden" NAME="Dept_ID_integer" VALUE="Please choose a department.">

<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><FONT COLOR="##CC0000">*</FONT><B>First name:</B></FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="FirstName" VALUE="#f_FirstName#" SIZE="20" MAXLENGTH="30" REQUIRED="Yes" MESSAGE="Please enter a first name."></TD></TR>
<TR><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><FONT COLOR="##CC0000">*</FONT><B>Last name:</B></FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="LastName" VALUE="#f_LastName#" SIZE="25" MAXLENGTH="30" REQUIRED="Yes" MESSAGE="Please enter a last name."></TD></TR>
<TR><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>Title:</B></FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="Title" VALUE="#f_Title#" SIZE="40" MAXLENGTH="60"></TD></TR>
<TR><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><FONT COLOR="##CC0000">*</FONT><B>Department:</B></FONT></TD>
	<TD><CFSELECT NAME="Dept_ID" QUERY="GetDepartments" VALUE="Dept_ID" DISPLAY="DeptName" SELECTED="#f_Dept_ID#" REQUIRED="Yes" MESSAGE="Please choose a department."></CFSELECT></TD></TR>
<TR><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>E-mail:</B></FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="Email" VALUE="#f_Email#" SIZE="35" MAXLENGTH="60"></TD></TR>
<TR><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>Phone:</B></FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="Phone" VALUE="#f_Phone#" SIZE="20" MAXLENGTH="20"></TD></TR>
<TR><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>Office:</B></FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="Office" VALUE="#f_Office#" SIZE="10" MAXLENGTH="20"></TD></TR>
<TR><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><FONT COLOR="##CC0000">*</FONT><B>Start date:</B></FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="StartDate" VALUE="#f_StartDate#" SIZE="12" MAXLENGTH="10" REQUIRED="Yes" VALIDATE="date" MESSAGE="Please enter the start date as mm/dd/yyyy.">
	<FONT FACE="#Request.Font#" SIZE=1>mm/dd/yyyy</FONT></TD></TR>
<TR VALIGN=TOP><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>Photo:</B></FONT></TD>
	<TD><CFLOOP INDEX="p" FROM="1" TO="4"><INPUT TYPE="Radio" NAME="Photo" VALUE="photo_#p#.gif"<CFIF f_Photo IS "photo_#p#.gif"> CHECKED</CFIF>><IMG SRC="#Request.Images#/photo_#p#.gif" WIDTH=36 HEIGHT=45 ALIGN=MIDDLE>&nbsp;&nbsp;</CFLOOP>
	<BR><FONT FACE="#Request.Font#" SIZE=1>Real photos arrive when Facilities fixes the digital camera.</FONT></TD></TR>
<TR VALIGN=TOP><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>Notes:</B></FONT></TD>
	<TD><TEXTAREA NAME="Notes" ROWS=3 COLS=45 WRAP="VIRTUAL">#HTMLEditFormat(f_Notes)#</TEXTAREA></TD></TR>
<TR><TD></TD>
	<TD><INPUT TYPE="Submit" NAME="SaveButton" VALUE="<CFIF f_Emp_ID>Update Entry<CFELSE>Add Employee</CFIF>">
	<CFIF f_Emp_ID><INPUT TYPE="Submit" NAME="DeleteButton" VALUE="Delete" onClick="return confirm('Really delete #JSStringFormat(f_FirstName)# #JSStringFormat(f_LastName)# from the directory?')"></CFIF>
	<INPUT TYPE="Button" VALUE="Cancel" onClick="history.back()"></TD></TR>
</TABLE>
</CFOUTPUT>
</CFFORM>

<CFINCLUDE TEMPLATE="../footer.cfm">
