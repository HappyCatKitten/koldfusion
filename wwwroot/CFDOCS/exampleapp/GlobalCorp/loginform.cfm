<!---
	loginform.cfm - included by Application.cfm when nobody is logged in.
	The form posts back to whatever page was requested, so after a
	successful login the visitor lands where they meant to go.
--->
<CFSET LoginAction = CGI.SCRIPT_NAME>
<CFIF Len(CGI.QUERY_STRING)>
	<CFSET LoginAction = LoginAction & "?" & CGI.QUERY_STRING>
</CFIF>
<CFQUERY NAME="SampleUsers" DATASOURCE="#Request.DSN#">
	SELECT UserName, Password, FullName, IsAdmin
	FROM Users
	ORDER BY IsAdmin, UserName
</CFQUERY>
<HTML>
<HEAD>
<TITLE>GlobalCorp Intranet - Please Log In</TITLE>
</HEAD>
<CFOUTPUT>
<BODY BGCOLOR="##003366" LINK="##003399" VLINK="##003399" onLoad="if (document.forms[0]) document.forms[0].Login_UserName.focus()">
<BR><BR>
<CENTER>
<TABLE WIDTH=520 BORDER=0 CELLPADDING=1 CELLSPACING=0 BGCOLOR="##FFCC00"><TR><TD>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=12 CELLSPACING=0 BGCOLOR="##FFFFFF">
<TR>
	<TD ALIGN=CENTER>
	<IMG SRC="#Request.Images#/gc_logo.gif" WIDTH=300 HEIGHT=64 ALT="GlobalCorp Intranet"><BR>
	<FONT FACE="#Request.Font#" SIZE=2>
	<P>This site is for GlobalCorp employees. Please log in with your intranet user name and password.</P>
	<CFIF Len(Request.LoginError)>
		<P><FONT COLOR="##CC0000"><B>#Request.LoginError#</B></FONT></P>
	</CFIF>
	</FONT>
	<CFFORM NAME="LoginForm" ACTION="#LoginAction#" METHOD="POST">
	<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0>
	<TR>
		<TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>User name:</B></FONT></TD>
		<TD><CFINPUT TYPE="Text" NAME="Login_UserName" SIZE="20" MAXLENGTH="20" REQUIRED="Yes" MESSAGE="Please enter your user name."></TD>
	</TR>
	<TR>
		<TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>Password:</B></FONT></TD>
		<TD><CFINPUT TYPE="Password" NAME="Login_Password" SIZE="20" MAXLENGTH="20" REQUIRED="Yes" MESSAGE="Please enter your password."></TD>
	</TR>
	<TR>
		<TD></TD>
		<TD><INPUT TYPE="Submit" VALUE="  Log In  "></TD>
	</TR>
	</TABLE>
	</CFFORM>
	</TD>
</TR>
<TR>
	<TD BGCOLOR="##FFFFE0">
	<FONT FACE="#Request.Font#" SIZE=1>
	<B>This is a sample application.</B> You can log in with any of these demonstration accounts
	(accounts marked <B>admin</B> may also add and edit directory entries):<BR>
	</FONT>
	<TABLE BORDER=0 CELLPADDING=1 CELLSPACING=0>
	<CFLOOP QUERY="SampleUsers">
	<TR>
		<TD><FONT FACE="Courier New, Courier" SIZE=2>#UserName#</FONT></TD>
		<TD><FONT FACE="Courier New, Courier" SIZE=2>&nbsp;/&nbsp;#Password#</FONT></TD>
		<TD><FONT FACE="#Request.Font#" SIZE=1>&nbsp;&nbsp;#FullName#<CFIF IsAdmin> (admin)</CFIF></FONT></TD>
	</TR>
	</CFLOOP>
	</TABLE>
	</TD>
</TR>
</TABLE>
</TD></TR></TABLE>
<BR>
<FONT FACE="#Request.Font#" SIZE=1 COLOR="##FFFFFF">
<A HREF="/CFDOCS/examplehome.cfm"><FONT COLOR="##FFCC00">Example Applications</FONT></A> &middot;
<A HREF="javascript:void(window.open('/CFDOCS/exampleapp/sourcewindow.cfm?file=GlobalCorp/Application.cfm','cfsource','width=680,height=500,scrollbars=yes,resizable=yes'))"><FONT COLOR="##FFCC00">View the source of Application.cfm</FONT></A>
</FONT>
</CENTER>
</BODY>
</CFOUTPUT>
</HTML>
