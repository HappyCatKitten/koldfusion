<!---
	parks/parklist.cfm - step 2: the parks in a state, region or name search,
	shown Request.PageSize at a time with "previous / next N" buttons.
	The query returns every match; CFOUTPUT STARTROW and MAXROWS show one page.
	  ?State=XX | ?Region=name | ?ParkName=text   (none = all parks)
	  &StartRow=n
--->
<CFPARAM NAME="URL.State" DEFAULT="">
<CFPARAM NAME="URL.Region" DEFAULT="">
<CFPARAM NAME="URL.ParkName" DEFAULT="">
<CFPARAM NAME="URL.StartRow" DEFAULT="1">
<CFIF NOT IsNumeric(URL.StartRow) OR URL.StartRow LT 1><CFSET URL.StartRow = 1></CFIF>
<CFSET URL.StartRow = Int(URL.StartRow)>

<CFQUERY NAME="GetParks" DATASOURCE="#Request.DSN#">
	SELECT Park_ID, ParkName, ParkType, City, State, Region
	FROM Parks
	WHERE 1 = 1
	<CFIF Len(URL.State)>
		AND State = '#UCase(Left(URL.State, 2))#'
	</CFIF>
	<CFIF Len(URL.Region)>
		AND Region = '#URL.Region#'
	</CFIF>
	<CFIF Len(Trim(URL.ParkName))>
		AND ParkName LIKE '%#Trim(URL.ParkName)#%'
	</CFIF>
	ORDER BY ParkName
</CFQUERY>

<!--- describe what we're showing, and remember it for the paging links --->
<CFIF Len(URL.State)>
	<CFSET Pos = ListFindNoCase(Request.StateCodes, URL.State)>
	<CFIF Pos><CFSET PageTitle = "Parks in " & ListGetAt(Request.StateNames, Pos)><CFELSE><CFSET PageTitle = "Parks in " & UCase(URL.State)></CFIF>
	<CFSET Criteria = "State=#URLEncodedFormat(URL.State)#">
<CFELSEIF Len(URL.Region)>
	<CFSET PageTitle = "Parks in the #URL.Region# Region">
	<CFSET Criteria = "Region=#URLEncodedFormat(URL.Region)#">
<CFELSEIF Len(Trim(URL.ParkName))>
	<CFSET PageTitle = "Parks Named Like '#Trim(URL.ParkName)#'">
	<CFSET Criteria = "ParkName=#URLEncodedFormat(Trim(URL.ParkName))#">
<CFELSE>
	<CFSET PageTitle = "All Parks">
	<CFSET Criteria = "">
</CFIF>

<CFSET EndRow = Min(URL.StartRow + Request.PageSize - 1, GetParks.RecordCount)>
<CFSET PrevStart = URL.StartRow - Request.PageSize>
<CFSET NextStart = URL.StartRow + Request.PageSize>

<CFINCLUDE TEMPLATE="header.cfm">

<CFIF GetParks.RecordCount EQ 0>
	<P>No parks matched. <A HREF="index.cfm">Try again</A>.</P>
<CFELSE>
	<CFOUTPUT><P>Showing parks <B>#URL.StartRow#-#EndRow#</B> of <B>#GetParks.RecordCount#</B>.</P></CFOUTPUT>
	<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%">
	<TR BGCOLOR="#006633">
		<TD><FONT FACE="Verdana, Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Park</B></FONT></TD>
		<TD><FONT FACE="Verdana, Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Type</B></FONT></TD>
		<TD><FONT FACE="Verdana, Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Near</B></FONT></TD>
	</TR>
	<CFOUTPUT QUERY="GetParks" STARTROW="#URL.StartRow#" MAXROWS="#Request.PageSize#">
	<TR BGCOLOR="###IIf(CurrentRow MOD 2, DE('FFFFFF'), DE('EEF4E8'))#">
		<TD><FONT FACE="Verdana, Arial, Helvetica" SIZE=2>#CurrentRow#. <A HREF="detail.cfm?Park_ID=#Park_ID#&#Criteria#&StartRow=#URL.StartRow#"><B>#ParkName#</B></A></FONT></TD>
		<TD><FONT FACE="Verdana, Arial, Helvetica" SIZE=1>#ParkType#</FONT></TD>
		<TD><FONT FACE="Verdana, Arial, Helvetica" SIZE=1>#City#, #State#</FONT></TD>
	</TR>
	</CFOUTPUT>
	</TABLE>

	<!--- the paging controls --->
	<CFOUTPUT>
	<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%"><TR>
	<TD>
		<CFIF PrevStart GE 1>
			<FORM ACTION="parklist.cfm?#Criteria#&StartRow=#PrevStart#" METHOD="POST" STYLE="margin:0"><INPUT TYPE="Submit" VALUE="&lt;&lt; Previous #Request.PageSize#"></FORM>
		</CFIF>
	</TD>
	<TD ALIGN=CENTER><FONT FACE="Verdana, Arial, Helvetica" SIZE=1>Page:
		<CFLOOP INDEX="p" FROM="1" TO="#Ceiling(GetParks.RecordCount / Request.PageSize)#">
			<CFSET PageStart = (p - 1) * Request.PageSize + 1>
			<CFIF PageStart EQ URL.StartRow><B>#p#</B><CFELSE><A HREF="parklist.cfm?#Criteria#&StartRow=#PageStart#">#p#</A></CFIF>
		</CFLOOP>
	</FONT></TD>
	<TD ALIGN=RIGHT>
		<CFIF NextStart LE GetParks.RecordCount>
			<CFSET NextCount = Min(Request.PageSize, GetParks.RecordCount - NextStart + 1)>
			<FORM ACTION="parklist.cfm?#Criteria#&StartRow=#NextStart#" METHOD="POST" STYLE="margin:0"><INPUT TYPE="Submit" VALUE="Next #NextCount# &gt;&gt;"></FORM>
		</CFIF>
	</TD>
	</TR></TABLE>
	</CFOUTPUT>
</CFIF>
<P><A HREF="index.cfm">&lt;&lt; Choose another state</A></P>

<CFINCLUDE TEMPLATE="footer.cfm">
