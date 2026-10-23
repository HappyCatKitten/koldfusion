<!--- Cool Stuff You Can Do With KoldFusion --->
<cfset quotes = "Content is king.|Information wants to be free.|The network is the computer.|On the Internet, nobody knows you're a dog.|Push technology is the future of the Web.|Y2K: we fixed it, you're welcome.|Bandwidth is the new real estate.|Portals! Portals everywhere!">
<cfset quote = ListGetAt(quotes, RandRange(1, ListLen(quotes, "|")), "|")>
<cfset y2k = CreateDateTime(2000, 1, 1, 0, 0, 0)>
<cfset sinceY2K = DateDiff("d", y2k, Now())>
<HTML>
<HEAD>
<TITLE>Cool Stuff You Can Do With KoldFusion</TITLE>
<META NAME="keywords" CONTENT="KoldFusion, CFML, cool, web, dynamic, database, push, portal, e-commerce, Y2K">
</HEAD>
<BODY BACKGROUND="/images/stars_bg.gif" BGCOLOR="#000000" TEXT="#FFFFFF" LINK="#FFFF00" VLINK="#FF9900" ALINK="#FF0000">
<CENTER>
<IMG SRC="/images/kf_welcome.gif" WIDTH=468 HEIGHT=60 ALT="Welcome to KoldFusion 4.5"><BR>
<FONT FACE="Arial, Helvetica" SIZE=6 COLOR="#66FF66"><B>Cool Stuff You Can Do</B></FONT><BR>
<IMG SRC="/images/fire.gif" WIDTH=120 HEIGHT=30><IMG SRC="/images/globe.gif" WIDTH=32 HEIGHT=32><IMG SRC="/images/fire.gif" WIDTH=120 HEIGHT=30><BR>
<FONT FACE="Arial, Helvetica" SIZE=2>
<MARQUEE WIDTH=468 BGCOLOR="#000066" SCROLLAMOUNT=4><cfoutput>*** #quote# *** Today is #DateFormat(Now(), "dddd, mmmm d, yyyy")# *** #NumberFormat(sinceY2K, ",")# days since the millennium bug failed to end civilisation ***</cfoutput></MARQUEE>
<P>You are visitor number
<cfoutput><cfloop index="i" from="1" to="#Len(Request.counter)#"><IMG SRC="/images/digit_#Mid(Request.counter, i, 1)#.gif" WIDTH=15 HEIGHT=20 ALIGN=ABSMIDDLE></cfloop></cfoutput>
since this server was installed!</P>
<IMG SRC="/images/rainbow_hr.gif" WIDTH=500 HEIGHT=6>
</FONT>
</CENTER>
<TABLE WIDTH="90%" ALIGN=CENTER BORDER=0 CELLPADDING=8><TR><TD>
<FONT FACE="Arial, Helvetica" SIZE=2>
<H3><IMG SRC="/images/bullet_red.gif" WIDTH=13 HEIGHT=13> Table of Contents</H3>
<UL>
<LI><A HREF="#server">Your server, by the numbers</A>
<LI><A HREF="#dice">Roll the dice (a CFX tag written in C)</A>
<LI><A HREF="guestbook.cfm">Sign the Guestbook</A> <IMG SRC="/images/new.gif" WIDTH=44 HEIGHT=22 ALIGN=ABSMIDDLE>
<LI><A HREF="search.cfm">Search this site with Verity</A>
<LI><A HREF="wddx.cfm">WDDX: ship a query to JavaScript</A>
<LI><A HREF="crypto.cfm">Encryption playground (1999-grade!)</A>
<LI><A HREF="fetch.cfm">CFHTTP: fetch a web page</A>
<LI><A HREF="widgets.cfm">Applet controls: CFGRID, CFTREE, CFSLIDER</A>
<LI><A HREF="phonebook.cfm">Employee Phone Directory (CFLDAP + the Gibson Directory Server)</A> <IMG SRC="/images/new.gif" WIDTH=44 HEIGHT=22 ALIGN=ABSMIDDLE>
<LI><A HREF="#gifs">The Animated GIF Hall of Fame</A>
</UL>

<A NAME="server"></A>
<H3><IMG SRC="/images/bullet_blue.gif" WIDTH=13 HEIGHT=13> Your server, by the numbers</H3>
<cfx_sysinfo name="sys">
<cfset metrics = GetMetricData("perf_monitor")>
<TABLE BORDER=1 CELLPADDING=4 CELLSPACING=0 BGCOLOR="#000066">
<cfoutput>
<TR><TD><FONT FACE="Arial" SIZE=2>Product</FONT></TD><TD><FONT FACE="Arial" SIZE=2>#Server.ColdFusion.ProductName# #Server.ColdFusion.ProductVersion# (#Server.ColdFusion.ProductLevel#)</FONT></TD></TR>
<TR><TD><FONT FACE="Arial" SIZE=2>Pages served</FONT></TD><TD><FONT FACE="Arial" SIZE=2>#NumberFormat(metrics.PageHits, ",")# (#metrics.ReqRunning# running right now)</FONT></TD></TR>
</cfoutput>
<cfoutput query="sys">
<TR><TD><FONT FACE="Arial" SIZE=2>#Item#</FONT></TD><TD><FONT FACE="Arial" SIZE=2>#Value#</FONT></TD></TR>
</cfoutput>
</TABLE>

<A NAME="dice"></A>
<H3><IMG SRC="/images/bullet_blue.gif" WIDTH=13 HEIGHT=13> Roll the dice</H3>
<P>Three six-sided dice, rolled by <TT>CFX_DICE</TT>, a CFX tag compiled from C and loaded with <TT>dlopen()</TT>:
<FONT SIZE=4 COLOR="#FFFF00"><B><cfx_dice rolls="3" sides="6" variable="total"></B></FONT>
<cfif total GTE 15><BLINK><FONT COLOR="#FF0000"><B>JACKPOT!</B></FONT></BLINK></cfif>
<A HREF="index.cfm#dice">Roll again</A></P>

<A NAME="gifs"></A>
<H3><IMG SRC="/images/bullet_blue.gif" WIDTH=13 HEIGHT=13> The Animated GIF Hall of Fame</H3>
<CENTER>
<IMG SRC="/images/construction.gif" WIDTH=140 HEIGHT=50 ALT="Under construction">
<IMG SRC="/images/email.gif" WIDTH=40 HEIGHT=30 ALT="Email me!">
<IMG SRC="/images/mailbox.gif" WIDTH=32 HEIGHT=32 ALT="You've got mail">
<IMG SRC="/images/globe.gif" WIDTH=32 HEIGHT=32 ALT="The World Wide Web">
<IMG SRC="/images/new.gif" WIDTH=44 HEIGHT=22 ALT="New!"><BR><BR>
<IMG SRC="/images/webring.gif" WIDTH=300 HEIGHT=40 ALT="KoldFusion WebRing"><BR><BR>
<A HREF="/"><IMG SRC="/images/powered_by_kf.gif" WIDTH=88 HEIGHT=31 BORDER=0></A>
<IMG SRC="/images/gibson_88x31.gif" WIDTH=88 HEIGHT=31>
<IMG SRC="/images/netscape_now.gif" WIDTH=88 HEIGHT=31>
<IMG SRC="/images/ie_parody.gif" WIDTH=88 HEIGHT=31>
</CENTER>
<P ALIGN=CENTER><FONT SIZE=1>This page is best viewed at 800x600 in 256 colors. Last updated <cfoutput>#DateFormat(Now(), "mm/dd/yy")#</cfoutput>.
<A HREF="mailto:webmaster@localhost"><IMG SRC="/images/email.gif" WIDTH=40 HEIGHT=30 BORDER=0 ALIGN=ABSMIDDLE></A></FONT></P>
</FONT>
</TD></TR></TABLE>
</BODY>
</HTML>
