<!--- Verify Data Source --->
<cfif IsDefined("URL.DSN")>
	<cfset v = KFUSION_VERIFYDSN(URL.DSN)>
	<cfparam name="URL.back" default="">
	<cfset backPage = "verify.cfm">
	<cfif URL.back EQ "Native"><cfset backPage = "native.cfm"><cfelseif URL.back EQ "OLEDB"><cfset backPage = "oledb.cfm"><cfelseif URL.back EQ "ODBC"><cfset backPage = "odbc.cfm"></cfif>
	<cfset pageTitle = "Verify Data Source: #URL.DSN#">
	<cfinclude template="../_header.cfm">
	<cfmodule template="../_tags/status.cfm" message="#v.Message#" back="#backPage#">
	<cfinclude template="../_footer.cfm">
	<cfabort>
</cfif>
<cfset dsns = KFUSION_DSNLIST()>
<cfset pageTitle = "Verify Data Source">
<cfinclude template="../_header.cfm">
<cfoutput>
<FORM ACTION="verify.cfm" METHOD="POST">
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="##669966"><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Data Source Name</B></FONT></TD><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>ODBC Driver</B></FONT></TD><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Status</B></FONT></TD></TR>
<cfloop query="dsns">
<TR BGCOLOR="#IIf(dsns.CurrentRow MOD 2, DE('FFFBF0'), DE('FFFFFF'))#">
<TD>#Request.f#<B><A HREF="verify.cfm?DSN=#URLEncodedFormat(dsns.Name)#">#dsns.Name#</A></B></FONT></TD>
<TD>#Request.f##dsns.Driver#</FONT></TD>
<TD>#Request.f#<cfif IsDefined("Form.VerifyAll")><cfset v = KFUSION_VERIFYDSN(dsns.Name)><cfif v.OK><FONT COLOR="##008000">Verified</FONT><cfelse><FONT COLOR="##CC0000" TITLE="#HTMLEditFormat(v.Message)#">Failed</FONT></cfif><cfelse>&nbsp;</cfif></FONT></TD></TR>
</cfloop>
</TABLE>
<P><INPUT TYPE="submit" NAME="VerifyAll" VALUE="Verify All">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
