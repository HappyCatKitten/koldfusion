<!--- Scheduled Tasks --->
<cfset msg = "">
<cfif IsDefined("URL.run")><cfset r = KFUSION_RUNTASK(URL.run)><cfset msg = r.Message></cfif>
<cfif IsDefined("URL.delete")><cfschedule action="delete" task="#URL.delete#"><cfset msg = "The task #URL.delete# has been deleted."></cfif>
<cfregistry action="getall" branch="#Request.reg#\Schedule" name="tasks" type="key" sort="Entry ASC">
<cfset pageTitle = "Scheduled Tasks">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="taskedit.cfm" METHOD="POST">
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="##669966"><cfloop list="Task Name,Operation,Duration,Interval,Last Run," index="h"><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>#h#</B></FONT></TD></cfloop></TR>
<TR BGCOLOR="##FFFFFF"><TD><INPUT TYPE="text" NAME="TaskName" SIZE=20></TD><TD><SELECT NAME="Operation"><OPTION>HTTPRequest</SELECT></TD>
<TD COLSPAN=4><INPUT TYPE="submit" VALUE="Add New Task..."></TD></TR>
<cfloop query="tasks">
	<cfmodule template="../_tags/getreg.cfm" key="Schedule\#tasks.Entry#" variable="T">
	<cfparam name="T.LastRun" default=""><cfparam name="T.enddate" default="">
	<TR BGCOLOR="#IIf(tasks.CurrentRow MOD 2, DE('FFFBF0'), DE('FFFFFF'))#">
	<TD>#Request.f#<B><A HREF="taskedit.cfm?TaskName=#URLEncodedFormat(tasks.Entry)#">#tasks.Entry#</A></B></FONT></TD>
	<TD>#Request.f##T.operation#</FONT></TD>
	<TD>#Request.f##T.startdate#<cfif Len(T.enddate)> - #T.enddate#</cfif></FONT></TD>
	<TD>#Request.f##T.interval#<cfif IsNumeric(T.interval)> sec</cfif></FONT></TD>
	<TD>#Request.f#<cfif Len(T.LastRun)>#DateFormat(T.LastRun, "mm/dd/yy")# #TimeFormat(T.LastRun, "HH:mm")#<cfelse>never</cfif></FONT></TD>
	<TD>#Request.f#<A HREF="tasks.cfm?run=#URLEncodedFormat(tasks.Entry)#">RUN</A> | <A HREF="tasks.cfm?delete=#URLEncodedFormat(tasks.Entry)#" onClick="return confirm('Delete this task?')">Delete</A></FONT></TD></TR>
</cfloop>
</TABLE>
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
