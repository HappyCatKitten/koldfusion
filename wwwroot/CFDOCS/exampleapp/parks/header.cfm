<!--- header.cfm - banner for the parks pages. Set PageTitle first. --->
<CFPARAM NAME="PageTitle" DEFAULT="">
<CFOUTPUT>
<HTML>
<HEAD><TITLE>National Parks Finder<CFIF Len(PageTitle)> - #PageTitle#</CFIF></TITLE></HEAD>
<BODY BGCOLOR="##FFFFF0" LINK="##006633" VLINK="##336633" ALINK="##CC6600">
<A HREF="index.cfm"><IMG SRC="/CFDOCS/exampleapp/images/parks_banner.gif" WIDTH=468 HEIGHT=60 BORDER=0 ALT="National Parks Finder"></A>
<TABLE WIDTH=600 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD>
<FONT FACE="Verdana, Arial, Helvetica" SIZE=2>
<CFIF Len(PageTitle)><H3><FONT COLOR="##006633">#PageTitle#</FONT></H3></CFIF>
</CFOUTPUT>
