<!--- 
	/CFDOCS/snippets/tagframe.cfm?tagname=cfquery
	The "Example" window of the CFML Language Reference: a header frame,
	then the example's source above its live output.
--->
<cfinclude template="_validate.cfm">
<cfif NOT Variables.snipRow>
<HTML><HEAD><TITLE>KoldFusion Examples</TITLE><LINK REL="stylesheet" TYPE="text/css" HREF="/CFDOCS/kfdocs.css"></HEAD>
<BODY BGCOLOR="#FFFFF0">
<P><IMG SRC="/CFIDE/administrator/images/warn.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
<B>There is no example called "<cfoutput>#HTMLEditFormat(URL.tagname)#</cfoutput>".</B></P>
<P>Pick one from the <A HREF="index.cfm">Snippets Launcher</A> or the
<A HREF="/CFDOCS/langref/index.htm" TARGET="_blank">CFML Language Reference</A>.</P>
</BODY></HTML>
<cfabort>
</cfif>
<cfoutput>
<HTML>
<HEAD><TITLE>#snipTitle# - KoldFusion Example</TITLE></HEAD>
<FRAMESET ROWS="62,*" BORDER=0 FRAMEBORDER=0 FRAMESPACING=0>
	<FRAME NAME="header" SRC="exampleheader.cfm?tagname=#tagname#" SCROLLING="no" NORESIZE MARGINHEIGHT=4 MARGINWIDTH=8>
	<FRAMESET ROWS="45%,*" BORDER=4 FRAMEBORDER=1 FRAMESPACING=4>
		<FRAME NAME="viewexample" SRC="viewexample.cfm?tagname=#tagname#" SCROLLING="auto" MARGINHEIGHT=4 MARGINWIDTH=8>
		<FRAME NAME="runexample" SRC="runexample.cfm?tagname=#tagname#" SCROLLING="auto" MARGINHEIGHT=8 MARGINWIDTH=8>
	</FRAMESET>
	<NOFRAMES>
	<BODY>The examples use frames, which Navigator 2.0 and later handle nicely.
	<A HREF="viewexample.cfm?tagname=#tagname#">View the source</A> or
	<A HREF="#tagname#.cfm">run the example</A>.</BODY>
	</NOFRAMES>
</FRAMESET>
</HTML>
</cfoutput>
