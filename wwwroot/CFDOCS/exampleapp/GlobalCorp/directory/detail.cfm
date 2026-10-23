<!---
	directory/detail.cfm - one employee's directory card
	  ?Emp_ID=n
--->
<CFPARAM NAME="URL.Emp_ID" DEFAULT="0">
<CFPARAM NAME="URL.saved" DEFAULT="">
<CFSET Section = "directory">

<CFQUERY NAME="GetEmployee" DATASOURCE="#Request.DSN#">
	SELECT e.*, d.DeptName, d.Building, d.MailStop, d.Manager
	FROM Employees e, Departments d
	WHERE e.Dept_ID = d.Dept_ID
	  AND e.Emp_ID = #Val(URL.Emp_ID)#
</CFQUERY>

<CFIF GetEmployee.RecordCount EQ 0>
	<CFSET PageTitle = "Employee Not Found">
	<CFINCLUDE TEMPLATE="../header.cfm">
	<P>There is no directory entry with that ID. It may have been deleted.</P>
	<P><A HREF="index.cfm">Back to the directory</A></P>
	<CFINCLUDE TEMPLATE="../footer.cfm">
	<CFABORT>
</CFIF>

<CFQUERY NAME="CoWorkers" DATASOURCE="#Request.DSN#">
	SELECT Emp_ID, FirstName, LastName, Title
	FROM Employees
	WHERE Dept_ID = #GetEmployee.Dept_ID#
	  AND Emp_ID <> #GetEmployee.Emp_ID#
	ORDER BY LastName
</CFQUERY>

<CFSET PageTitle = GetEmployee.FirstName & " " & GetEmployee.LastName>
<!--- no photo on file? pick one of the placeholder silhouettes --->
<CFIF Len(GetEmployee.Photo)>
	<CFSET PhotoFile = GetEmployee.Photo>
<CFELSE>
	<CFSET PhotoFile = "photo_#(GetEmployee.Emp_ID MOD 4) + 1#.gif">
</CFIF>

<CFINCLUDE TEMPLATE="../header.cfm">

<CFOUTPUT QUERY="GetEmployee">
<CFIF URL.saved IS "yes"><P><FONT COLOR="##006600"><B>The directory entry has been saved.</B></FONT></P></CFIF>
<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0>
<TR VALIGN=TOP>
	<TD><IMG SRC="#Request.Images#/#PhotoFile#" WIDTH=72 HEIGHT=90 BORDER=1 ALT="Photo of #FirstName# #LastName#"></TD>
	<TD>
	<FONT FACE="#Request.Font#" SIZE=3><B>#Title#</B></FONT><BR>
	<FONT FACE="#Request.Font#" SIZE=2>#DeptName#</FONT>
	<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=0>
	<TR><TD><FONT FACE="#Request.Font#" SIZE=2><B>Phone:</B></FONT></TD><TD><FONT FACE="#Request.Font#" SIZE=2>#Phone#</FONT></TD></TR>
	<TR><TD><FONT FACE="#Request.Font#" SIZE=2><B>E-mail:</B></FONT></TD><TD><FONT FACE="#Request.Font#" SIZE=2><A HREF="mailto:#Email#">#Email#</A></FONT></TD></TR>
	<TR><TD><FONT FACE="#Request.Font#" SIZE=2><B>Office:</B></FONT></TD><TD><FONT FACE="#Request.Font#" SIZE=2>#Office# (#Building#, mail stop #MailStop#)</FONT></TD></TR>
	<TR><TD><FONT FACE="#Request.Font#" SIZE=2><B>With us since:</B></FONT></TD><TD><FONT FACE="#Request.Font#" SIZE=2>#DateFormat(StartDate, "mmmm d, yyyy")#</FONT></TD></TR>
	<TR><TD><FONT FACE="#Request.Font#" SIZE=2><B>Department head:</B></FONT></TD><TD><FONT FACE="#Request.Font#" SIZE=2>#Manager#</FONT></TD></TR>
	</TABLE>
	</TD>
</TR>
</TABLE>
<CFIF Len(Notes)>
	<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0 WIDTH="80%"><TR><TD BGCOLOR="##FFFFE0"><FONT FACE="#Request.Font#" SIZE=2><I>#HTMLEditFormat(Notes)#</I></FONT></TD></TR></TABLE>
</CFIF>
<CFIF Request.IsAdmin>
	<FORM ACTION="edit.cfm" METHOD="GET">
	<INPUT TYPE="Hidden" NAME="Emp_ID" VALUE="#Emp_ID#">
	<INPUT TYPE="Submit" VALUE="Edit This Entry">
	</FORM>
</CFIF>
</CFOUTPUT>

<CFIF CoWorkers.RecordCount>
	<CFOUTPUT><P><B>Also in #GetEmployee.DeptName#:</B><BR></CFOUTPUT>
	<CFOUTPUT QUERY="CoWorkers"><A HREF="detail.cfm?Emp_ID=#Emp_ID#">#FirstName# #LastName#</A>, #Title#<BR></CFOUTPUT>
	</P>
</CFIF>
<P><A HREF="index.cfm">&lt;&lt; Back to the directory</A></P>

<CFINCLUDE TEMPLATE="../footer.cfm">
