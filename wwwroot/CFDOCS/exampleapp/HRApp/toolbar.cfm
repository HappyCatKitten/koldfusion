<!---
	toolbar.cfm - the page top and navigation toolbar shared by every HRApp page.
	Set Variables.PageTitle before including it.
--->
<CFPARAM NAME="PageTitle" DEFAULT="">
<CFSET ThisFile = ReplaceNoCase(CGI.SCRIPT_NAME, "/CFDOCS/exampleapp/", "")>
<CFOUTPUT>
<HTML>
<HEAD>
<TITLE>Human Resources Employee Manager<CFIF Len(PageTitle)> - #PageTitle#</CFIF></TITLE>
</HEAD>
<BODY BGCOLOR="##FFFFFF" LINK="##003399" VLINK="##003399">
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=4 CELLSPACING=0 BGCOLOR="##003399">
<TR>
	<TD><FONT FACE="#Request.Font#" SIZE="+2" COLOR="##CCCCCC"><B>Human Resources Employee Manager</B></FONT></TD>
	<TD ALIGN=RIGHT NOWRAP><FONT FACE="#Request.Font#" SIZE=2>
		<A HREF="EmpList.cfm"><FONT COLOR="##FFFFFF"><B>List</B></FONT></A>
		<FONT COLOR="##CCCCCC">|</FONT>
		<A HREF="SearchForm.cfm"><FONT COLOR="##FFFFFF"><B>Search</B></FONT></A>
		<FONT COLOR="##CCCCCC">|</FONT>
		<A HREF="InsertForm.cfm"><FONT COLOR="##FFFFFF"><B>Add</B></FONT></A>
		<FONT COLOR="##CCCCCC">|</FONT>
		<A HREF="UpdateList.cfm"><FONT COLOR="##FFFFFF"><B>Update</B></FONT></A>
	</FONT></TD>
</TR>
</TABLE>
<CFIF Len(PageTitle)>
	<P><FONT FACE="#Request.Font#" SIZE=4><B>#PageTitle#</B></FONT></P>
</CFIF>
</CFOUTPUT>
