<!---
	directory/index.cfm - browse the employee directory by department.
	Uses CFOUTPUT GROUP= to print each department heading once,
	followed by everyone who works there.
	  ?letter=X   only last names starting with X
	  ?Dept_ID=n  only one department
--->
<CFPARAM NAME="URL.letter" DEFAULT="">
<CFPARAM NAME="URL.Dept_ID" DEFAULT="0">
<CFSET PageTitle = "Employee Directory">
<CFSET Section = "directory">

<CFQUERY NAME="GetDepartments" DATASOURCE="#Request.DSN#">
	SELECT Dept_ID, DeptName FROM Departments ORDER BY DeptName
</CFQUERY>

<CFQUERY NAME="GetEmployees" DATASOURCE="#Request.DSN#">
	SELECT e.Emp_ID, e.FirstName, e.LastName, e.Title, e.Phone, e.Email, e.Office,
	       d.Dept_ID, d.DeptName, d.Building, d.MailStop
	FROM Employees e, Departments d
	WHERE e.Dept_ID = d.Dept_ID
	<CFIF Len(URL.letter) EQ 1>
	  AND e.LastName LIKE '#UCase(URL.letter)#%'
	</CFIF>
	<CFIF Val(URL.Dept_ID)>
	  AND d.Dept_ID = #Val(URL.Dept_ID)#
	</CFIF>
	ORDER BY d.DeptName, e.LastName, e.FirstName
</CFQUERY>

<CFINCLUDE TEMPLATE="../header.cfm">

<CFOUTPUT>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=4 CELLSPACING=0 BGCOLOR="##EEEEEE">
<TR>
<TD><FONT FACE="#Request.Font#" SIZE=2>
	<B>Last name:</B>
	<CFLOOP INDEX="i" FROM="65" TO="90"><A HREF="index.cfm?letter=#Chr(i)#"><CFIF URL.letter IS Chr(i)><FONT COLOR="##CC0000"><B>#Chr(i)#</B></FONT><CFELSE>#Chr(i)#</CFIF></A> </CFLOOP>
	| <A HREF="index.cfm">All</A>
</FONT></TD>
<TD ALIGN=RIGHT>
	<FORM ACTION="index.cfm" METHOD="GET" STYLE="margin:0">
	<FONT FACE="#Request.Font#" SIZE=2>
	<SELECT NAME="Dept_ID" onChange="this.form.submit()">
		<OPTION VALUE="0">All departments
		<CFLOOP QUERY="GetDepartments"><OPTION VALUE="#Dept_ID#"<CFIF Dept_ID EQ URL.Dept_ID> SELECTED</CFIF>>#DeptName#</CFLOOP>
	</SELECT>
	<NOSCRIPT><INPUT TYPE="Submit" VALUE="Go"></NOSCRIPT>
	</FONT>
	</FORM>
</TD>
</TR>
</TABLE>
<P>
<A HREF="search.cfm"><IMG SRC="/CFIDE/administrator/images/arrow.gif" WIDTH=16 HEIGHT=16 BORDER=0 ALIGN=ABSMIDDLE> Search the directory</A>
<CFIF Request.IsAdmin>&nbsp;&nbsp;&nbsp;<A HREF="edit.cfm"><IMG SRC="/CFIDE/administrator/images/file.gif" WIDTH=16 HEIGHT=16 BORDER=0 ALIGN=ABSMIDDLE> Add a new employee</A></CFIF>
&nbsp;&nbsp;&nbsp;<FONT SIZE=1 COLOR="##666666">#GetEmployees.RecordCount# listing<CFIF GetEmployees.RecordCount NEQ 1>s</CFIF></FONT>
</P>
</CFOUTPUT>

<CFIF GetEmployees.RecordCount EQ 0>
	<P>Nobody matches. Try another letter, or <A HREF="index.cfm">show everyone</A>.</P>
<CFELSE>
	<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
	<CFOUTPUT QUERY="GetEmployees" GROUP="DeptName">
		<TR><TD COLSPAN=4 BGCOLOR="##003366"><FONT FACE="#Request.Font#" SIZE=2 COLOR="##FFFFFF"><B>#DeptName#</B></FONT>
			<FONT FACE="#Request.Font#" SIZE=1 COLOR="##FFCC00">&nbsp;&nbsp;#Building# &middot; Mail stop #MailStop#</FONT></TD></TR>
		<TR BGCOLOR="##CCCCCC">
			<TD><FONT FACE="#Request.Font#" SIZE=1><B>Name</B></FONT></TD>
			<TD><FONT FACE="#Request.Font#" SIZE=1><B>Title</B></FONT></TD>
			<TD><FONT FACE="#Request.Font#" SIZE=1><B>Phone</B></FONT></TD>
			<TD><FONT FACE="#Request.Font#" SIZE=1><B>Office</B></FONT></TD>
		</TR>
		<CFSET RowNum = 0>
		<CFOUTPUT>
		<CFSET RowNum = RowNum + 1>
		<TR BGCOLOR="<CFIF RowNum MOD 2>##FFFFFF<CFELSE>##F0F0F0</CFIF>">
			<TD><FONT FACE="#Request.Font#" SIZE=2><A HREF="detail.cfm?Emp_ID=#Emp_ID#">#LastName#, #FirstName#</A></FONT></TD>
			<TD><FONT FACE="#Request.Font#" SIZE=2>#Title#</FONT></TD>
			<TD NOWRAP><FONT FACE="#Request.Font#" SIZE=2>#Phone#</FONT></TD>
			<TD><FONT FACE="#Request.Font#" SIZE=2>#Office#</FONT></TD>
		</TR>
		</CFOUTPUT>
		<TR><TD COLSPAN=4>&nbsp;</TD></TR>
	</CFOUTPUT>
	</TABLE>
</CFIF>

<CFINCLUDE TEMPLATE="../footer.cfm">
