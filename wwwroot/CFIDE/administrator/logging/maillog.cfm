<!--- Mail Logging --->
<cfset msg = "">
<cfif IsDefined("Form.Apply")>
	<cfmodule template="../_tags/setreg.cfm" key="Logging" entry="MailLogSeverity" value="#Form.MailLogSeverity#">
	<cfmodule template="../_tags/setreg.cfm" key="Logging" entry="LogAllMail" value="#IIf(IsDefined('Form.LogAllMail'), 1, 0)#">
	<cfset msg = "Mail logging settings have been applied.">
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="Logging" variable="L">
<cfset pageTitle = "Mail Logging">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="maillog.cfm" METHOD="POST">
<P>#Request.f#<B>Error Log Severity</B><BR>
<SELECT NAME="MailLogSeverity"><cfloop list="Error,Warning,Information" index="s"><OPTION<cfif L.MailLogSeverity EQ s> SELECTED</cfif>>#s#</cfloop></SELECT><BR>
Select the type of SMTP-related error messages to log.</FONT>
<P>#Request.f#<INPUT TYPE="checkbox" NAME="LogAllMail" VALUE="1"<cfif L.LogAllMail EQ 1> CHECKED</cfif>>
<B>Log all email messages sent by KoldFusion</B><BR>Save the content of all email messages to a log file.</FONT>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Apply" VALUE="Apply"> <INPUT TYPE="reset" VALUE="Cancel">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
