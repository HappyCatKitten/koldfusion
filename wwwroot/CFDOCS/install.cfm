<!--- /CFDOCS/install.cfm - Installation Support --->
<cfset pageTitle = "Installation Support - KoldFusion 4.5">
<cfset prevURL = "/CFDOCS/newfeatures.cfm">
<cfset nextURL = "/CFDOCS/dochome.cfm">
<cfinclude template="_docheader.cfm">

<H1>Installation Support</H1>
<P>Congratulations: if you can read this page, KoldFusion is installed and running, because this page is
itself a CFML template. The rest of this page helps you check that everything else is in order too.</P>

<H2>Quick self-test</H2>
<P>The server just checked a few things on your behalf:</P>
<cfset Variables.webRoot = ExpandPath("/")>
<cfset Variables.kfRoot = GetDirectoryFromPath(Left(Variables.webRoot, Len(Variables.webRoot) - 1)) & "kfroot/">
<cfset Variables.checks = ArrayNew(1)>
<!--- each check: label | ok (1/0) | detail --->
<cfset ArrayAppend(Variables.checks, "CFML processing|1|You are looking at the result.")>
<cftry>
	<cfquery name="Variables.q" datasource="cfsnippets">SELECT COUNT(*) AS N FROM Employees</cfquery>
	<cfset ArrayAppend(Variables.checks, "Data source cfsnippets|1|#Variables.q.N# employees on file")>
	<cfcatch type="Any"><cfset ArrayAppend(Variables.checks, "Data source cfsnippets|0|#CFCATCH.Message#")></cfcatch>
</cftry>
<cftry>
	<cfquery name="Variables.q" datasource="cfexamples">SELECT 1 AS One</cfquery>
	<cfset ArrayAppend(Variables.checks, "Data source cfexamples|1|reachable")>
	<cfcatch type="Any"><cfset ArrayAppend(Variables.checks, "Data source cfexamples|0|#CFCATCH.Message#")></cfcatch>
</cftry>
<cfset ArrayAppend(Variables.checks, "Install directory (C:\CFUSION)|#DirectoryExists(Variables.kfRoot)#|kfroot/")>
<cfset ArrayAppend(Variables.checks, "Registry file|#FileExists(Variables.kfRoot & 'registry/kf.registry')#|kfroot/registry/kf.registry")>
<cfset ArrayAppend(Variables.checks, "Log directory|#DirectoryExists(Variables.kfRoot & 'log')#|kfroot/log/")>
<cfset ArrayAppend(Variables.checks, "Mail spool|#DirectoryExists(Variables.kfRoot & 'mail')#|kfroot/mail/")>
<cfset ArrayAppend(Variables.checks, "Temporary directory|#DirectoryExists(GetTempDirectory())#|#GetTempDirectory()#")>
<cfset ArrayAppend(Variables.checks, "Form validation script|#FileExists(ExpandPath('/CFIDE/scripts/cfform.js'))#|/CFIDE/scripts/cfform.js")>
<cfset ArrayAppend(Variables.checks, "Year 2000|#IsLeapYear(2000)#|February 29, 2000 exists. Phew.")>
<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=1 BGCOLOR="#999999">
<TR BGCOLOR="#669966"><TH ALIGN=LEFT><FONT COLOR="#FFFFFF">Check</FONT></TH><TH><FONT COLOR="#FFFFFF">Status</FONT></TH><TH ALIGN=LEFT><FONT COLOR="#FFFFFF">Details</FONT></TH></TR>
<cfoutput>
<cfloop index="i" from="1" to="#ArrayLen(Variables.checks)#">
	<cfset Variables.c = Variables.checks[i]>
	<cfif i MOD 2><cfset Variables.bg = "FFFFFF"><cfelse><cfset Variables.bg = "FFFBF0"></cfif>
	<TR BGCOLOR="###Variables.bg#">
	<TD>#ListGetAt(Variables.c, 1, "|")#</TD>
	<TD ALIGN=CENTER><cfif ListGetAt(Variables.c, 2, "|")><IMG SRC="/CFIDE/administrator/images/check.gif" WIDTH=16 HEIGHT=16 ALT="OK"><cfelse><IMG SRC="/CFIDE/administrator/images/x.gif" WIDTH=16 HEIGHT=16 ALT="Problem"></cfif></TD>
	<TD><FONT SIZE=1>#HTMLEditFormat(ListRest(ListRest(Variables.c, "|"), "|"))#</FONT></TD>
	</TR>
</cfloop>
</cfoutput>
</TABLE>
<P>For a fuller test, including a sample query, run <A HREF="testinstallation/test.cfm">Test your Installation</A>.</P>

<H2>System requirements</H2>
<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=1 BGCOLOR="#999999">
<TR BGCOLOR="#669966"><TH ALIGN=LEFT><FONT COLOR="#FFFFFF"></FONT></TH><TH ALIGN=LEFT><FONT COLOR="#FFFFFF">Minimum</FONT></TH><TH ALIGN=LEFT><FONT COLOR="#FFFFFF">Recommended</FONT></TH></TR>
<TR BGCOLOR="#FFFFFF"><TD><B>Processor</B></TD><TD>Pentium 166 MHz</TD><TD>Pentium II 400 MHz or better</TD></TR>
<TR BGCOLOR="#FFFBF0"><TD><B>Memory</B></TD><TD>64 MB RAM</TD><TD>128 MB RAM (it is 1999, treat yourself)</TD></TR>
<TR BGCOLOR="#FFFFFF"><TD><B>Disk</B></TD><TD>100 MB free</TD><TD>A whole 4.3 GB drive of its own</TD></TR>
<TR BGCOLOR="#FFFBF0"><TD><B>Operating system</B></TD><TD COLSPAN=2>Any POSIX system with a C compiler: Linux, Solaris, HP-UX, the BSDs. The Windows NT 4.0 (Service Pack 4) edition is sold separately.</TD></TR>
<TR BGCOLOR="#FFFFFF"><TD><B>Web browser</B></TD><TD COLSPAN=2>Netscape Navigator 4.7 or Microsoft Internet Explorer 4.01, with JavaScript enabled for the Administrator and Java enabled for the applet form controls.</TD></TR>
</TABLE>

<H2>Installing</H2>
<OL>
<LI>Unpack the distribution and change to its directory.
<LI>Build the server with <CODE>make</CODE>. This produces <CODE>bin/kfserver</CODE> and the sample CFX tag libraries.
<LI>Start the server: <CODE>./bin/kfserver</CODE>. It listens on port 8500 of 127.0.0.1. Use <CODE>-p</CODE> to choose another
    port and <CODE>-b</CODE> to listen on another address.
<LI>Point your browser at <CODE>http://127.0.0.1:8500/</CODE>. The welcome page appears.
<LI>Open the <A HREF="/CFIDE/administrator/index.cfm">KoldFusion Administrator</A> and change the Administrator password
    (it starts out as <CODE>admin</CODE>, which is not a secret anyone has ever failed to guess).
</OL>
<P>The sample data sources are created the first time the server starts. To restore one to its original state, stop the
server, delete its directory under <CODE>kfroot/db/</CODE> and start the server again.</P>
<P>Want to try a page without starting the server at all? <CODE>./bin/kfserver --run wwwroot/CFDOCS/install.cfm</CODE>
prints the page, HTTP headers and all, to your terminal.</P>

<H2>Troubleshooting</H2>
<DL>
<DT><B>The browser says it cannot connect.</B></DT>
<DD>Is the server running, and are you using the right port? Another program may already be using port 8500; start
    KoldFusion with <CODE>-p 8501</CODE>.</DD>
<DT><B>&quot;Data source cfsnippets could not be found.&quot;</B></DT>
<DD>Check the data source on the <A HREF="/CFIDE/administrator/datasources/odbc.cfm">ODBC</A> page of the Administrator and
    press Verify. If it is missing, re-create it, or re-seed it as described above.</DD>
<DT><B>I forgot the Administrator password.</B></DT>
<DD>Stop the server, edit <CODE>kfroot/registry/kf.registry</CODE> and set <CODE>UseAdminPassword</CODE> to 0 under the
    Server key. Then restart, log in, and set a new password you will remember. We recommend not writing it on the monitor.</DD>
<DT><B>Pages show the CFML source instead of running it.</B></DT>
<DD>You opened the file directly from disk (<CODE>file:///</CODE>). Templates must be requested through the server.</DD>
<DT><B>Something else.</B></DT>
<DD>Look in the log files (<A HREF="/CFIDE/administrator/logging/logfiles.cfm">Logging &gt; Log Files</A>), read the
    <A HREF="releasenotes.cfm">Release Notes</A>, then visit <A HREF="support.cfm">Technical Support</A>.</DD>
</DL>

<cfinclude template="_docfooter.cfm">
