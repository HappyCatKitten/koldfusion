<!--- ch6_header.cfm: shared page header. Set Request.PageTitle before including it. --->
<CFPARAM NAME="Request.PageTitle" DEFAULT="Developing with KoldFusion">
<HTML>
<HEAD><TITLE><CFOUTPUT>#Request.PageTitle#</CFOUTPUT></TITLE></HEAD>
<BODY BGCOLOR="#FFFFFF">
<TABLE WIDTH="100%" BORDER="0" CELLPADDING="4" CELLSPACING="0">
<TR><TD BGCOLOR="#003399"><FONT FACE="Arial, Helvetica" COLOR="#FFFFFF" SIZE="4">
<B><CFOUTPUT>#Request.PageTitle#</CFOUTPUT></B></FONT></TD></TR>
</TABLE>
<FONT FACE="Arial, Helvetica" SIZE="2">
