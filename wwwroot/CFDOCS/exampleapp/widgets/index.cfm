<!---
	widgets/index.cfm - the CFFORM "applet" controls.
	In 1999 CFGRID, CFTREE, CFSLIDER and CFTEXTINPUT were Java applets
	downloaded from /CFIDE/classes. KoldFusion draws HTML versions of them
	that submit the same form fields the applets did.
	  1. an editable CFGRID saved with CFGRIDUPDATE (gridaction.cfm)
	  2. a browse-mode CFGRID with links
	  3. CFTREE built from a query, and one built item by item
	  4. CFSLIDER and CFTEXTINPUT
--->
<CFPARAM NAME="URL.saved" DEFAULT="">

<CFQUERY NAME="GetVendors" DATASOURCE="#Request.DSN#">
	SELECT Vendor_ID, VendorName, Contact, Phone, City, Rating
	FROM Vendors
	ORDER BY VendorName
</CFQUERY>
<CFQUERY NAME="GetRooms" DATASOURCE="#Request.DSN#">
	SELECT Room_ID, RoomName, Location, Capacity FROM Rooms ORDER BY Capacity DESC
</CFQUERY>
<CFQUERY NAME="GetParkTree" DATASOURCE="#Request.DSN#">
	SELECT Region, State, ParkName FROM Parks
	WHERE Region IN ('Alaska', 'Northeast', 'Southeast')
	ORDER BY Region, State, ParkName
</CFQUERY>
<CFQUERY NAME="GetOrgChart" DATASOURCE="#Request.DSN#">
	SELECT d.Dept_ID, d.DeptName, e.Emp_ID, e.FirstName, e.LastName
	FROM Departments d, Employees e
	WHERE e.Dept_ID = d.Dept_ID
	ORDER BY d.DeptName, e.LastName
</CFQUERY>

<HTML>
<HEAD>
<TITLE>KoldFusion Form Controls: CFGRID and CFTREE</TITLE>
</HEAD>
<BODY BGCOLOR="#FFFFFF" LINK="#003399" VLINK="#663399">
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR><TD><FONT FACE="Arial, Helvetica" SIZE=5><B>CFGRID, CFTREE and Friends</B></FONT><BR>
<FONT FACE="Arial, Helvetica" SIZE=2>The Java applet form controls of KoldFusion 4.5, rendered in plain HTML.</FONT></TD>
<TD ALIGN=RIGHT><IMG SRC="/CFDOCS/exampleapp/images/ic_grid.gif" WIDTH=32 HEIGHT=32> <IMG SRC="/CFIDE/administrator/images/kf_logo_small.gif" WIDTH=120 HEIGHT=40 ALT="KoldFusion"></TD></TR>
</TABLE>
<HR SIZE=1 NOSHADE>

<!-- ======================================================= 1. edit grid -->
<FONT FACE="Arial, Helvetica" SIZE=3 COLOR="#003399"><B>1. An editable grid</B></FONT><BR>
<FONT FACE="Arial, Helvetica" SIZE=2>
Change any cell, tick <B>Del</B> to delete a row, or fill in the yellow row to add a vendor, then press
<B>Save Changes</B>. The action page needs just one tag, <TT>&lt;CFGRIDUPDATE&gt;</TT>, to write
everything back to the <TT>Vendors</TT> table in the <TT>cfexamples</TT> data source.
</FONT>
<CFIF URL.saved IS "yes"><P><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#006600"><B>Your changes were saved.</B></FONT></P></CFIF>
<CFFORM NAME="VendorForm" ACTION="gridaction.cfm" METHOD="POST">
<CFGRID NAME="VendorGrid" QUERY="GetVendors" SELECTMODE="Edit" INSERT="Yes" DELETE="Yes"
	WIDTH="560" HEIGHT="200" FONT="Arial" FONTSIZE="10" ROWHEADERS="No">
	<CFGRIDCOLUMN NAME="Vendor_ID" DISPLAY="No">
	<CFGRIDCOLUMN NAME="VendorName" HEADER="Vendor" WIDTH="160">
	<CFGRIDCOLUMN NAME="Contact" HEADER="Contact" WIDTH="110">
	<CFGRIDCOLUMN NAME="Phone" HEADER="Phone" WIDTH="80">
	<CFGRIDCOLUMN NAME="City" HEADER="City" WIDTH="90">
	<CFGRIDCOLUMN NAME="Rating" HEADER="Rating (1-5)" WIDTH="60" DATAALIGN="Center">
</CFGRID>
<BR>
<INPUT TYPE="Submit" VALUE="Save Changes"> <INPUT TYPE="Reset" VALUE="Undo">
</CFFORM>
<FONT FACE="Arial, Helvetica" SIZE=2>Current ratings:
<CFOUTPUT QUERY="GetVendors"><NOBR>#VendorName#
<CFLOOP INDEX="s" FROM="1" TO="5"><IMG SRC="/CFDOCS/exampleapp/images/<CFIF s LE Val(Rating)>star_on.gif<CFELSE>star_off.gif</CFIF>" WIDTH=12 HEIGHT=12></CFLOOP></NOBR>&nbsp;
</CFOUTPUT></FONT>
<P>

<!-- ======================================================= 2. browse grid -->
<FONT FACE="Arial, Helvetica" SIZE=3 COLOR="#003399"><B>2. A browse grid with links</B></FONT><BR>
<FONT FACE="Arial, Helvetica" SIZE=2>Each room name links to the GlobalCorp meeting room page; <TT>HREFKEY</TT>
makes the link carry the <TT>Room_ID</TT> as <TT>CFGRIDKEY</TT>.</FONT>
<CFFORM NAME="RoomForm" ACTION="index.cfm" METHOD="POST">
<CFGRID NAME="RoomGrid" QUERY="GetRooms" SELECTMODE="Browse" WIDTH="400"
	HREF="gridlink.cfm" HREFKEY="Room_ID">
	<CFGRIDCOLUMN NAME="RoomName" HEADER="Room">
	<CFGRIDCOLUMN NAME="Location" HEADER="Location">
	<CFGRIDCOLUMN NAME="Capacity" HEADER="Seats" DATAALIGN="Right">
</CFGRID>
</CFFORM>
<P>

<!-- ======================================================= 3. trees -->
<FONT FACE="Arial, Helvetica" SIZE=3 COLOR="#003399"><B>3. Trees</B></FONT><BR>
<FONT FACE="Arial, Helvetica" SIZE=2>The tree on the left is built from a query in one tag:
<TT>VALUE="Region,State,ParkName"</TT> makes one level per column. Click a park, then press
<B>Show Selection</B> to see the <TT>Form.ParkTree.node</TT> field the tree submits.
The org chart on the right is built item by item with <TT>CFTREEITEM PARENT=</TT>.</FONT>
<CFFORM NAME="TreeForm" ACTION="treeaction.cfm" METHOD="POST">
<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0><TR VALIGN=TOP>
<TD>
	<CFTREE NAME="ParkTree" WIDTH="260" HEIGHT="300" FONT="Arial">
		<CFTREEITEM VALUE="Region,State,ParkName" QUERY="GetParkTree" IMG="folder,folder,document">
	</CFTREE>
	<INPUT TYPE="Submit" VALUE="Show Selection">
</TD>
<TD>
	<CFTREE NAME="OrgChart" WIDTH="260" FONT="Arial">
		<CFTREEITEM VALUE="GC" DISPLAY="GlobalCorp Industries" IMG="computer" EXPAND="Yes">
		<CFOUTPUT QUERY="GetOrgChart" GROUP="Dept_ID">
			<CFTREEITEM VALUE="D#Dept_ID#" DISPLAY="#DeptName#" PARENT="GC" IMG="folder" EXPAND="No">
			<CFOUTPUT>
			<CFTREEITEM VALUE="E#Emp_ID#" DISPLAY="#FirstName# #LastName#" PARENT="D#Dept_ID#" IMG="document"
				HREF="/CFDOCS/exampleapp/GlobalCorp/directory/detail.cfm?Emp_ID=#Emp_ID#">
			</CFOUTPUT>
		</CFOUTPUT>
	</CFTREE>
	<FONT FACE="Arial, Helvetica" SIZE=1>(Employee links go to the GlobalCorp intranet, which asks you to log in.)</FONT>
</TD>
</TR></TABLE>
</CFFORM>
<P>

<!-- ======================================================= 4. slider, textinput -->
<FONT FACE="Arial, Helvetica" SIZE=3 COLOR="#003399"><B>4. CFSLIDER and CFTEXTINPUT</B></FONT><BR>
<CFFORM NAME="MiscForm" ACTION="treeaction.cfm" METHOD="POST">
<TABLE BORDER=0 CELLPADDING=4><TR>
<TD><FONT FACE="Arial, Helvetica" SIZE=2>How many widgets do you own?</FONT></TD>
<TD><CFSLIDER NAME="WidgetCount" RANGE="0,20" SCALE="1" VALUE="3" LABEL="Widgets:" WIDTH="200"></TD></TR>
<TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>Favorite park:</FONT></TD>
<TD><CFTEXTINPUT NAME="FavoritePark" VALUE="Yosemite" SIZE="25" FONT="Arial" BGCOLOR="##FFFFCC" REQUIRED="Yes" MESSAGE="Please name a park."></TD></TR>
<TR><TD></TD><TD><INPUT TYPE="Submit" VALUE="Send"></TD></TR>
</TABLE>
</CFFORM>

<HR SIZE=1 NOSHADE>
<FONT FACE="Arial, Helvetica" SIZE=1 COLOR="#666666">
<A HREF="javascript:void(window.open('/CFDOCS/exampleapp/sourcewindow.cfm?file=widgets/index.cfm','cfsource','width=680,height=500,scrollbars=yes,resizable=yes'))">View the source of this page</A> &middot;
<A HREF="javascript:void(window.open('/CFDOCS/exampleapp/sourcewindow.cfm?file=widgets/gridaction.cfm','cfsource','width=680,height=500,scrollbars=yes,resizable=yes'))">View gridaction.cfm</A> &middot;
<A HREF="/CFDOCS/examplehome.cfm">Example Applications</A>
</FONT>
</BODY>
</HTML>
