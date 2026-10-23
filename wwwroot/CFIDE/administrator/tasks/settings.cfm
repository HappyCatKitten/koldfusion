<!--- Scheduler Settings --->
<cfset msg = "">
<cfif IsDefined("Form.Apply")>
	<cfif IsNumeric(Form.RefreshInterval) AND Form.RefreshInterval GT 0>
		<cfmodule template="../_tags/setreg.cfm" key="Scheduler" entry="RefreshInterval" value="#Form.RefreshInterval#">
		<cfmodule template="../_tags/setreg.cfm" key="Scheduler" entry="LogActivity" value="#IIf(IsDefined('Form.LogActivity'), 1, 0)#">
		<cfset msg = "Scheduler settings have been applied.">
	<cfelse><cfset msg = "The refresh interval must be a positive number."></cfif>
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="Scheduler" variable="S">
<cfset pageTitle = "Scheduler Settings">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="settings.cfm" METHOD="POST">
<P>#Request.f#<B>Scheduler Refresh Interval:</B> <INPUT TYPE="text" NAME="RefreshInterval" VALUE="#S.RefreshInterval#" SIZE=3> <B>minutes</B><BR>
Determines how often the scheduler checks the saved scheduled task list for new tasks. On refresh, the scheduler updates the active
task list, which gets inspected every minute to determine what tasks are ready to be run.</FONT>
<P>#Request.f#<INPUT TYPE="checkbox" NAME="LogActivity" VALUE="1"<cfif S.LogActivity EQ 1> CHECKED</cfif>> <B>Log scheduled task activity</B><BR>
Write an entry to schedule.log each time the scheduler runs a task.</FONT>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Apply" VALUE="Apply"> <INPUT TYPE="reset" VALUE="Cancel">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
