<!--- /CFDOCS/snippets/index.cfm - the Snippets Launcher --->
<cfinclude template="_catalog.cfm">
<cfparam name="URL.show" default="all">
<cfif NOT ListFindNoCase("all,tags,functions,new", URL.show)><cfset URL.show = "all"></cfif>
<cfset Variables.local = ListFind("127.0.0.1,::1", CGI.REMOTE_ADDR) GT 0>
<cfset Variables.nTags = 0>
<cfset Variables.nNew = 0>
<cfloop query="Snippets">
	<cfif Snippets.Kind EQ "Tag"><cfset Variables.nTags = Variables.nTags + 1></cfif>
	<cfif Snippets.New45><cfset Variables.nNew = Variables.nNew + 1></cfif>
</cfloop>
<HTML>
<HEAD>
<TITLE>Snippets Launcher - KoldFusion Documentation</TITLE>
<LINK REL="stylesheet" TYPE="text/css" HREF="/CFDOCS/kfdocs.css">
<SCRIPT LANGUAGE="JavaScript">
<!--
function runExample(name) {
	var w = window.open('tagframe.cfm?tagname=' + name, 'kfexample',
		'width=720,height=560,resizable=yes,scrollbars=yes,toolbar=no,status=yes');
	if (w) w.focus();
}
//-->
</SCRIPT>
</HEAD>
<BODY BGCOLOR="#FFFFF0" LINK="#0000CC" VLINK="#663399">
<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=2><TR>
<TD><A HREF="/CFDOCS/dochome.cfm"><IMG SRC="/CFDOCS/images/doc_up.gif" WIDTH=16 HEIGHT=16 BORDER=0 ALT="Documentation home"></A></TD>
<TD><A HREF="/CFDOCS/dochome.cfm"><IMG SRC="/CFDOCS/images/doc_home.gif" WIDTH=16 HEIGHT=16 BORDER=0 ALT="Documentation home"></A></TD>
<TD><A HREF="/CFDOCS/langref/index.htm"><IMG SRC="/CFDOCS/images/doc_index.gif" WIDTH=16 HEIGHT=16 BORDER=0 ALT="CFML Language Reference"></A></TD>
</TR></TABLE>
<FONT SIZE=1 CLASS="booktitle">KoldFusion Documentation</FONT>
<HR NOSHADE SIZE=1>
<H1>Snippets Launcher</H1>
<cfoutput>
<P>Every page of the <A HREF="/CFDOCS/langref/index.htm">CFML Language Reference</A> ends with a small,
working example. This launcher lists all #Snippets.RecordCount# of them (#Variables.nTags# tags,
#Evaluate(Snippets.RecordCount - Variables.nTags)# functions). Click a name to open the example
window: the CFML source on top, the live result below. Click <I>ref</I> to read the reference page.
All examples use the <CODE>cfsnippets</CODE> data source.</P>
<cfif NOT Variables.local>
<P CLASS="note"><IMG SRC="/CFIDE/administrator/images/lock.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
<B>Examples run on the server.</B> For safety they only work when you browse from the server itself
(127.0.0.1). You are at #HTMLEditFormat(CGI.REMOTE_ADDR)#, so the reference pages are as far as you go.</P>
</cfif>
<P><B>Show:</B>
<cfloop list="all=Everything,tags=Tags,functions=Functions,new=New in 4.5 (#Variables.nNew#)" index="opt">
	<cfif ListFirst(opt, "=") EQ URL.show><B>[#ListLast(opt, "=")#]</B><cfelse><A HREF="index.cfm?show=#ListFirst(opt, "=")#">#ListLast(opt, "=")#</A></cfif>
</cfloop>
</P>
</cfoutput>

<cfset Variables.lastKind = "">
<cfoutput query="Snippets" group="Category">
	<cfset Variables.inSection = URL.show EQ "all" OR (URL.show EQ "tags" AND Snippets.Kind EQ "Tag")
		OR (URL.show EQ "functions" AND Snippets.Kind EQ "Function") OR URL.show EQ "new">
	<cfif Variables.inSection>
		<cfif Snippets.Kind NEQ Variables.lastKind>
			<H2><cfif Snippets.Kind EQ "Tag">CFML Tags<cfelse>CFML Functions</cfif></H2>
			<cfset Variables.lastKind = Snippets.Kind>
		</cfif>
		<cfset Variables.items = "">
		<cfoutput>
			<cfif URL.show NEQ "new" OR Snippets.New45>
				<cfset Variables.items = ListAppend(Variables.items, CurrentRow)>
			</cfif>
		</cfoutput>
		<cfif ListLen(Variables.items)>
		<H3>#Snippets.Category#</H3>
		<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=0 WIDTH="95%">
		<cfloop list="#Variables.items#" index="r">
			<TR VALIGN=TOP>
			<TD WIDTH="28%" NOWRAP><IMG SRC="/CFIDE/administrator/images/arrow.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
			<cfif Variables.local><A HREF="tagframe.cfm?tagname=#Snippets.Name[r]#" onClick="runExample('#Snippets.Name[r]#'); return false;"><B>#Snippets.Title[r]#</B></A><cfelse><B>#Snippets.Title[r]#</B></cfif>
			<FONT SIZE=1>(<A HREF="/CFDOCS/langref/#Snippets.Name[r]#.htm">ref</A>)</FONT>
			<cfif Snippets.New45[r]><FONT SIZE=1 COLOR="##CC0000"><B>4.5</B></FONT></cfif></TD>
			<TD><FONT SIZE=1>#HTMLEditFormat(Snippets.Summary[r])#</FONT></TD>
			</TR>
		</cfloop>
		</TABLE>
		</cfif>
	</cfif>
</cfoutput>
<HR NOSHADE SIZE=1>
<FONT SIZE=1 CLASS="copyright">Copyright &copy; 1995-1999, Gibson Mainframe Co. All rights reserved.</FONT>
</BODY>
</HTML>
