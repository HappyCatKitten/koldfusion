<!---
	footer.cfm - closes the layout opened by header.cfm and offers a
	"view source" link for the page being displayed.
--->
<CFSET ThisFile = ReplaceNoCase(CGI.SCRIPT_NAME, "/CFDOCS/exampleapp/", "")>
<CFOUTPUT>
<BR><BR>
</FONT>
</TD>
<TD WIDTH=16><IMG SRC="/CFIDE/administrator/images/spacer.gif" WIDTH=16 HEIGHT=1></TD>
</TR>
</TABLE>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=4 CELLSPACING=0>
<TR><TD BGCOLOR="##FFCC00"><IMG SRC="/CFIDE/administrator/images/spacer.gif" WIDTH=1 HEIGHT=1></TD></TR>
<TR>
	<TD ALIGN=CENTER>
	<FONT FACE="#Request.Font#" SIZE=1 COLOR="##666666">
	<A HREF="#Request.Root#/index.cfm">What's New</A> |
	<A HREF="#Request.Root#/directory/index.cfm">Directory</A> |
	<A HREF="#Request.Root#/forum/index.cfm">Forum</A> |
	<A HREF="#Request.Root#/catalog/index.cfm">Catalog</A> |
	<A HREF="#Request.Root#/scheduler/index.cfm">Meeting Rooms</A> |
	<A HREF="javascript:viewSource('#ThisFile#')">View source of this page</A><BR>
	Copyright &copy; 1999 GlobalCorp Industries (a fictional company). For internal use only.<BR>
	A KoldFusion example application.
	</FONT>
	</TD>
</TR>
</TABLE>
</BODY>
</HTML>
</CFOUTPUT>
