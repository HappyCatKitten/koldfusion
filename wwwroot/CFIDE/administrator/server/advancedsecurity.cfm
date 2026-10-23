<!--- Advanced Server Security --->
<cfset msg = "">
<cfset fields = "SecurityServer,SharedSecret,AuthPort,AuthzPort,PolicyStoreRefresh,AuthorizationRefresh,ServerCacheRefresh,MaxCacheEntries,AdminContext,StudioContext">
<cfset checks = "UseAdvancedSecurity,PolicyStoreCache,LoadPolicyAtStartup,AuthorizationCache,ServerCache,UseAdminAuthentication,UseStudioAuthentication,UseSandboxes,ProtectAllResources">
<cfif IsDefined("Form.Apply")>
	<cfloop list="#fields#" index="f">
		<cfif IsDefined("Form." & f)><cfmodule template="../_tags/setreg.cfm" key="Security" entry="#f#" value="#Trim(Form[f])#"></cfif>
	</cfloop>
	<cfloop list="#checks#" index="f">
		<cfmodule template="../_tags/setreg.cfm" key="Security" entry="#f#" value="#IIf(IsDefined('Form.' & f), 1, 0)#">
	</cfloop>
	<cfset msg = "Advanced security settings have been applied.">
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="Security" variable="S">
<cfparam name="S.AdminContext" default="">
<cfparam name="S.StudioContext" default="">
<cfregistry action="getall" branch="#Request.reg#\Security\Contexts" name="ctx" type="key">
<cfset pageTitle = "Advanced Server Security">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="advancedsecurity.cfm" METHOD="POST">
<P>#Request.f#<INPUT TYPE="checkbox" NAME="UseAdvancedSecurity" VALUE="1"<cfif S.UseAdvancedSecurity EQ 1> CHECKED</cfif>>
<B>Use Advanced Server Security</B><BR>
Advanced security provides authentication and authorization for users of your applications through security contexts,
user directories, rules and policies. Applications use it through CFAUTHENTICATE, CFIMPERSONATE, IsAuthenticated() and IsAuthorized().</FONT>
<BLOCKQUOTE><TABLE BORDER=0 CELLPADDING=2>
<TR><TD>#Request.f#Security Server</FONT></TD><TD><INPUT TYPE="text" NAME="SecurityServer" VALUE="#S.SecurityServer#" SIZE=20></TD></TR>
<TR><TD>#Request.f#Shared Secret</FONT></TD><TD><INPUT TYPE="password" NAME="SharedSecret" VALUE="#S.SharedSecret#" SIZE=20></TD></TR>
<TR><TD>#Request.f#Authentication Port</FONT></TD><TD><INPUT TYPE="text" NAME="AuthPort" VALUE="#S.AuthPort#" SIZE=6></TD></TR>
<TR><TD>#Request.f#Authorization Port</FONT></TD><TD><INPUT TYPE="text" NAME="AuthzPort" VALUE="#S.AuthzPort#" SIZE=6></TD></TR>
</TABLE></BLOCKQUOTE>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>Security Server Cache</B></FONT></TD></TR></TABLE>
<BLOCKQUOTE><TABLE BORDER=0 CELLPADDING=2>
<TR><TD>#Request.f#<INPUT TYPE="checkbox" NAME="PolicyStoreCache" VALUE="1"<cfif S.PolicyStoreCache EQ 1> CHECKED</cfif>> Security Server Policy Store Cache</FONT></TD>
	<TD>#Request.f#Refresh Interval <INPUT TYPE="text" NAME="PolicyStoreRefresh" VALUE="#S.PolicyStoreRefresh#" SIZE=3> minutes</FONT></TD></TR>
<TR><TD COLSPAN=2>#Request.f#<INPUT TYPE="checkbox" NAME="LoadPolicyAtStartup" VALUE="1"<cfif S.LoadPolicyAtStartup EQ 1> CHECKED</cfif>> Load Security Server Policy Store Cache at Startup</FONT></TD></TR>
<TR><TD>#Request.f#<INPUT TYPE="checkbox" NAME="AuthorizationCache" VALUE="1"<cfif S.AuthorizationCache EQ 1> CHECKED</cfif>> Security Server Authorization Cache</FONT></TD>
	<TD>#Request.f#Refresh Interval <INPUT TYPE="text" NAME="AuthorizationRefresh" VALUE="#S.AuthorizationRefresh#" SIZE=3> minutes</FONT></TD></TR>
<TR><TD>#Request.f#<INPUT TYPE="checkbox" NAME="ServerCache" VALUE="1"<cfif S.ServerCache EQ 1> CHECKED</cfif>> KoldFusion Server Cache</FONT></TD>
	<TD>#Request.f#Refresh Interval <INPUT TYPE="text" NAME="ServerCacheRefresh" VALUE="#S.ServerCacheRefresh#" SIZE=3> minutes</FONT></TD></TR>
<TR><TD>#Request.f#Maximum Cache Entries</FONT></TD><TD><INPUT TYPE="text" NAME="MaxCacheEntries" VALUE="#S.MaxCacheEntries#" SIZE=6></TD></TR>
</TABLE></BLOCKQUOTE>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>KoldFusion Administration and Studio Security</B></FONT></TD></TR></TABLE>
<BLOCKQUOTE><TABLE BORDER=0 CELLPADDING=2>
<TR><TD>#Request.f#<INPUT TYPE="checkbox" NAME="UseAdminAuthentication" VALUE="1"<cfif S.UseAdminAuthentication EQ 1> CHECKED</cfif>> Use KoldFusion Administration Authentication</FONT></TD>
	<TD>#Request.f#Security context <SELECT NAME="AdminContext"><OPTION VALUE="">(none)<cfloop query="ctx"><OPTION<cfif ctx.Entry EQ S.AdminContext> SELECTED</cfif>>#ctx.Entry#</cfloop></SELECT></FONT></TD></TR>
<TR><TD>#Request.f#<INPUT TYPE="checkbox" NAME="UseStudioAuthentication" VALUE="1"<cfif S.UseStudioAuthentication EQ 1> CHECKED</cfif>> Use KoldFusion Studio Authentication</FONT></TD>
	<TD>#Request.f#Security context <SELECT NAME="StudioContext"><OPTION VALUE="">(none)<cfloop query="ctx"><OPTION<cfif ctx.Entry EQ S.StudioContext> SELECTED</cfif>>#ctx.Entry#</cfloop></SELECT></FONT></TD></TR>
<TR><TD COLSPAN=2>#Request.f#<INPUT TYPE="checkbox" NAME="UseSandboxes" VALUE="1"<cfif S.UseSandboxes EQ 1> CHECKED</cfif>> Use Security Sandbox Settings</FONT></TD></TR>
<TR><TD COLSPAN=2>#Request.f#<INPUT TYPE="checkbox" NAME="ProtectAllResources" VALUE="1"<cfif S.ProtectAllResources EQ 1> CHECKED</cfif>> Protect all resources of protected resource types by default</FONT></TD></TR>
</TABLE></BLOCKQUOTE>
<HR NOSHADE SIZE=1>
<INPUT TYPE="button" VALUE="User Directories" onClick="location='userdirs.cfm'">
<INPUT TYPE="button" VALUE="Security Contexts" onClick="location='contexts.cfm'">
<INPUT TYPE="button" VALUE="Security Sandboxes" onClick="location='sandboxes.cfm'">
<INPUT TYPE="button" VALUE="Resources" onClick="location='resources.cfm'">
<INPUT TYPE="button" VALUE="Map" onClick="location='securitymap.cfm'">
&nbsp;&nbsp;<INPUT TYPE="submit" NAME="Apply" VALUE="Apply">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
