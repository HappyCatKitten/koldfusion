<!--- shared data source list; set kind, pageTitle, driverLabel, drivers (| list or "" for free text) --->
<cfset dsns = KFUSION_DSNLIST()>
<cfset results = StructNew()>
<cfif IsDefined("Form.VerifyAll")>
	<cfloop query="dsns"><cfif dsns.Kind EQ kind><cfset results[dsns.Name] = KFUSION_VERIFYDSN(dsns.Name)></cfif></cfloop>
</cfif>
<cfinclude template="../_header.cfm">
<cfoutput>
<FORM ACTION="dsnedit.cfm" METHOD="POST"><INPUT TYPE="hidden" NAME="Kind" VALUE="#kind#"><INPUT TYPE="hidden" NAME="IsNew" VALUE="1">
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="##669966">
	<TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Data Source Name</B></FONT></TD>
	<TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>#driverLabel#</B></FONT></TD>
	<TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Verify</B></FONT></TD></TR>
<TR BGCOLOR="##FFFFFF">
	<TD><INPUT TYPE="text" NAME="DSN" SIZE=20></TD>
	<TD><cfif Len(drivers)><SELECT NAME="Driver"><cfloop list="#drivers#" index="d" delimiters="|"><OPTION>#d#</cfloop></SELECT><cfelse><INPUT TYPE="text" NAME="Driver" SIZE=25 VALUE="SQLOLEDB"></cfif>
	<INPUT TYPE="submit" VALUE="Add..."></TD><TD></TD></TR>
<cfset row = 0>
<cfloop query="dsns">
	<cfif dsns.Kind EQ kind>
	<cfset row = row + 1>
	<TR BGCOLOR="#IIf(row MOD 2, DE('FFFBF0'), DE('FFFFFF'))#">
	<TD>#Request.f#<B><A HREF="dsnedit.cfm?DSN=#URLEncodedFormat(dsns.Name)#">#dsns.Name#</A></B></FONT></TD>
	<TD>#Request.f##dsns.Driver#</FONT></TD>
	<TD>#Request.f#<cfif StructKeyExists(results, dsns.Name)><cfif results[dsns.Name].OK><FONT COLOR="##008000">Verified</FONT><cfelse><FONT COLOR="##CC0000">Failed</FONT></cfif><cfelse><A HREF="verify.cfm?DSN=#URLEncodedFormat(dsns.Name)#&back=#kind#">Verify</A></cfif></FONT></TD></TR>
	</cfif>
</cfloop>
</TABLE>
</FORM>
<FORM ACTION="#GetFileFromPath(GetBaseTemplatePath())#" METHOD="POST"><INPUT TYPE="submit" NAME="VerifyAll" VALUE="Verify All"></FORM>
<P>#Request.f#<I>Every KoldFusion data source, whichever driver it names, is served by the built-in KoldFusion Flat-File Driver:
each database is a directory of tables under <TT>#KFUSION_SERVERINFO().Root#/db</TT>.</I></FONT>
</cfoutput>
<cfinclude template="../_footer.cfm">
