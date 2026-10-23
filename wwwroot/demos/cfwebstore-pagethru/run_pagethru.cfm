<!--- KoldFusion Demo Gallery companion (not part of CFWebstore).
      pagethru.cfm is a custom tag, so it needs a caller. This page builds a
      98-row query of 1990s web landmarks with QueryNew/QueryAddRow, calls
      <CF_PAGETHRU> exactly as CFWebstore's product listings do, and shows the
      current page. Request.ImagePath must exist because the tag's CFPARAM
      default refers to it even when IMAGEPATH is passed. --->
<cfset Request.ImagePath = "">
<cfparam name="URL.currentpage" default="1">
<cfif NOT IsNumeric(URL.currentpage) OR URL.currentpage LT 1><cfset URL.currentpage = 1></cfif>
<cfparam name="URL.style" default="text">

<cfset sites = "GeoCities,Tripod,Angelfire,Yahoo!,AltaVista,Excite,Lycos,HotBot,WebCrawler,Infoseek,Ask Jeeves,"
	& "Netscape Netcenter,Hotmail,Four11,Deja News,Slashdot,Suck.com,Feed,Word.com,Salon,The Onion,Ain't It Cool News,"
	& "Dancing Baby,Hamster Dance,Mahir,All Your Base,Zombo,Bert Is Evil,Exploding Whale,Space Jam,"
	& "Jennicam,eBay,Amazon.com,CDNow,Pets.com,Kozmo,Webvan,Boo.com,theGlobe.com,Xoom,"
	& "Winamp,ICQ,AIM,Napster,mIRC,RealPlayer,Shockwave,Macromedia Flash 4,Java Applets,ActiveX,"
	& "Netscape Navigator 4,Internet Explorer 5,Opera 3,Lynx,Mosaic,HotJava,Cello,NCSA httpd,Apache 1.3,IIS 4,"
	& "Allair KoldFusion 4.5,PHP/FI,Perl CGI,Matt's Script Archive,FrontPage 98,HomeSite 4,Dreamweaver 2,NetObjects Fusion,"
	& "WebTV,Prodigy,CompuServe,AOL Keyword,EarthLink,MindSpring,Juno,NetZero,BBS,Usenet,Gopher,Archie,Veronica,"
	& "Webring,Under Construction GIF,Hit Counter,Guestbook,Frames,Marquee,Blink,Animated GIF,Spacer GIF,"
	& "Best Viewed in 800x600,Y2K Bug,Push Technology,PointCast,VRML,Microsoft Bob,Clippy,Tamagotchi">
<cfset Landmarks = QueryNew("Rank,Site")>
<cfset rank = 0>
<cfloop list="#sites#" index="s">
	<cfset rank = rank + 1>
	<cfset QueryAddRow(Landmarks)>
	<cfset QuerySetCell(Landmarks, "Rank", rank)>
	<cfset QuerySetCell(Landmarks, "Site", s)>
</cfloop>

<cfif URL.style IS "images">
	<cfset imgpath = "/demos/cfwebstore-pagethru/">
<cfelse>
	<cfset imgpath = "NONE">
</cfif>

<cf_pagethru totalrecords="#Landmarks.RecordCount#"
	currentpage="#URL.currentpage#"
	templateurl="run_pagethru.cfm"
	addedpath="&style=#URL.style#"
	displaycount="10"
	pagegroup="5"
	imagepath="#imgpath#">

<html>
<head><title>CF_PAGETHRU demo</title>
<script language="JavaScript">
<!--
// the tag's links call dmim() (a Dreamweaver status-bar helper in CFWebstore)
function dmim(msg) { window.status = msg; document.returnValue = true; }
// -->
</script>
</head>
<body bgcolor="#FFFFFF">
<font face="Arial, Helvetica" size="2">
<h2>CF_PAGETHRU - Next/Prev record paging</h2>
<cfoutput>
<p>#Landmarks.RecordCount# records, 10 per page, page groups of 5.
Showing rows #pt_startrow# to #pt_endrow#. Status: #pt_errorcode# (#pt_errormsg#)</p>
<p><b>#pt_pagethru#</b></p>
</cfoutput>
<table border="1" cellpadding="3" cellspacing="0" width="400">
<tr bgcolor="#000080"><th><font color="#FFFFFF" face="Arial" size="2">#</font></th><th><font color="#FFFFFF" face="Arial" size="2">1990s web landmark</font></th></tr>
<cfoutput query="Landmarks" startrow="#pt_startrow#" maxrows="10">
<tr bgcolor="###IIf(CurrentRow MOD 2, DE('FFFFFF'), DE('EEEEFF'))#"><td align="right">#Rank#</td><td>#Site#</td></tr>
</cfoutput>
</table>
<cfoutput><p><b>#pt_pagethru#</b></p></cfoutput>
<p>Navigation style: <a href="run_pagethru.cfm?style=text">text links</a> |
<a href="run_pagethru.cfm?style=images">image buttons</a></p>
</font>
</body>
</html>
