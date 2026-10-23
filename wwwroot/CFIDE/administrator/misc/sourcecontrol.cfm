<!--- Source Control (4.5, Windows) --->
<cfset msg = "">
<cfif IsDefined("Form.Apply")>
	<cfloop list="SrcSafeIni,WorkingDirectory,Timeout" index="f"><cfmodule template="../_tags/setreg.cfm" key="SourceControl" entry="#f#" value="#Trim(Form[f])#"></cfloop>
	<cfset msg = "Source control settings have been applied.">
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="SourceControl" variable="S">
<cfset pageTitle = "Source Control">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<P>#Request.f#Server-side source control lets KoldFusion Studio check files in and out of a Visual SourceSafe database through
this server. <I>(Visual SourceSafe integration requires Windows NT; on this server the settings are stored but not used.)</I></FONT>
<FORM ACTION="sourcecontrol.cfm" METHOD="POST">
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD>#Request.f#<B>Path to SrcSafe.ini</B></FONT></TD><TD><INPUT TYPE="text" NAME="SrcSafeIni" VALUE="#HTMLEditFormat(S.SrcSafeIni)#" SIZE=45></TD></TR>
<TR><TD>#Request.f#<B>Working directory</B></FONT></TD><TD><INPUT TYPE="text" NAME="WorkingDirectory" VALUE="#HTMLEditFormat(S.WorkingDirectory)#" SIZE=45></TD></TR>
<TR><TD>#Request.f#<B>Operation Timeout</B></FONT></TD><TD>#Request.f#<INPUT TYPE="text" NAME="Timeout" VALUE="#S.Timeout#" SIZE=4> seconds</FONT></TD></TR>
</TABLE>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Apply" VALUE="Apply"> <INPUT TYPE="reset" VALUE="Cancel">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
