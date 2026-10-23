<!--- Log Files --->
<cfregistry action="get" branch="#Request.reg#\Server" entry="LogDirectory" variable="logDir">
<cfset msg = "">
<cfif IsDefined("URL.delete") AND NOT Find("/", URL.delete) AND NOT Find("..", URL.delete)>
	<cffile action="delete" file="#logDir#/#URL.delete#">
	<cfset msg = "The log file #URL.delete# has been deleted.">
</cfif>
<cfdirectory action="list" directory="#logDir#" name="logs" filter="*.log" sort="Name ASC">
<cfset pageTitle = "Log Files (#logDir#)">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="##669966"><cfloop list="File Name,Size,Last Modified,Attributes" index="h"><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>#h#</B></FONT></TD></cfloop></TR>
<cfloop query="logs">
<TR BGCOLOR="#IIf(logs.CurrentRow MOD 2, DE('FFFBF0'), DE('FFFFFF'))#">
<TD>#Request.f#<IMG SRC="../images/file.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE> <cfif logs.Size GT 0><B><A HREF="viewlog.cfm?file=#URLEncodedFormat(logs.Name)#">#UCase(logs.Name)#</A></B><cfelse>#UCase(logs.Name)#</cfif></FONT></TD>
<TD>#Request.f##NumberFormat(logs.Size, ",")#</FONT></TD><TD>#Request.f##logs.DateLastModified#</FONT></TD><TD>#Request.f#A</FONT></TD></TR>
</cfloop>
<cfif NOT logs.RecordCount><TR><TD COLSPAN=4>#Request.f#<I>No log files.</I></FONT></TD></TR></cfif>
</TABLE>
</cfoutput>
<cfinclude template="../_footer.cfm">
