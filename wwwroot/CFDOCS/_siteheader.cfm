<!--- Header for the "Gibson Online" resource pages (forums, support, training, devcenter, registration).
      Set Variables.pageTitle and Variables.section before including. --->
<cfparam name="Variables.pageTitle" default="Gibson Online">
<cfparam name="Variables.section" default="">
<cfset Variables.siteNav = "registration.cfm=Register KoldFusion,support.cfm=Technical Support,forums.cfm=Support Forums,training.cfm=Education &amp; Training,devcenter.cfm=Developer Center,dochome.cfm=Documentation,/CFDOCS/index.cfm=Server Home">
<cfoutput>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<HTML>
<HEAD>
<TITLE>Gibson Online - #Variables.pageTitle#</TITLE>
<LINK REL="stylesheet" TYPE="text/css" HREF="/CFDOCS/kfdocs.css">
</HEAD>
<BODY BGCOLOR="##FFFFFF" TEXT="##000000" LINK="##003399" VLINK="##669966" ALINK="##CC0000" LEFTMARGIN=0 TOPMARGIN=0 MARGINWIDTH=0 MARGINHEIGHT=0 STYLE="margin:0px; background-color:##FFFFFF">
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR BGCOLOR="##000066">
	<TD WIDTH=150 HEIGHT=40>&nbsp;<FONT FACE="Arial, Helvetica" SIZE=4 COLOR="##FFFFFF"><B><I>gibson</I></B></FONT><FONT FACE="Arial, Helvetica" SIZE=1 COLOR="##99CCFF"> online</FONT></TD>
	<TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=1 COLOR="##FFFFFF">
	<A HREF="/CFDOCS/index.cfm" STYLE="color:##FFFFFF">Home</A> &middot;
	<A HREF="/CFDOCS/dochome.cfm" STYLE="color:##FFFFFF">Products</A> &middot;
	<A HREF="/CFDOCS/support.cfm" STYLE="color:##FFFFFF">Support</A> &middot;
	<A HREF="/CFDOCS/devcenter.cfm" STYLE="color:##FFFFFF">Developers</A> &middot;
	<A HREF="/CFDOCS/training.cfm" STYLE="color:##FFFFFF">Training</A> &nbsp;</FONT></TD>
</TR>
<TR BGCOLOR="##99CC99"><TD COLSPAN=2 HEIGHT=4><IMG SRC="/CFIDE/administrator/images/spacer.gif" WIDTH=1 HEIGHT=4></TD></TR>
</TABLE>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR VALIGN=TOP>
	<TD WIDTH=150 BGCOLOR="##CCE6CC">
	<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0 WIDTH=150><TR><TD>
	<FONT FACE="Arial, Helvetica" SIZE=1>
	<BR>
	<cfloop list="#Variables.siteNav#" index="Variables.navItem">
		<cfif ListFirst(Variables.navItem, "=") EQ Variables.section>
			<IMG SRC="/CFIDE/administrator/images/arrow.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE><B>#ListLast(Variables.navItem, "=")#</B><BR>
		<cfelse>
			<IMG SRC="/CFIDE/administrator/images/spacer.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE><A HREF="#ListFirst(Variables.navItem, "=")#"><B>#ListLast(Variables.navItem, "=")#</B></A><BR>
		</cfif>
	</cfloop>
	<BR><BR>
	<CENTER>
	<IMG SRC="/images/netscape_now.gif" WIDTH=88 HEIGHT=31 ALT="Netscape Now!"><BR><BR>
	<IMG SRC="/images/powered_by_kf.gif" WIDTH=88 HEIGHT=31 ALT="Powered by KoldFusion"><BR><BR>
	<FONT SIZE=1 COLOR="##003399">Y2K compliant!<BR>Optimized for<BR>Netscape Navigator 4.7<BR>at 800x600</FONT>
	</CENTER>
	</FONT>
	</TD></TR></TABLE>
	</TD>
	<TD WIDTH=20>&nbsp;</TD>
	<TD>
	<BR>
	<FONT FACE="Arial, Helvetica" SIZE=5 COLOR="##000066"><B>#Variables.pageTitle#</B></FONT>
	<HR NOSHADE SIZE=1 COLOR="##003399">
</cfoutput>
