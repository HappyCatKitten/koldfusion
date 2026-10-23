<!--- Left-hand navigation, after the 4.x Administrator --->
<cfset sections = ArrayNew(1)>
<cfset sections[1] = "server|Settings=server/settings.cfm|Web Server &amp; SSL=server/webserver.cfm|Caching=server/caching.cfm|Basic Security=server/basicsecurity.cfm|Advanced Security=server/advancedsecurity.cfm|Variables=server/variables.cfm|Locking=server/locking.cfm|Mappings=server/mappings.cfm|Java=server/java.cfm|Version Info=server/versioninfo.cfm">
<cfset sections[2] = "datasources|ODBC=datasources/odbc.cfm|Native Drivers=datasources/native.cfm|OLE DB=datasources/oledb.cfm|Verify Data Source=datasources/verify.cfm">
<cfset sections[3] = "extensions|CFX Tags=extensions/cfx.cfm|Applets=extensions/applets.cfm">
<cfset sections[4] = "logging|Settings=logging/settings.cfm|Mail Logging=logging/maillog.cfm|Log Files=logging/logfiles.cfm">
<cfset sections[5] = "automated tasks|Settings=tasks/settings.cfm|Scheduled Tasks=tasks/tasks.cfm">
<cfset sections[6] = "miscellaneous|Mail=misc/mail.cfm|Debugging=misc/debugging.cfm|Verity=misc/verity.cfm|Source Control=misc/sourcecontrol.cfm">
<HTML>
<HEAD><TITLE>Navigation</TITLE></HEAD>
<BODY BGCOLOR="#99CC99" BACKGROUND="images/pinstripe.gif" LINK="#0000FF" VLINK="#0000FF" ALINK="#FF0000"
      LEFTMARGIN=0 TOPMARGIN=0 MARGINWIDTH=0 MARGINHEIGHT=0>
<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH="100%">
<TR>
	<TD WIDTH=27 HEIGHT=20><IMG SRC="images/spacer.gif" WIDTH=27 HEIGHT=20></TD>
	<TD ALIGN=RIGHT VALIGN=TOP><TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD BGCOLOR="#FFFFFF" WIDTH=18 HEIGHT=18><IMG SRC="images/spacer.gif" WIDTH=18 HEIGHT=18></TD></TR></TABLE></TD>
</TR>
<TR>
	<TD WIDTH=27>&nbsp;</TD>
	<TD VALIGN=TOP>
	<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH="100%" BGCOLOR="#669966">
	<TR><TD>
	<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH="100%">
	<cfoutput>
	<cfloop index="i" from="1" to="#ArrayLen(sections)#">
		<cfset entries = sections[i]>
		<TR><TD BGCOLOR="##003399" HEIGHT=20>&nbsp;<FONT FACE="Arial, Helvetica" SIZE="2" COLOR="##FFFFFF"><B>#ListFirst(entries, "|")#</B></FONT></TD></TR>
		<TR><TD BGCOLOR="##FFFFFF" HEIGHT=1><IMG SRC="images/spacer.gif" WIDTH=1 HEIGHT=1></TD></TR>
		<TR><TD BGCOLOR="##99CC99"><TABLE BORDER=0 CELLPADDING=1 CELLSPACING=0><TR><TD WIDTH=8>&nbsp;</TD><TD><FONT FACE="Arial, Helvetica" SIZE="1" STYLE="font-size:11px">
		<cfloop index="item" list="#ListRest(entries, "|")#" delimiters="|">
			<A HREF="#ListLast(item, "=")#" TARGET="main">#ListFirst(item, "=")#</A><BR>
		</cfloop>
		</FONT></TD></TR></TABLE></TD></TR>
		<TR><TD BGCOLOR="##FFFFFF" HEIGHT=2><IMG SRC="images/spacer.gif" WIDTH=1 HEIGHT=2></TD></TR>
	</cfloop>
	</cfoutput>
	</TABLE>
	</TD></TR>
	</TABLE>
	<BR>
	<FONT FACE="Arial, Helvetica" SIZE="1">
	<A HREF="/" TARGET="_top">Server Home</A><BR>
	<cfif Request.useAdminPw EQ "1"><A HREF="login.cfm?logout=1" TARGET="_top">Logout</A><BR></cfif>
	</FONT>
	<BR>
	</TD>
</TR>
</TABLE>
</BODY>
</HTML>
