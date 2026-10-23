<!--- Common header for the hand-written documentation pages (the generated ones come from tools/mkdocs.py).
      Set Variables.pageTitle (and optionally bookTitle, prevURL, nextURL, upURL, headExtra) before including. --->
<cfparam name="Variables.pageTitle" default="KoldFusion Documentation">
<cfparam name="Variables.bookTitle" default="KoldFusion Documentation">
<cfparam name="Variables.prevURL" default="">
<cfparam name="Variables.nextURL" default="">
<cfparam name="Variables.upURL" default="/CFDOCS/dochome.cfm">
<cfparam name="Variables.headExtra" default="">
<cfset Variables.docNav = "">
<cfloop list="prev=doc_back=Previous page,up=doc_up=Up one level,next=doc_next=Next page,home=doc_home=Documentation home,index=doc_index=CFML Language Reference" index="Variables.navItem">
	<cfset Variables.navKey = ListGetAt(Variables.navItem, 1, "=")>
	<cfset Variables.navImg = ListGetAt(Variables.navItem, 2, "=")>
	<cfset Variables.navAlt = ListGetAt(Variables.navItem, 3, "=")>
	<cfif Variables.navKey EQ "home"><cfset Variables.navURL = "/CFDOCS/dochome.cfm">
	<cfelseif Variables.navKey EQ "index"><cfset Variables.navURL = "/CFDOCS/langref/index.htm">
	<cfelse><cfset Variables.navURL = Variables[Variables.navKey & "URL"]></cfif>
	<cfif Len(Variables.navURL)>
		<cfset Variables.docNav = Variables.docNav & "<TD><A HREF=""#Variables.navURL#""><IMG SRC=""/CFDOCS/images/#Variables.navImg#.gif"" WIDTH=16 HEIGHT=16 BORDER=0 ALT=""#Variables.navAlt#""></A></TD>">
	<cfelse>
		<cfset Variables.docNav = Variables.docNav & "<TD><IMG SRC=""/CFDOCS/images/#Variables.navImg#_off.gif"" WIDTH=16 HEIGHT=16 BORDER=0 ALT=""""></TD>">
	</cfif>
</cfloop>
<cfset Variables.docNav = "<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=2><TR>" & Variables.docNav & "</TR></TABLE>">
<cfoutput>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<HTML>
<HEAD>
<TITLE>#Variables.pageTitle#</TITLE>
<LINK REL="stylesheet" TYPE="text/css" HREF="/CFDOCS/kfdocs.css">
#Variables.headExtra#
</HEAD>
<BODY BGCOLOR="##FFFFF0" TEXT="##000000" LINK="##0000CC" VLINK="##663399" ALINK="##CC0000">
#Variables.docNav#
<FONT SIZE=1 CLASS="booktitle">#Variables.bookTitle#</FONT>
<HR NOSHADE SIZE=1>
</cfoutput>
