<!---
	examplehome.cfm - the Example Applications hub, linked from the welcome page.
	Each sample has a "View Source" link that opens exampleapp/sourcewindow.cfm.
--->
<CFSET Apps = ArrayNew(1)>

<CFSET App = StructNew()>
<CFSET App.Name = "GlobalCorp Intranet">
<CFSET App.Icon = "/CFDOCS/exampleapp/images/gc_globe.gif">
<CFSET App.URL = "/CFDOCS/exampleapp/GlobalCorp/index.cfm">
<CFSET App.Source = "GlobalCorp/Application.cfm">
<CFSET App.DSN = "cfexamples">
<CFSET App.Blurb = "A complete company intranet for the fictional GlobalCorp Industries. Log in (sample accounts are listed on the login page) and try the five modules: a What's New page with a hit counter and a stock ticker fetched with CFHTTP, an employee directory you can browse, search and edit, a threaded discussion forum, a company store with Verity search, a shopping cart and e-mailed order confirmations, and a meeting room scheduler that refuses double bookings.">
<CFSET App.Tags = "CFAPPLICATION, Session and Application variables, CFLOCK, CFOUTPUT GROUP, CFFORM/CFINPUT/CFSELECT, CFINCLUDE, CFMODULE, custom tags, CFHTTP, CFCOLLECTION/CFINDEX/CFSEARCH, CFTRANSACTION, CFMAIL, CFQUERYPARAM, CFLOCATION">
<CFSET App.Parts = "What's New=GlobalCorp/index.cfm,Employee Directory=GlobalCorp/directory/index.cfm,Discussion Forum=GlobalCorp/forum/index.cfm,Product Catalog=GlobalCorp/catalog/index.cfm,Meeting Rooms=GlobalCorp/scheduler/index.cfm">
<CFSET ArrayAppend(Apps, App)>

<CFSET App = StructNew()>
<CFSET App.Name = "Human Resources Employee Manager">
<CFSET App.Icon = "/CFDOCS/exampleapp/images/ic_people.gif">
<CFSET App.URL = "/CFDOCS/exampleapp/HRApp/index.cfm">
<CFSET App.Source = "HRApp/InsertForm.cfm">
<CFSET App.DSN = "CompanyInfo">
<CFSET App.Blurb = "The classic list / search / add / update application. Every form field is named after a database column, so adding and changing employees takes one CFINSERT or CFUPDATE tag. Hidden _required, _date and _float fields check the input on the server even when the browser has JavaScript turned off.">
<CFSET App.Tags = "CFINSERT, CFUPDATE, CFSELECT, server-side form validation, CFSWITCH, dynamic WHERE clauses">
<CFSET App.Parts = "">
<CFSET ArrayAppend(Apps, App)>

<CFSET App = StructNew()>
<CFSET App.Name = "National Parks Finder">
<CFSET App.Icon = "/CFDOCS/exampleapp/images/ic_parks.gif">
<CFSET App.URL = "/CFDOCS/exampleapp/parks/index.cfm">
<CFSET App.Source = "parks/parklist.cfm">
<CFSET App.DSN = "cfexamples">
<CFSET App.Blurb = "A three-level drill-down: choose a state, page through its parks five at a time with Previous and Next buttons, then read about one park. Shows how CFOUTPUT STARTROW and MAXROWS turn one query into as many pages as you need.">
<CFSET App.Tags = "CFOUTPUT STARTROW/MAXROWS, GROUP BY and COUNT, URL parameters, LIKE searches">
<CFSET App.Parts = "">
<CFSET ArrayAppend(Apps, App)>

<CFSET App = StructNew()>
<CFSET App.Name = "CFGRID and CFTREE Controls">
<CFSET App.Icon = "/CFDOCS/exampleapp/images/ic_grid.gif">
<CFSET App.URL = "/CFDOCS/exampleapp/widgets/index.cfm">
<CFSET App.Source = "widgets/index.cfm">
<CFSET App.DSN = "cfexamples">
<CFSET App.Blurb = "The CFFORM applet controls: an editable grid that saves its changes with a single CFGRIDUPDATE, a browse grid with links, trees built from a query or item by item, and CFSLIDER and CFTEXTINPUT. KoldFusion draws them in HTML, so no Java plug-in is needed.">
<CFSET App.Tags = "CFGRID, CFGRIDCOLUMN, CFGRIDUPDATE, CFTREE, CFTREEITEM, CFSLIDER, CFTEXTINPUT">
<CFSET App.Parts = "">
<CFSET ArrayAppend(Apps, App)>

<HTML>
<HEAD>
<TITLE>KoldFusion Example Applications</TITLE>
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
<BODY BGCOLOR="#99CC99" BACKGROUND="/images/bgblue.gif" LINK="#003399" VLINK="#669966" ALINK="#669966">
<BR>
<CENTER>
<TABLE WIDTH=640 BORDER=0 CELLPADDING=1 CELLSPACING=0 BGCOLOR="#000066"><TR><TD>
<TABLE WIDTH=638 BORDER=0 CELLPADDING=0 CELLSPACING=0 BGCOLOR="#FFFFFF">
<TR>
	<TD WIDTH=30>&nbsp;</TD>
	<TD VALIGN=TOP>
		<BR>
		<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0><TR>
		<TD><FONT FACE="Arial, Helvetica" SIZE=5 COLOR="#000066"><B>Example Applications</B></FONT></TD>
		<TD ALIGN=RIGHT><A HREF="/CFDOCS/index.cfm"><IMG SRC="/CFIDE/administrator/images/kf_logo_small.gif" WIDTH=120 HEIGHT=40 BORDER=0 ALT="KoldFusion"></A></TD>
		</TR></TABLE>
		<HR NOSHADE SIZE=1 COLOR="#000066">
		<FONT FACE="Arial, Helvetica" SIZE=2>
		<P>These sample applications show how the pieces of CFML fit together in real Web
		applications. Run them, then open the source of any page to see how it works:
		every template is commented. Feel free to copy them as a starting point for your own work.</P>
		</FONT>

		<CFLOOP INDEX="i" FROM="1" TO="#ArrayLen(Apps)#">
		<CFSET App = Apps[i]>
		<CFOUTPUT>
		<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>
		<TR><TD COLSPAN=2 BGCOLOR="##003399"><IMG SRC="/CFIDE/administrator/images/spacer.gif" WIDTH=1 HEIGHT=2></TD></TR>
		<TR VALIGN=TOP>
			<TD WIDTH=44><BR><A HREF="#App.URL#"><IMG SRC="#App.Icon#" WIDTH=32 HEIGHT=32 BORDER=0 ALT="#App.Name#"></A></TD>
			<TD><BR><FONT FACE="Arial, Helvetica" SIZE=3><A HREF="#App.URL#"><B>#App.Name#</B></A></FONT>
			<FONT FACE="Arial, Helvetica" SIZE=1 COLOR="##666666">&nbsp; data source: <TT>#App.DSN#</TT></FONT><BR>
			<FONT FACE="Arial, Helvetica" SIZE=2>#App.Blurb#</FONT><BR>
			<CFIF Len(App.Parts)>
				<FONT FACE="Arial, Helvetica" SIZE=2>
				<CFLOOP LIST="#App.Parts#" INDEX="Part">
					<IMG SRC="/images/bullet_blue.gif" WIDTH=13 HEIGHT=13 ALIGN=ABSMIDDLE>
					<A HREF="/CFDOCS/exampleapp/#ListLast(Part, '=')#">#ListFirst(Part, '=')#</A>&nbsp;
				</CFLOOP>
				</FONT><BR>
			</CFIF>
			<FONT FACE="Arial, Helvetica" SIZE=1><B>Demonstrates:</B> #App.Tags#</FONT><BR>
			<FONT FACE="Arial, Helvetica" SIZE=2>
			<A HREF="#App.URL#"><B>Run the example</B></A> &nbsp;|&nbsp;
			<A HREF="javascript:viewSource('#App.Source#')">View Source</A>
			</FONT><BR><BR>
			</TD>
		</TR>
		</TABLE>
		</CFOUTPUT>
		</CFLOOP>

		<TABLE WIDTH="100%" BORDER=0 CELLPADDING=6 CELLSPACING=0>
		<TR><TD BGCOLOR="#FFFFCC"><FONT FACE="Arial, Helvetica" SIZE=1>
		<IMG SRC="/CFIDE/administrator/images/warn.gif" WIDTH=16 HEIGHT=16 ALIGN=LEFT HSPACE=4>
		<B>Security note:</B> the example applications are for learning. They let visitors change
		data and read template source code, so do not install the <TT>/CFDOCS/</TT> directory on a
		production server. The examples use the <TT>cfexamples</TT> and <TT>CompanyInfo</TT> data sources;
		delete the <TT>kfroot/db/cfexamples</TT> or <TT>kfroot/db/CompanyInfo</TT> directory and restart
		the server to put the sample data back the way it was.
		</FONT></TD></TR>
		</TABLE>
		<BR>
	</TD>
	<TD WIDTH=30>&nbsp;</TD>
</TR>
<TR>
	<TD></TD>
	<TD><FONT FACE="Arial, Helvetica" SIZE=1 COLOR="#666666">
	<HR NOSHADE SIZE=1>
	<A HREF="/CFDOCS/index.cfm">KoldFusion Server Home</A> &middot;
	<A HREF="/CFDOCS/dochome.cfm">Product Documentation</A> &middot;
	<A HREF="/CFDOCS/snippets/index.cfm">Snippets</A> &middot;
	<A HREF="/CFIDE/administrator/index.cfm">Administrator</A><BR><BR>
	</FONT></TD>
	<TD></TD>
</TR>
</TABLE>
</TD></TR></TABLE>
<FONT FACE="Arial, Helvetica" SIZE=1 COLOR="#FFFFFF">Copyright 1995-2000, Gibson Mainframe Co. All rights reserved.
GlobalCorp Industries and everyone who works there are fictional.</FONT>
</CENTER>
</BODY>
</HTML>
