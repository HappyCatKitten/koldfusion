<!--- /CFDOCS/releasenotes.cfm - KoldFusion 4.5 Release Notes --->
<cfset pageTitle = "KoldFusion 4.5 Release Notes">
<cfset nextURL = "/CFDOCS/newfeatures.cfm">
<cfinclude template="_docheader.cfm">

<H1>KoldFusion Server 4.5 Release Notes</H1>
<cfoutput>
<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=1 BGCOLOR="##999999">
<TR BGCOLOR="##669966"><TH ALIGN=LEFT COLSPAN=2><FONT COLOR="##FFFFFF">This server</FONT></TH></TR>
<TR BGCOLOR="##FFFFFF"><TD><B>Product</B></TD><TD>#Server.ColdFusion.ProductName# #Server.ColdFusion.ProductLevel#</TD></TR>
<TR BGCOLOR="##FFFBF0"><TD><B>Version</B></TD><TD>#Server.ColdFusion.ProductVersion#</TD></TR>
<TR BGCOLOR="##FFFFFF"><TD><B>Web server</B></TD><TD>#HTMLEditFormat(CGI.SERVER_SOFTWARE)#</TD></TR>
<TR BGCOLOR="##FFFBF0"><TD><B>Operating system</B></TD><TD>#HTMLEditFormat(Server.OS.Name)# #HTMLEditFormat(Server.OS.Version)#</TD></TR>
</TABLE>
</cfoutput>

<P>These notes cover late-breaking information that did not make it into the printed manuals in
time for the shrink-wrap. Please read them before you install, and again before you call
Technical Support. (The second reading is the one that counts.)</P>

<H3>Contents</H3>
<UL>
<LI><A HREF="#about">About this release</A>
<LI><A HREF="#y2k">Year 2000 compliance</A>
<LI><A HREF="#upgrade">Upgrading from KoldFusion 4.0</A>
<LI><A HREF="#unix">Notes for the UNIX edition</A>
<LI><A HREF="#known">Known issues</A>
<LI><A HREF="#errata">Documentation errata</A>
</UL>

<H2><A NAME="about">About this release</A></H2>
<P>KoldFusion 4.5 is a feature release of the KoldFusion Web Application Server. It adds new tags and
functions for safer database access, external programs, Java integration and output control, a
reworked Administrator with new Caching, Locking, Java and Source Control pages, and a long list of fixes.
See <A HREF="newfeatures.cfm">New Features in 4.5</A> for the full tour.</P>
<P>The server reads CFML templates (<CODE>.cfm</CODE>) from the web root and talks to data sources through its
built-in database engine. The sample data sources <CODE>cfsnippets</CODE> and <CODE>cfexamples</CODE> are
installed and registered for you, so the examples in this documentation work out of the box.</P>

<H2><A NAME="y2k">Year 2000 compliance</A></H2>
<P><IMG SRC="/CFIDE/administrator/images/check.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
<B>KoldFusion 4.5 is Y2K compliant.</B> Dates are stored internally as double-precision day counts and will keep
working well past December 31, 9999, by which time we expect a patch to be available.</P>
<UL>
<LI>Two-digit years entered by users are interpreted with a sliding window: 00-29 become 2000-2029,
    30-99 become 1930-1999.
<LI><CODE>DateFormat</CODE> with a <CODE>yy</CODE> mask prints two-digit years, exactly as you asked.
    If your pages print &quot;19100&quot; on New Year's morning, the bug is in your CFML, not in ours.
<LI>Use <CODE>CreateODBCDate</CODE> or <CODE>CFQUERYPARAM</CODE> with <CODE>CF_SQL_DATE</CODE> when passing dates to a database.
<LI>February 29, 2000 is a leap day. <CODE>IsLeapYear(2000)</CODE> agrees.
</UL>

<H2><A NAME="upgrade">Upgrading from KoldFusion 4.0</A></H2>
<UL>
<LI>CFML templates written for 4.0 run unchanged. New reserved words: none. New tags may clash with custom
    tags of the same name only if your custom tag is called <CODE>CF_SILENT</CODE>, which, frankly, would be on you.
<LI>The Administrator now has <B>Caching</B> and <B>Locking</B> pages. Template cache size and
    &quot;Limit database connection inactive time&quot; moved from the Settings page to Caching.
<LI>Data source definitions, mappings, CFX tags and scheduled tasks are kept in the registry
    (<CODE>kfroot/registry/kf.registry</CODE>) and carry over between versions.
<LI>Client variables stored in the registry: consider moving them to a data source, see
    <A HREF="admin/variables.htm">Variables</A> in <I>Administering KoldFusion Server</I>.
</UL>

<H2><A NAME="unix">Notes for the UNIX edition</A></H2>
<P>KoldFusion for UNIX keeps the familiar Windows names in the documentation and the Administrator so that books
and magazine articles still make sense. Translate as follows:</P>
<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=1 BGCOLOR="#999999">
<TR BGCOLOR="#669966"><TH ALIGN=LEFT><FONT COLOR="#FFFFFF">The manuals say</FONT></TH><TH ALIGN=LEFT><FONT COLOR="#FFFFFF">On this server</FONT></TH></TR>
<TR BGCOLOR="#FFFFFF"><TD><CODE>C:\CFUSION</CODE></TD><TD>the <CODE>kfroot/</CODE> directory</TD></TR>
<TR BGCOLOR="#FFFBF0"><TD>the Windows NT registry</TD><TD><CODE>kfroot/registry/kf.registry</CODE> (REGEDIT4 text format)</TD></TR>
<TR BGCOLOR="#FFFFFF"><TD><CODE>C:\CFUSION\LOG</CODE></TD><TD><CODE>kfroot/log/</CODE></TD></TR>
<TR BGCOLOR="#FFFBF0"><TD><CODE>C:\CFUSION\MAIL\SPOOL</CODE></TD><TD><CODE>kfroot/mail/spool/</CODE></TD></TR>
<TR BGCOLOR="#FFFFFF"><TD><CODE>C:\INETPUB\WWWROOT</CODE></TD><TD>the <CODE>wwwroot/</CODE> directory</TD></TR>
<TR BGCOLOR="#FFFBF0"><TD>the Services control panel</TD><TD><CODE>./bin/kfserver</CODE> (use <CODE>-p</CODE> to pick a port)</TD></TR>
</TABLE>

<H2><A NAME="known">Known issues</A></H2>
<UL>
<LI><B>COM, CORBA and Java objects.</B> <CODE>CFOBJECT</CODE> and <CODE>CreateObject</CODE> report an error on this
    platform: COM is a Windows NT technology, no ORB is installed, and the Java Virtual Machine is not loaded.
<LI><B>CFSERVLET, CFREPORT and CFSTOREDPROC</B> are recognized but not available in this edition;
    they throw an exception you can catch with <CODE>CFTRY</CODE>.
<LI><B>CFFTP</B> uses passive-mode FTP only. If your firewall insists on active mode, your firewall wins.
<LI><B>SSL</B> (the <CODE>https://</CODE> listener on port 8543, and <CODE>https://</CODE> URLs in <CODE>CFHTTP</CODE>)
    needs the OpenSSL libraries on the server. Without them the secure listener stays off and <CODE>CFHTTP</CODE>
    refuses <CODE>https://</CODE> URLs. The certificate made at installation is self-signed, so browsers will ask you
    to accept it; the 128-bit VeriSign certificate is currently stuck in the mail. See
    <A HREF="admin/webserver.htm">Web Server and SSL</A>.
<LI><B>Verity.</B> Collections are searched by the built-in engine; the advanced Verity query language is
    supported only in part (simple words, phrases, AND, OR, NOT and wildcards).
<LI><B>Java applet form controls</B> (<CODE>CFGRID</CODE>, <CODE>CFTREE</CODE>, <CODE>CFSLIDER</CODE>, <CODE>CFTEXTINPUT</CODE>)
    need a browser with Java switched on. Navigator 4.7 users on a 56K modem: go and make a sandwich while the applet loads.
<LI><B>Query of queries</B> (<CODE>DBTYPE=&quot;query&quot;</CODE>), <CODE>CFDUMP</CODE> and user-defined functions are
    not part of this release. Rumor has it they will be in the next one.
<LI>The <A HREF="expeval/ExprCalc.cfm">Expression Evaluator</A> only answers to requests from the server itself.
    See the note on that page for the reason.
</UL>

<H2><A NAME="errata">Documentation errata</A></H2>
<UL>
<LI><I>Developing Web Applications</I>, chapter on forms: &quot;validate on the client and trust the client&quot; should of
    course read &quot;validate on the client and <B>never</B> trust the client&quot;.
<LI><I>CFML Language Reference</I>: page numbers in the printed index are off by one after page 404,
    which our technical writers insist is funnier than it sounds.
<LI>The online documentation is updated more often than the printed manuals. When they disagree, believe
    the one with the <B>Example</B> button.
</UL>

<cfinclude template="_docfooter.cfm">
