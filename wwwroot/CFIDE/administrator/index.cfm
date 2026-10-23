<HTML>
<HEAD>
<TITLE>KoldFusion Administrator</TITLE>
</HEAD>
<cfparam name="URL.page" default="server/settings.cfm">
<cfoutput>
<FRAMESET COLS="175,*" FRAMEBORDER=1 BORDER=2>
	<FRAME SRC="navigation.cfm" NAME="nav" SCROLLING="AUTO" MARGINWIDTH=0 MARGINHEIGHT=0>
	<FRAME SRC="#HTMLEditFormat(URL.page)#" NAME="main" SCROLLING="AUTO">
	<NOFRAMES>
	<BODY>The KoldFusion Administrator requires an HTML 3.0 browser that supports frames,
	such as Netscape Navigator 2.0 or Microsoft Internet Explorer 3.0 (or later).</BODY>
	</NOFRAMES>
</FRAMESET>
</cfoutput>
</HTML>
