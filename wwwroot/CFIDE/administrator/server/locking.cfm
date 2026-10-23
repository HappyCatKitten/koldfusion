<!--- Locking (new in 4.5) --->
<cfset msg = "">
<cfif IsDefined("Form.Apply")>
	<cfloop list="ServerScope,ApplicationScope,SessionScope" index="s">
		<cfmodule template="../_tags/setreg.cfm" key="Locking" entry="#s#" value="#Form[s]#">
	</cfloop>
	<cfmodule template="../_tags/setreg.cfm" key="Locking" entry="SingleThreadedSessions" value="#IIf(Form.SessionScope EQ 'single', 1, 0)#">
	<cfset msg = "Locking settings have been applied.">
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="Locking" variable="L">
<cfif L.SingleThreadedSessions EQ 1><cfset L.SessionScope = "single"></cfif>
<cfset pageTitle = "Locking">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<P>#Request.f#Variables in the Server, Application and Session scopes are shared between simultaneous requests and must be protected
with CFLOCK. These settings let the server check or enforce locking for you.</FONT>
<FORM ACTION="locking.cfm" METHOD="POST">
<cfloop list="ServerScope:Server Scope,ApplicationScope:Application Scope,SessionScope:Session Scope" index="row">
	<cfset fld = ListFirst(row, ":")>
	<P><TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>#ListLast(row, ":")#</B></FONT></TD></TR></TABLE>
	#Request.f#
	<INPUT TYPE="radio" NAME="#fld#" VALUE="none"<cfif L[fld] EQ "none"> CHECKED</cfif>> No automatic checking or locking<BR>
	<INPUT TYPE="radio" NAME="#fld#" VALUE="full"<cfif L[fld] EQ "full"> CHECKED</cfif>> Full checking (an error is raised for any unlocked access)<BR>
	<INPUT TYPE="radio" NAME="#fld#" VALUE="readlock"<cfif L[fld] EQ "readlock"> CHECKED</cfif>> Automatic read locking (unlocked writes raise an error)<BR>
	<cfif fld EQ "SessionScope"><INPUT TYPE="radio" NAME="#fld#" VALUE="single"<cfif L[fld] EQ "single"> CHECKED</cfif>> Single threaded sessions (requests from one session run one at a time)<BR></cfif>
	</FONT>
</cfloop>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Apply" VALUE="Apply"> <INPUT TYPE="reset" VALUE="Cancel">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
