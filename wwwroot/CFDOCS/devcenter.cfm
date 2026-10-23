<!--- /CFDOCS/devcenter.cfm - the Gibson Developer Center --->
<cfset pageTitle = "Developer Center">
<cfset section = "devcenter.cfm">
<cfparam name="URL.download" default="">
<cfparam name="URL.modem" default="28800">
<cfinclude template="snippets/_catalog.cfm">

<!--- tip of the day: changes daily --->
<cfset Tips = ArrayNew(1)>
<cfset ArrayAppend(Tips, "Put CFSILENT around the setup code in Application.cfm and your pages will stop starting with forty blank lines.")>
<cfset ArrayAppend(Tips, "Every value from a form or a URL that goes into SQL deserves a CFQUERYPARAM.")>
<cfset ArrayAppend(Tips, "Use CFPARAM to give optional URL and Form variables a default instead of wrapping everything in IsDefined().")>
<cfset ArrayAppend(Tips, "Lock all reads and writes of Session, Application and Server variables with CFLOCK. Yes, all of them.")>
<cfset ArrayAppend(Tips, "CACHEDWITHIN=""##CreateTimeSpan(0,1,0,0)##"" on a lookup query can take a whole database round trip off every page.")>
<cfset ArrayAppend(Tips, "Variable names are case-insensitive: a query called Thread will happily overwrite a variable called thread.")>
<cfset ArrayAppend(Tips, "Need a literal pound sign inside CFOUTPUT? Double it: ####.")>
<cfset ArrayAppend(Tips, "Run the CFML Syntax Checker over a directory before you upgrade a production server.")>
<cfset ArrayAppend(Tips, "Use four-digit years. It is late 1999. You know why.")>
<cfset Variables.tip = Tips[(DayOfYear(Now()) MOD ArrayLen(Tips)) + 1]>

<!--- downloads: name | size in KB | description, separated by ~ --->
<cfset Downloads = "KoldFusion Studio 4.5 (30-day trial)|22900|The IDE: tag editors, Expression Builder, remote development and a debugger.~KoldFusion Server 4.5.1 Update|8400|Fixes for the issues listed in the Release Notes.~CFX Developer Kit|640|Headers and samples for writing CFX tags in C and C++.~Custom Tag Gallery CD image|98000|Over 500 custom tags from the community. Some of them work.~Y2K Template Scanner|180|Finds two-digit year masks in your templates.">
<cfset Modems = "14400=14.4K modem,28800=28.8K modem,56000=56K modem,128000=ISDN (128K),1544000=T1 line">

<cfinclude template="_siteheader.cfm">
<FONT FACE="Arial, Helvetica" SIZE=2>
<P>Everything a KoldFusion developer needs, short of a second monitor: tips, tools, downloads and the
whole CFML reference.</P>

<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH="100%"><TR VALIGN=TOP>
<TD WIDTH="49%">
	<TABLE BORDER=0 CELLPADDING=1 CELLSPACING=0 WIDTH="100%" BGCOLOR="#003399"><TR><TD>
	<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0 WIDTH="100%" BGCOLOR="#FFFFF0"><TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>
	<FONT COLOR="#003399"><B>Tip of the day</B></FONT><BR>
	<cfoutput>#HTMLEditFormat(Variables.tip)#</cfoutput>
	</FONT></TD></TR></TABLE></TD></TR></TABLE>
</TD>
<TD WIDTH="2%">&nbsp;</TD>
<TD WIDTH="49%">
	<TABLE BORDER=0 CELLPADDING=1 CELLSPACING=0 WIDTH="100%" BGCOLOR="#669966"><TR><TD>
	<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0 WIDTH="100%" BGCOLOR="#FFFFFF"><TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>
	<FONT COLOR="#669966"><B>CFML of the day</B></FONT><BR>
	<cfif Snippets.RecordCount>
		<cfset Variables.r = (DayOfYear(Now()) * 7 MOD Snippets.RecordCount) + 1>
		<cfoutput><A HREF="langref/#Snippets.Name[Variables.r]#.htm"><B>#Snippets.Title[Variables.r]#</B></A>:
		#HTMLEditFormat(Snippets.Summary[Variables.r])#</cfoutput>
	<cfelse>
		Browse the <A HREF="langref/index.htm">CFML Language Reference</A>.
	</cfif>
	</FONT></TD></TR></TABLE></TD></TR></TABLE>
</TD>
</TR></TABLE>

<H3>Developer tools on this server</H3>
<UL>
<LI><A HREF="langref/index.htm"><B>CFML Language Reference</B></A> and the one-page <A HREF="quickref/index.htm">Quick Reference</A>
<LI><A HREF="snippets/index.cfm"><B>Snippets Launcher</B></A>: a runnable example for every tag and function
<LI><A HREF="cfmlsyntaxcheck/cfmlsyntaxcheck.cfm"><B>CFML Syntax Checker</B></A>: find parse errors without running anything
<LI><A HREF="expeval/ExprCalc.cfm"><B>Expression Evaluator</B></A>: try out expressions and functions interactively
<LI><A HREF="devguide/index.htm"><B>Developing Web Applications with KoldFusion</B></A>: the tutorial
</UL>

<H3>Articles</H3>
<UL>
<LI><B>Fusebox in Fifteen Minutes</B> &middot; Organizing a large application around one index.cfm and a pile of switch statements. <FONT SIZE=1 COLOR="#666666">(Coming soon)</FONT>
<LI><B>WDDX: Sharing Data Between JavaScript and CFML</B> &middot; Serialize a query on the server, use it in the browser. See <A HREF="langref/cfwddx.htm">CFWDDX</A>.
<LI><B>Writing Your First CFX Tag in C</B> &middot; The CFX API explained with CFX_HELLO. See <A HREF="langref/cfx_hello.htm">CFX Tags</A>.
<LI><B>Shopping Carts with Session Variables</B> &middot; Structures, arrays, and why you need CFLOCK. See <A HREF="langref/cflock.htm">CFLOCK</A>.
<LI><B>Surviving the Slashdot Effect</B> &middot; Query caching, trusted cache and a bigger modem.
</UL>

<H3>Downloads</H3>
<FORM ACTION="devcenter.cfm" METHOD="GET">
<FONT FACE="Arial, Helvetica" SIZE=2>Show download times for my
<SELECT NAME="modem">
<cfoutput><cfloop list="#Modems#" index="m"><OPTION VALUE="#ListFirst(m, "=")#"<cfif ListFirst(m, "=") EQ URL.modem> SELECTED</cfif>>#ListLast(m, "=")#</cfloop></cfoutput>
</SELECT>
<INPUT TYPE="submit" VALUE="Calculate"></FONT>
</FORM>
<cfset Variables.bps = Val(URL.modem)>
<cfif Variables.bps LT 9600><cfset Variables.bps = 28800></cfif>
<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=1 BGCOLOR="#999999" WIDTH="100%">
<TR BGCOLOR="#669966">
	<TH ALIGN=LEFT><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF">Download</FONT></TH>
	<TH ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF">Size</FONT></TH>
	<TH ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF">Estimated time</FONT></TH>
</TR>
<cfset Variables.row = 0>
<cfoutput>
<cfloop list="#Downloads#" index="d" delimiters="~">
	<cfset Variables.row = Variables.row + 1>
	<cfset Variables.kb = ListGetAt(d, 2, "|")>
	<!--- 10 bits per byte on the wire, and nobody ever gets the full speed --->
	<cfset Variables.secs = Int(Variables.kb * 1024 * 10 / (Variables.bps * 0.85))>
	<cfif Variables.secs LT 60><cfset Variables.est = "#Variables.secs# seconds">
	<cfelseif Variables.secs LT 3600><cfset Variables.est = "#Int(Variables.secs / 60)# min #Variables.secs MOD 60# sec">
	<cfelse><cfset Variables.est = "#Int(Variables.secs / 3600)# hr #Int((Variables.secs MOD 3600) / 60)# min"></cfif>
	<cfif Variables.row MOD 2><cfset Variables.bg = "FFFFFF"><cfelse><cfset Variables.bg = "FFFBF0"></cfif>
	<TR BGCOLOR="###Variables.bg#" VALIGN=TOP>
	<TD><FONT FACE="Arial, Helvetica" SIZE=2><B>#ListGetAt(d, 1, "|")#</B><BR><FONT SIZE=1>#ListGetAt(d, 3, "|")#</FONT></FONT></TD>
	<TD ALIGN=RIGHT NOWRAP><FONT FACE="Arial, Helvetica" SIZE=2><cfif Variables.kb GE 1024>#NumberFormat(Variables.kb / 1024, "999.9")# MB<cfelse>#Variables.kb# KB</cfif></FONT></TD>
	<TD ALIGN=RIGHT NOWRAP><FONT FACE="Arial, Helvetica" SIZE=2>#Variables.est#<cfif Variables.secs GT 7200><BR><FONT SIZE=1 COLOR="##CC0000">order the CD</FONT></cfif></FONT></TD>
	</TR>
</cfloop>
</cfoutput>
</TABLE>
<P><FONT SIZE=1>Downloads are temporarily unavailable while we upgrade our FTP server to a faster 486. Please try again in 1999.</FONT></P>

<H3>Mailing lists</H3>
<P>Subscribe to <B>KF-Talk</B> by sending a message with <CODE>SUBSCRIBE KF-TALK</CODE> in the body to
<CODE>listserv@localhost</CODE>. Expect roughly 120 messages a day, a third of them asking how to make the
Administrator password go away.</P>
</FONT>
<cfinclude template="_sitefooter.cfm">
