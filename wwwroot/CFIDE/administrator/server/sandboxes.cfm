<!--- Registered Security Sandboxes --->
<cfset base = Request.reg & "\Security\Sandboxes">
<cfset msg = "">
<cfif IsDefined("Form.Add") AND Len(Trim(Form.SandboxPath))>
	<cfset nm = Replace(Trim(Form.SandboxPath), "/", "_", "ALL")>
	<cfregistry action="set" branch="#base#\#nm#" entry="Path" value="#Trim(Form.SandboxPath)#">
	<cfregistry action="set" branch="#base#\#nm#" entry="Context" value="#Form.Context#">
	<cfset msg = "The sandbox has been registered.">
</cfif>
<cfif IsDefined("URL.delete")><cfregistry action="delete" branch="#base#\#URL.delete#"><cfset msg = "The sandbox has been removed."></cfif>
<cfregistry action="getall" branch="#base#" name="sb" type="key">
<cfregistry action="getall" branch="#Request.reg#\Security\Contexts" name="ctxs" type="key">
<cfset pageTitle = "Registered Security Sandboxes">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<P>#Request.f#A sandbox ties a directory tree to a security context: templates in that tree run with the permissions the
context's policies grant.</FONT>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="##669966"><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Path</B></FONT></TD><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Security Context</B></FONT></TD><TD></TD></TR>
<cfloop query="sb">
	<cfregistry action="get" branch="#base#\#sb.Entry#" entry="Path" variable="p">
	<cfregistry action="get" branch="#base#\#sb.Entry#" entry="Context" variable="cx">
	<TR BGCOLOR="#IIf(sb.CurrentRow MOD 2, DE('FFFFFF'), DE('FFFBF0'))#"><TD>#Request.f#<TT>#p#</TT></FONT></TD><TD>#Request.f##cx#</FONT></TD>
	<TD>#Request.f#<A HREF="sandboxes.cfm?delete=#URLEncodedFormat(sb.Entry)#">Delete</A></FONT></TD></TR>
</cfloop>
</TABLE>
<FORM ACTION="sandboxes.cfm" METHOD="POST">
<P>#Request.f#<B>New Sandbox</B><BR>Path <INPUT TYPE="text" NAME="SandboxPath" SIZE=40> <INPUT TYPE="button" VALUE="Browse Server..." onClick="browseServer('SandboxPath')">
Type <SELECT NAME="Context"><cfloop query="ctxs"><OPTION>#ctxs.Entry#</cfloop><OPTION VALUE="OS">Operating System (Windows NT only)</SELECT>
<INPUT TYPE="submit" NAME="Add" VALUE="Apply"> <INPUT TYPE="button" VALUE="Back" onClick="location='advancedsecurity.cfm'"></FONT>
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
