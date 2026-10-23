<!---
	directory/search.cfm - search form and results on one page.
	The form posts back to this template; Form.DoSearch tells us to search.
--->
<CFPARAM NAME="Form.LastName" DEFAULT="">
<CFPARAM NAME="Form.FirstName" DEFAULT="">
<CFPARAM NAME="Form.Title" DEFAULT="">
<CFPARAM NAME="Form.Dept_ID" DEFAULT="0">
<CFSET PageTitle = "Search the Directory">
<CFSET Section = "directory">

<CFQUERY NAME="GetDepartments" DATASOURCE="#Request.DSN#">
	SELECT Dept_ID, DeptName FROM Departments ORDER BY DeptName
</CFQUERY>

<CFIF IsDefined("Form.DoSearch")>
	<CFQUERY NAME="Results" DATASOURCE="#Request.DSN#">
		SELECT e.Emp_ID, e.FirstName, e.LastName, e.Title, e.Phone, d.DeptName
		FROM Employees e, Departments d
		WHERE e.Dept_ID = d.Dept_ID
		<CFIF Len(Trim(Form.LastName))>
		  AND e.LastName LIKE '#Trim(Form.LastName)#%'
		</CFIF>
		<CFIF Len(Trim(Form.FirstName))>
		  AND e.FirstName LIKE '#Trim(Form.FirstName)#%'
		</CFIF>
		<CFIF Len(Trim(Form.Title))>
		  AND e.Title LIKE '%#Trim(Form.Title)#%'
		</CFIF>
		<CFIF Val(Form.Dept_ID)>
		  AND e.Dept_ID = #Val(Form.Dept_ID)#
		</CFIF>
		ORDER BY e.LastName, e.FirstName
	</CFQUERY>
</CFIF>

<CFINCLUDE TEMPLATE="../header.cfm">

<CFOUTPUT>
<P>Fill in any of the fields below. Partial names are fine: <I>Ko</I> finds Kowalski and Kowalczyk.</P>
<FORM ACTION="search.cfm" METHOD="POST">
<INPUT TYPE="Hidden" NAME="DoSearch" VALUE="Yes">
<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0 BGCOLOR="##EEEEEE">
<TR><TD><FONT FACE="#Request.Font#" SIZE=2><B>Last name</B></FONT></TD>
	<TD><INPUT TYPE="Text" NAME="LastName" SIZE=20 VALUE="#HTMLEditFormat(Form.LastName)#"></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2><B>First name</B></FONT></TD>
	<TD><INPUT TYPE="Text" NAME="FirstName" SIZE=15 VALUE="#HTMLEditFormat(Form.FirstName)#"></TD></TR>
<TR><TD><FONT FACE="#Request.Font#" SIZE=2><B>Title contains</B></FONT></TD>
	<TD><INPUT TYPE="Text" NAME="Title" SIZE=20 VALUE="#HTMLEditFormat(Form.Title)#"></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2><B>Department</B></FONT></TD>
	<TD><SELECT NAME="Dept_ID">
		<OPTION VALUE="0">(any)
		<CFLOOP QUERY="GetDepartments"><OPTION VALUE="#Dept_ID#"<CFIF Dept_ID EQ Form.Dept_ID> SELECTED</CFIF>>#DeptName#</CFLOOP>
	</SELECT></TD></TR>
<TR><TD></TD><TD COLSPAN=3><INPUT TYPE="Submit" VALUE="Search"> <INPUT TYPE="Button" VALUE="Browse All" onClick="location.href='index.cfm'"></TD></TR>
</TABLE>
</FORM>
</CFOUTPUT>

<CFIF IsDefined("Results")>
	<CFOUTPUT><P><B>#Results.RecordCount#</B> match<CFIF Results.RecordCount NEQ 1>es</CFIF> found.</P></CFOUTPUT>
	<CFIF Results.RecordCount>
		<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0 WIDTH="100%">
		<TR BGCOLOR="#003366">
			<TD><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Name</B></FONT></TD>
			<TD><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Title</B></FONT></TD>
			<TD><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Department</B></FONT></TD>
			<TD><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Phone</B></FONT></TD>
		</TR>
		<CFOUTPUT QUERY="Results">
		<TR BGCOLOR="###IIf(CurrentRow MOD 2, DE('FFFFFF'), DE('F0F0F0'))#">
			<TD><FONT FACE="#Request.Font#" SIZE=2><A HREF="detail.cfm?Emp_ID=#Emp_ID#">#LastName#, #FirstName#</A></FONT></TD>
			<TD><FONT FACE="#Request.Font#" SIZE=2>#Title#</FONT></TD>
			<TD><FONT FACE="#Request.Font#" SIZE=2>#DeptName#</FONT></TD>
			<TD NOWRAP><FONT FACE="#Request.Font#" SIZE=2>#Phone#</FONT></TD>
		</TR>
		</CFOUTPUT>
		</TABLE>
	</CFIF>
</CFIF>

<CFINCLUDE TEMPLATE="../footer.cfm">
