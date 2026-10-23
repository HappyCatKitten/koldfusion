<!--- View a log file --->
<cfparam name="URL.file" default="">
<cfparam name="URL.lines" default="200">
<cfregistry action="get" branch="#Request.reg#\Server" entry="LogDirectory" variable="logDir">
<cfif Find("/", URL.file) OR Find("..", URL.file) OR NOT Len(URL.file)><cflocation url="logfiles.cfm" addtoken="no"></cfif>
<cfset path = logDir & "/" & URL.file>
<cfif IsDefined("URL.download")>
	<cfheader name="Content-Disposition" value="attachment; filename=#URL.file#">
	<cfcontent type="text/plain" file="#path#">
</cfif>
<cffile action="read" file="#path#" variable="contents">
<cfset all = ListToArray(contents, Chr(10))>
<cfset first = Max(1, ArrayLen(all) - URL.lines + 1)>
<cfset pageTitle = "Log File: #UCase(URL.file)#">
<cfinclude template="../_header.cfm">
<cfoutput>
<P>#Request.f#Showing the last #ArrayLen(all) - first + 1# of #ArrayLen(all)# lines.
<A HREF="viewlog.cfm?file=#URLEncodedFormat(URL.file)#&lines=1000">Show 1000</A> |
<A HREF="viewlog.cfm?file=#URLEncodedFormat(URL.file)#&download=1">Download</A> |
<A HREF="logfiles.cfm?delete=#URLEncodedFormat(URL.file)#" onClick="return confirm('Delete this log file?')">Delete</A> |
<A HREF="logfiles.cfm">Back to Log Files</A></FONT>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0>
<cfloop index="i" from="#ArrayLen(all)#" to="#first#" step="-1">
	<cfset line = all[i]>
	<cfset sev = Replace(ListFirst(line), '"', "", "ALL")>
	<TR BGCOLOR="#IIf(i MOD 2, DE('FFFFFF'), DE('FFFBF0'))#"><TD><FONT FACE="Courier New, Courier" SIZE=1<cfif sev EQ "Error"> COLOR="##CC0000"<cfelseif sev EQ "Warning"> COLOR="##996600"</cfif>>#HTMLEditFormat(line)#</FONT></TD></TR>
</cfloop>
</TABLE>
</cfoutput>
<cfinclude template="../_footer.cfm">
