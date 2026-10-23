<!---
	parks/index.cfm - step 1 of the drill-down: pick a state (or a region).
	Each state links to parklist.cfm, which pages through its parks;
	each park links to detail.cfm.
--->
<CFSET PageTitle = "">
<CFQUERY NAME="GetStates" DATASOURCE="#Request.DSN#">
	SELECT State, COUNT(*) AS NumParks
	FROM Parks
	GROUP BY State
	ORDER BY State
</CFQUERY>
<CFQUERY NAME="GetRegions" DATASOURCE="#Request.DSN#">
	SELECT Region, COUNT(*) AS NumParks FROM Parks GROUP BY Region ORDER BY Region
</CFQUERY>
<CFQUERY NAME="GetTotal" DATASOURCE="#Request.DSN#">
	SELECT COUNT(*) AS Total FROM Parks
</CFQUERY>

<CFINCLUDE TEMPLATE="header.cfm">

<CFOUTPUT>
<P>Find national parks, monuments and seashores in the United States. This sample holds
<B>#GetTotal.Total#</B> park units in <B>#GetStates.RecordCount#</B> states and territories.
Choose a state to begin.</P>
</CFOUTPUT>

<!--- three columns of states --->
<CFSET PerColumn = Ceiling(GetStates.RecordCount / 3)>
<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0 WIDTH="100%">
<TR VALIGN=TOP>
<TD>
<CFOUTPUT QUERY="GetStates">
	<CFSET Pos = ListFindNoCase(Request.StateCodes, State)>
	<CFIF Pos><CFSET StateName = ListGetAt(Request.StateNames, Pos)><CFELSE><CFSET StateName = State></CFIF>
	<IMG SRC="/images/bullet_blue.gif" WIDTH=13 HEIGHT=13 ALIGN=ABSMIDDLE>
	<FONT FACE="Verdana, Arial, Helvetica" SIZE=2><A HREF="parklist.cfm?State=#State#">#StateName#</A> <FONT SIZE=1 COLOR="##666666">(#NumParks#)</FONT></FONT><BR>
	<CFIF CurrentRow MOD PerColumn EQ 0 AND CurrentRow LT RecordCount></TD><TD></CFIF>
</CFOUTPUT>
</TD>
</TR>
</TABLE>

<CFOUTPUT>
<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0 BGCOLOR="##E8F0E0" WIDTH="100%">
<TR><TD>
	<FORM ACTION="parklist.cfm" METHOD="GET" STYLE="margin:0">
	<FONT FACE="Verdana, Arial, Helvetica" SIZE=2><B>Or browse by region:</B></FONT>
	<SELECT NAME="Region">
	<CFLOOP QUERY="GetRegions"><OPTION VALUE="#Region#">#Region# (#NumParks#)</CFLOOP>
	</SELECT>
	<INPUT TYPE="Submit" VALUE="Show Parks">
	</FORM>
</TD></TR>
<TR><TD>
	<FORM ACTION="parklist.cfm" METHOD="GET" STYLE="margin:0">
	<FONT FACE="Verdana, Arial, Helvetica" SIZE=2><B>Or search by name:</B></FONT>
	<INPUT TYPE="Text" NAME="ParkName" SIZE=20>
	<INPUT TYPE="Submit" VALUE="Find">
	&nbsp;<FONT FACE="Verdana, Arial, Helvetica" SIZE=1><A HREF="parklist.cfm">list every park</A></FONT>
	</FORM>
</TD></TR>
</TABLE>
</CFOUTPUT>

<CFINCLUDE TEMPLATE="footer.cfm">
