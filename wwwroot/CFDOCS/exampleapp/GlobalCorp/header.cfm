<!---
	header.cfm - common page top for the GlobalCorp intranet.
	Set these before including:
	  PageTitle  - shown in the title bar and as the page heading
	  Section    - home | directory | forum | catalog | scheduler (highlights the nav)
--->
<CFPARAM NAME="PageTitle" DEFAULT="">
<CFPARAM NAME="Section" DEFAULT="home">
<CFSET NavItems = "home,directory,forum,catalog,scheduler">
<CFSET NavLabels = "What's New,Directory,Forum,Company Store,Meeting Rooms">
<CFSET NavLinks = "index.cfm,directory/index.cfm,forum/index.cfm,catalog/index.cfm,scheduler/index.cfm">
<CFSET NavIcons = "ic_news.gif,ic_directory.gif,ic_forum.gif,ic_cart.gif,ic_calendar.gif">
<CFOUTPUT>
<HTML>
<HEAD>
<TITLE>GlobalCorp Intranet<CFIF Len(PageTitle)> - #PageTitle#</CFIF></TITLE>
<SCRIPT LANGUAGE="JavaScript">
<!--
function viewSource(f) {
	var w = window.open('/CFDOCS/exampleapp/sourcewindow.cfm?file=' + escape(f), 'cfsource',
		'width=680,height=500,scrollbars=yes,resizable=yes');
	w.focus();
}
//-->
</SCRIPT>
</HEAD>
<BODY BGCOLOR="##FFFFFF" LINK="##003399" VLINK="##663399" ALINK="##CC0000" TOPMARGIN=0 LEFTMARGIN=0 MARGINWIDTH=0 MARGINHEIGHT=0>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR>
	<TD WIDTH=310><A HREF="#Request.Root#/index.cfm"><IMG SRC="#Request.Images#/gc_logo.gif" WIDTH=300 HEIGHT=64 BORDER=0 HSPACE=6 VSPACE=4 ALT="GlobalCorp Intranet"></A></TD>
	<TD ALIGN=RIGHT VALIGN=BOTTOM>
		<FONT FACE="#Request.Font#" SIZE=1>
		Logged in as <B>#HTMLEditFormat(Request.FullName)#</B>
		(<A HREF="#Request.Root#/logout.cfm">log out</A>)<BR>
		#DateFormat(Now(), "dddd, mmmm d, yyyy")#
		</FONT>&nbsp;&nbsp;<BR><IMG SRC="/CFIDE/administrator/images/spacer.gif" WIDTH=1 HEIGHT=6>
	</TD>
</TR>
<TR><TD COLSPAN=2 BGCOLOR="##FFCC00"><IMG SRC="/CFIDE/administrator/images/spacer.gif" WIDTH=1 HEIGHT=4></TD></TR>
</TABLE>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR VALIGN=TOP>
<TD WIDTH=160 BGCOLOR="##003366">
	<TABLE WIDTH=160 BORDER=0 CELLPADDING=4 CELLSPACING=0>
	<TR><TD><IMG SRC="/CFIDE/administrator/images/spacer.gif" WIDTH=1 HEIGHT=4></TD></TR>
	<CFLOOP INDEX="i" FROM="1" TO="#ListLen(NavItems)#">
		<CFIF ListGetAt(NavItems, i) IS Section>
			<CFSET NavColor = "##336699">
		<CFELSE>
			<CFSET NavColor = "##003366">
		</CFIF>
		<TR><TD BGCOLOR="#NavColor#"><A HREF="#Request.Root#/#ListGetAt(NavLinks, i)#"><IMG SRC="#Request.Images#/#ListGetAt(NavIcons, i)#" WIDTH=32 HEIGHT=32 BORDER=0 ALIGN=ABSMIDDLE></A><FONT FACE="#Request.Font#" SIZE=2>&nbsp;<A HREF="#Request.Root#/#ListGetAt(NavLinks, i)#"><FONT COLOR="##FFFFFF"><B>#ListGetAt(NavLabels, i)#</B></FONT></A></FONT></TD></TR>
	</CFLOOP>
	<TR><TD><HR SIZE=1 NOSHADE COLOR="##FFCC00"></TD></TR>
	<TR><TD>
		<!--- cart summary custom tag, called by path because it lives in catalog/ --->
		<CFMODULE TEMPLATE="catalog/cartsummary.cfm">
	</TD></TR>
	<TR><TD><HR SIZE=1 NOSHADE COLOR="##FFCC00">
		<FONT FACE="#Request.Font#" SIZE=1 COLOR="##CCCCCC">
		Help Desk: #Request.HelpDesk#<BR><BR>
		<A HREF="/CFDOCS/examplehome.cfm"><FONT COLOR="##FFCC00">&lt;&lt; Example Applications</FONT></A>
		</FONT>
	</TD></TR>
	</TABLE>
</TD>
<TD WIDTH=16><IMG SRC="/CFIDE/administrator/images/spacer.gif" WIDTH=16 HEIGHT=1></TD>
<TD>
<FONT FACE="#Request.Font#" SIZE=2>
<CFIF Len(PageTitle)>
	<BR><FONT SIZE=4 COLOR="##003366"><B>#PageTitle#</B></FONT>
	<HR SIZE=1 NOSHADE>
</CFIF>
</CFOUTPUT>
