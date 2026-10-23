<!--- /CFDOCS/dochome.cfm - the documentation home page ("the bookshelf") --->
<cfset pageTitle = "KoldFusion Documentation">
<cfset upURL = "/CFDOCS/index.cfm">
<cfset nextURL = "/CFDOCS/admin/index.htm">
<cfinclude template="_docheader.cfm">
<cfinclude template="snippets/_catalog.cfm">
<cfset Variables.nTags = 0>
<cfloop query="Snippets"><cfif Snippets.Kind EQ "Tag"><cfset Variables.nTags = Variables.nTags + 1></cfif></cfloop>

<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH="100%">
<TR VALIGN=BOTTOM>
	<TD><IMG SRC="/images/welcome_logo.gif" WIDTH=400 HEIGHT=105 ALT="KoldFusion 4.5"></TD>
	<TD ALIGN=RIGHT><FONT SIZE=1 COLOR="#666666">Version 4.5<BR>Online documentation set</FONT></TD>
</TR>
</TABLE>
<HR NOSHADE SIZE=2 COLOR="#003399">

<H1>KoldFusion Documentation</H1>
<P>Welcome to the complete KoldFusion 4.5 documentation set, online and fully hyperlinked. Every book
is also available in print for the cost of shipping, a self-addressed envelope and roughly
eleven pounds of shelf space.</P>

<H4><IMG SRC="/CFIDE/administrator/images/file.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
<A HREF="admin/index.htm">Administering KoldFusion Server</A></H4>
<BLOCKQUOTE>How to install, configure and keep a KoldFusion server healthy: one chapter for each page of the
<A HREF="/CFIDE/administrator/index.cfm">KoldFusion Administrator</A>, from server settings and caching to data
sources, CFX tags, logging, scheduled tasks, mail and Verity collections.</BLOCKQUOTE>

<H4><IMG SRC="/CFIDE/administrator/images/file.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
<A HREF="devguide/index.htm">Developing Web Applications with KoldFusion</A></H4>
<BLOCKQUOTE>A hands-on tutorial for HTML authors moving up to dynamic pages. Short chapters introduce CFML,
queries, forms, database updates, the application framework, error handling and reusable code, each with
small examples you can run right from the page.</BLOCKQUOTE>

<H4><IMG SRC="/CFIDE/administrator/images/file.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
<A HREF="langref/index.htm">CFML Language Reference</A></H4>
<BLOCKQUOTE>Every tag and function of the KoldFusion Markup Language<cfif Snippets.RecordCount><cfoutput>
(#Variables.nTags# tags and #Evaluate(Snippets.RecordCount - Variables.nTags)# functions with runnable examples)</cfoutput></cfif>,
grouped by category, with syntax, attribute descriptions, usage notes and an <B>Example</B> button
that runs the example on your server. See also the <A HREF="snippets/index.cfm">Snippets Launcher</A>.</BLOCKQUOTE>

<H4><IMG SRC="/CFIDE/administrator/images/file.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
<A HREF="quickref/index.htm">CFML Quick Reference</A></H4>
<BLOCKQUOTE>The whole language on one long page: the syntax of every tag, the signature of every function and
the operator table. Print it, laminate it, tape it to the side of your 17-inch monitor.</BLOCKQUOTE>

<H3>More information</H3>
<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR><TD><IMG SRC="/CFIDE/administrator/images/arrow.gif" WIDTH=16 HEIGHT=16></TD><TD><A HREF="releasenotes.cfm">Release Notes</A></TD>
	<TD>Late-breaking news, known issues and the fine print.</TD></TR>
<TR><TD><IMG SRC="/CFIDE/administrator/images/arrow.gif" WIDTH=16 HEIGHT=16></TD><TD><A HREF="newfeatures.cfm">New Features in 4.5</A></TD>
	<TD>What changed since 4.0, and why you will love CFQUERYPARAM.</TD></TR>
<TR><TD><IMG SRC="/CFIDE/administrator/images/arrow.gif" WIDTH=16 HEIGHT=16></TD><TD><A HREF="install.cfm">Installation Support</A></TD>
	<TD>System requirements, installing, and testing your installation.</TD></TR>
<TR><TD><IMG SRC="/CFIDE/administrator/images/check.gif" WIDTH=16 HEIGHT=16></TD><TD><A HREF="cfmlsyntaxcheck/cfmlsyntaxcheck.cfm">CFML Syntax Checker</A></TD>
	<TD>Check templates for syntax errors before your users find them.</TD></TR>
<TR><TD><IMG SRC="/CFIDE/administrator/images/help.gif" WIDTH=16 HEIGHT=16></TD><TD><A HREF="expeval/ExprCalc.cfm">Expression Evaluator</A></TD>
	<TD>Try out CFML expressions interactively (local use only).</TD></TR>
<TR><TD><IMG SRC="/CFIDE/administrator/images/folder.gif" WIDTH=16 HEIGHT=16></TD><TD><A HREF="examplehome.cfm">Example Applications</A></TD>
	<TD>Complete sample applications with source.</TD></TR>
</TABLE>

<P><FONT SIZE=1>Using Netscape Navigator 4? The documentation looks its best at 800x600 or higher with
&quot;Enable style sheets&quot; switched on. Readers with Lynx will be pleased to hear that every
icon has ALT text.</FONT></P>
<cfinclude template="_docfooter.cfm">
