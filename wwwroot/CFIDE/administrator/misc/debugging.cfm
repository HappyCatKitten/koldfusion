<!--- Debug Settings --->
<cfset opts = "EnablePerformanceMonitoring|Enable performance monitoring|allows a performance monitor to display information about a running KoldFusion Application Server. On UNIX a command line utility, kfstat, displays the same information. (You must restart the KoldFusion Application Server in order for changes in this setting to take effect.)~EnableStackTrace|Enable CFML stack trace|generates information in CFCATCH.TAGCONTEXT describing the tags that were executing when an exception was thrown.~ShowVariables|Show variables|displays the names and values of all CGI, URL, form, and cookie variables.~ShowProcessingTime|Show processing time|shows the time, in milliseconds, to process the entire page.~DetailView|Detail View|breaks processing time down by template (requires Show processing time).~ShowSQL|Show SQL and data source name|permits the display of the data source name and the SQL statement in messages about database query errors.~ShowQueryInfo|Show query information|displays the record count, processing time, and the SQL statement for each query executed.~ShowTemplatePath|Display the template path in error messages|includes the full path of the template in error messages. You may want to turn this off on production servers.">
<cfset msg = "">
<cfmodule template="../_tags/getreg.cfm" key="Debug" variable="D">
<cfif IsDefined("Form.Apply")>
	<cfloop list="#opts#" index="o" delimiters="~">
		<cfset f = ListFirst(o, "|")>
		<cfmodule template="../_tags/setreg.cfm" key="Debug" entry="#f#" value="#IIf(IsDefined('Form.' & f), 1, 0)#">
	</cfloop>
	<cfset msg = "Debug settings have been applied.">
</cfif>
<cfif IsDefined("Form.AddIP") AND Len(Trim(Form.IPAddress))>
	<cfif NOT ListFind(D.DebugIPs, Trim(Form.IPAddress))>
		<cfmodule template="../_tags/setreg.cfm" key="Debug" entry="DebugIPs" value="#ListAppend(D.DebugIPs, Trim(Form.IPAddress))#">
	</cfif>
	<cfset msg = "The IP address has been added.">
</cfif>
<cfif IsDefined("Form.RemoveIP") AND IsDefined("Form.IPList")>
	<cfset newList = "">
	<cfloop list="#D.DebugIPs#" index="ip"><cfif NOT ListFind(Form.IPList, ip)><cfset newList = ListAppend(newList, ip)></cfif></cfloop>
	<cfmodule template="../_tags/setreg.cfm" key="Debug" entry="DebugIPs" value="#newList#">
	<cfset msg = "The selected addresses have been removed.">
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="Debug" variable="D">
<cfset pageTitle = "Debug Settings">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="debugging.cfm" METHOD="POST">
<cfloop list="#opts#" index="o" delimiters="~">
	<cfset f = ListGetAt(o, 1, "|")>
	<P>#Request.f#<INPUT TYPE="checkbox" NAME="#f#" VALUE="1"<cfif D[f] EQ 1> CHECKED</cfif>>
	<B>#ListGetAt(o, 2, "|")#</B> - #ListGetAt(o, 3, "|")#</FONT>
</cfloop>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Apply" VALUE="Apply"> <INPUT TYPE="reset" VALUE="Cancel">
<P><TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>Restrict debug output to selected IP addresses</B></FONT></TD></TR></TABLE>
<P>#Request.f#Select the IP addresses that should receive debug output. When the list is empty, every client receives it.
<TABLE BORDER=0 CELLPADDING=3><TR VALIGN=TOP>
<TD>#Request.f#IP Address<BR><INPUT TYPE="text" NAME="IPAddress" SIZE=16> <INPUT TYPE="submit" NAME="AddIP" VALUE="Add"></FONT></TD>
<TD><SELECT NAME="IPList" SIZE=5 MULTIPLE STYLE="width:150px"><cfloop list="#D.DebugIPs#" index="ip"><OPTION>#ip#</cfloop></SELECT><BR>
<INPUT TYPE="submit" NAME="RemoveIP" VALUE="Remove"></TD></TR></TABLE></FONT>
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
