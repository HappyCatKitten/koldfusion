<!--- Header frame of the example window --->
<cfinclude template="_validate.cfm">
<HTML>
<HEAD><TITLE>Example</TITLE>
<LINK REL="stylesheet" TYPE="text/css" HREF="/CFDOCS/kfdocs.css">
<STYLE TYPE="text/css"><!-- A:link, A:visited { color: #FFFFCC; } A:hover { color: #FF9900; } --></STYLE>
<SCRIPT LANGUAGE="JavaScript">
<!--
function showRef(url) {
	if (top.opener && !top.opener.closed) { top.opener.location.href = url; top.opener.focus(); }
	else window.open(url, 'kfdocs');
}
//-->
</SCRIPT>
</HEAD>
<BODY BGCOLOR="#003399" TEXT="#FFFFFF" LINK="#FFFFCC" VLINK="#FFFFCC" ALINK="#FF9900" STYLE="background-color:#003399; margin-left:8px">
<cfif Variables.snipRow>
<cfoutput>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR VALIGN=TOP>
	<TD><FONT FACE="Verdana, Arial, Helvetica" SIZE=3 COLOR="##FFFFFF"><B>#snipTitle#</B></FONT>
	<FONT FACE="Verdana, Arial, Helvetica" SIZE=1 COLOR="##CCCCFF">&nbsp;#snipKind# &middot; #snipCategory#</FONT><BR>
	<FONT FACE="Verdana, Arial, Helvetica" SIZE=1 COLOR="##FFFFFF">#HTMLEditFormat(snipSummary)#</FONT></TD>
	<TD ALIGN=RIGHT NOWRAP><FONT FACE="Verdana, Arial, Helvetica" SIZE=1>
	<A HREF="javascript:showRef('/CFDOCS/langref/#tagname#.htm')">Reference page</A> |
	<A HREF="runexample.cfm?tagname=#tagname#" TARGET="runexample">Run again</A> |
	<A HREF="index.cfm" TARGET="_top">All examples</A> |
	<A HREF="javascript:top.close()">Close</A></FONT></TD>
</TR>
</TABLE>
</cfoutput>
</cfif>
</BODY>
</HTML>
