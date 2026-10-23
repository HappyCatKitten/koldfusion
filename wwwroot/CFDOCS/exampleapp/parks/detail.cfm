<!---
	parks/detail.cfm - step 3: one park.
	The list's criteria and StartRow ride along in the URL so
	"Back to the list" returns to the same page of results.
--->
<CFPARAM NAME="URL.Park_ID" DEFAULT="0">
<CFPARAM NAME="URL.StartRow" DEFAULT="1">
<CFQUERY NAME="GetPark" DATASOURCE="#Request.DSN#">
	SELECT * FROM Parks WHERE Park_ID = #Val(URL.Park_ID)#
</CFQUERY>
<CFIF GetPark.RecordCount EQ 0>
	<CFLOCATION URL="index.cfm" ADDTOKEN="No">
</CFIF>
<CFQUERY NAME="Neighbors" DATASOURCE="#Request.DSN#">
	SELECT Park_ID, ParkName, ParkType FROM Parks
	WHERE State = '#GetPark.State#' AND Park_ID <> #GetPark.Park_ID#
	ORDER BY ParkName
</CFQUERY>

<CFSET Pos = ListFindNoCase(Request.StateCodes, GetPark.State)>
<CFIF Pos><CFSET StateName = ListGetAt(Request.StateNames, Pos)><CFELSE><CFSET StateName = GetPark.State></CFIF>
<!--- rebuild the link back to the list the visitor came from --->
<CFSET BackLink = "parklist.cfm?StartRow=#Val(URL.StartRow)#">
<CFLOOP LIST="State,Region,ParkName" INDEX="field">
	<CFIF IsDefined("URL.#field#")>
		<CFSET BackLink = BackLink & "&#field#=" & URLEncodedFormat(URL[field])>
	</CFIF>
</CFLOOP>
<CFSET PageTitle = GetPark.ParkName & " " & GetPark.ParkType>

<CFINCLUDE TEMPLATE="header.cfm">

<CFOUTPUT QUERY="GetPark">
<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0>
<TR VALIGN=TOP><TD ROWSPAN=5><IMG SRC="/CFDOCS/exampleapp/images/ic_parks.gif" WIDTH=32 HEIGHT=32></TD>
	<TD><FONT FACE="Verdana, Arial, Helvetica" SIZE=2><B>Type:</B></FONT></TD><TD><FONT FACE="Verdana, Arial, Helvetica" SIZE=2>#ParkType#</FONT></TD></TR>
<TR><TD><FONT FACE="Verdana, Arial, Helvetica" SIZE=2><B>State:</B></FONT></TD><TD><FONT FACE="Verdana, Arial, Helvetica" SIZE=2><A HREF="parklist.cfm?State=#State#">#StateName#</A></FONT></TD></TR>
<TR><TD><FONT FACE="Verdana, Arial, Helvetica" SIZE=2><B>Nearest town:</B></FONT></TD><TD><FONT FACE="Verdana, Arial, Helvetica" SIZE=2>#City#</FONT></TD></TR>
<TR><TD><FONT FACE="Verdana, Arial, Helvetica" SIZE=2><B>Region:</B></FONT></TD><TD><FONT FACE="Verdana, Arial, Helvetica" SIZE=2><A HREF="parklist.cfm?Region=#URLEncodedFormat(Region)#">#Region#</A></FONT></TD></TR>
</TABLE>
<BLOCKQUOTE><I>#Highlights#</I></BLOCKQUOTE>
</CFOUTPUT>

<CFIF Neighbors.RecordCount>
	<CFOUTPUT><P><B>Also in #StateName#:</B><BR></CFOUTPUT>
	<CFOUTPUT QUERY="Neighbors"><A HREF="detail.cfm?Park_ID=#Park_ID#&State=#GetPark.State#">#ParkName#</A> <FONT SIZE=1>(#ParkType#)</FONT><BR></CFOUTPUT>
</CFIF>
<CFOUTPUT><P><A HREF="#BackLink#">&lt;&lt; Back to the list</A></P></CFOUTPUT>

<CFINCLUDE TEMPLATE="footer.cfm">
