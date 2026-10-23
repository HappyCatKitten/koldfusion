<!--- KoldFusion Administrator login --->
<cfset loginError = "">
<cfparam name="URL.page" default="">
<cfparam name="Form.page" default="#URL.page#">
<!--- only pages inside the Administrator --->
<cfif REFind("[^A-Za-z0-9_/.]", Form.page) OR Find("..", Form.page) OR Left(Form.page, 1) EQ "/"><cfset Form.page = ""></cfif>
<cfif IsDefined("Form.AdminPassword")>
	<cfif KFUSION_CHECKPASSWORD(Form.AdminPassword)>
		<cfcookie name="CFADMIN_AUTH" value="#Request.authToken#">
		<cfif Len(Form.page)><cflocation url="/CFIDE/administrator/index.cfm?page=#URLEncodedFormat(Form.page)#" addtoken="no">
		<cfelse><cflocation url="/CFIDE/administrator/index.cfm" addtoken="no"></cfif>
	<cfelse>
		<cfset loginError = "The password you entered is not valid. Please try again.">
	</cfif>
</cfif>
<cfif IsDefined("URL.logout")>
	<cfcookie name="CFADMIN_AUTH" value="" expires="now">
</cfif>
<HTML>
<HEAD>
<TITLE>KoldFusion Administrator Login</TITLE>
<SCRIPT LANGUAGE="JavaScript">
<!--
if (top != self) top.location = self.location;
function setFocus() { if (document.loginform) document.loginform.AdminPassword.focus(); }
//-->
</SCRIPT>
</HEAD>
<BODY BGCOLOR="#99CC99" BACKGROUND="/images/bgblue.gif" onLoad="setFocus()">
<BR><BR>
<CENTER>
<TABLE WIDTH=580 BORDER=0 CELLPADDING=0 CELLSPACING=0 BGCOLOR="#000066">
<TR><TD>
<TABLE WIDTH=580 HEIGHT=400 BORDER=0 CELLPADDING=0 CELLSPACING=1>
<TR><TD BGCOLOR="#FFFFFF" VALIGN=TOP>
	<TABLE WIDTH="100%" HEIGHT=380 BORDER=0 CELLPADDING=0 CELLSPACING=0>
	<TR>
		<TD VALIGN=TOP WIDTH=330>
			<TABLE BORDER=0 CELLPADDING=12 CELLSPACING=0><TR><TD>
			<IMG SRC="images/login_banner.gif" WIDTH=400 HEIGHT=80 ALT="KoldFusion Administrator"><BR><BR>
			<FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#469320"><B>w e b &nbsp; a p p l i c a t i o n &nbsp; s e r v e r</B></FONT>
			<BR><BR><BR>
			<FORM NAME="loginform" ACTION="login.cfm" METHOD="POST">
			<cfoutput><INPUT TYPE="hidden" NAME="page" VALUE="#HTMLEditFormat(Form.page)#"></cfoutput>
			<cfif Request.useAdminPw EQ "1">
			<INPUT TYPE="password" NAME="AdminPassword" SIZE=20 MAXLENGTH=64>
			<INPUT TYPE="submit" VALUE="Password">
			<cfelse>
			<FONT FACE="Arial, Helvetica" SIZE=2>The Administrator password is disabled.</FONT>
			<INPUT TYPE="button" VALUE="Enter" onClick="top.location='index.cfm'">
			</cfif>
			</FORM>
			<cfif Len(loginError)><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#CC0000"><B><cfoutput>#loginError#</cfoutput></B></FONT><BR><BR></cfif>
			<FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#808080">In order to access the administrative functions on this KoldFusion
			server you need to login using the administrator password.</FONT>
			</TD></TR></TABLE>
		</TD>
		<TD ALIGN=RIGHT VALIGN=BOTTOM><IMG SRC="images/swoosh.gif" WIDTH=170 HEIGHT=330 ALT=""></TD>
	</TR>
	</TABLE>
</TD></TR>
<TR><TD BGCOLOR="#000066" HEIGHT=18 ALIGN=CENTER><FONT FACE="Arial, Helvetica" SIZE=1 COLOR="#FFFFFF">Copyright 1995-1999, Gibson Mainframe Co.</FONT></TD></TR>
</TABLE>
</TD></TR>
</TABLE>
</CENTER>
</BODY>
</HTML>
