<!---
	scheduler/index.cfm - month-at-a-glance calendar of meeting room bookings
	  ?month=m&year=y   which month (default: this month)
	  ?Room_ID=n        only one room (default: all rooms)
	The grid is built with CreateDate, DayOfWeek and DaysInMonth:
	blank cells before the 1st, then one cell per day, seven to a row.
--->
<CFPARAM NAME="URL.month" DEFAULT="#Month(Now())#">
<CFPARAM NAME="URL.year" DEFAULT="#Year(Now())#">
<CFPARAM NAME="URL.Room_ID" DEFAULT="0">
<CFSET Section = "scheduler">

<!--- guard against hand-typed URLs --->
<CFIF NOT IsNumeric(URL.month) OR URL.month LT 1 OR URL.month GT 12><CFSET URL.month = Month(Now())></CFIF>
<CFIF NOT IsNumeric(URL.year) OR URL.year LT 1990 OR URL.year GT 2100><CFSET URL.year = Year(Now())></CFIF>

<CFSET FirstOfMonth = CreateDate(URL.year, URL.month, 1)>
<CFSET FirstOfNext = DateAdd("m", 1, FirstOfMonth)>
<CFSET FirstOfPrev = DateAdd("m", -1, FirstOfMonth)>
<CFSET NumDays = DaysInMonth(FirstOfMonth)>
<CFSET LeadingBlanks = DayOfWeek(FirstOfMonth) - 1>
<CFSET PageTitle = "Meeting Rooms: " & MonthAsString(URL.month) & " " & URL.year>

<CFQUERY NAME="GetRooms" DATASOURCE="#Request.DSN#">
	SELECT Room_ID, RoomName FROM Rooms ORDER BY RoomName
</CFQUERY>

<CFQUERY NAME="GetBookings" DATASOURCE="#Request.DSN#">
	SELECT b.Booking_ID, b.MeetingDate, b.StartTime, b.EndTime, b.Purpose, r.RoomName
	FROM Bookings b, Rooms r
	WHERE b.Room_ID = r.Room_ID
	  AND b.MeetingDate >= <CFQUERYPARAM CFSQLTYPE="CF_SQL_DATE" VALUE="#FirstOfMonth#">
	  AND b.MeetingDate < <CFQUERYPARAM CFSQLTYPE="CF_SQL_DATE" VALUE="#FirstOfNext#">
	<CFIF Val(URL.Room_ID)>
	  AND b.Room_ID = #Val(URL.Room_ID)#
	</CFIF>
	ORDER BY b.MeetingDate, b.StartTime
</CFQUERY>

<CFINCLUDE TEMPLATE="../header.cfm">

<CFOUTPUT>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0>
<TR>
<TD><FONT FACE="#Request.Font#" SIZE=2>
	<A HREF="index.cfm?month=#Month(FirstOfPrev)#&year=#Year(FirstOfPrev)#&Room_ID=#Val(URL.Room_ID)#">&lt;&lt; #MonthAsString(Month(FirstOfPrev))#</A> |
	<A HREF="index.cfm?Room_ID=#Val(URL.Room_ID)#">This month</A> |
	<A HREF="index.cfm?month=#Month(FirstOfNext)#&year=#Year(FirstOfNext)#&Room_ID=#Val(URL.Room_ID)#">#MonthAsString(Month(FirstOfNext))# &gt;&gt;</A>
</FONT></TD>
<TD ALIGN=RIGHT>
	<FORM ACTION="index.cfm" METHOD="GET" STYLE="margin:0">
	<INPUT TYPE="Hidden" NAME="month" VALUE="#URL.month#">
	<INPUT TYPE="Hidden" NAME="year" VALUE="#URL.year#">
	<SELECT NAME="Room_ID" onChange="this.form.submit()">
		<OPTION VALUE="0">All rooms
		<CFLOOP QUERY="GetRooms"><OPTION VALUE="#Room_ID#"<CFIF Room_ID EQ URL.Room_ID> SELECTED</CFIF>>#RoomName#</CFLOOP>
	</SELECT>
	<NOSCRIPT><INPUT TYPE="Submit" VALUE="Show"></NOSCRIPT>
	</FORM>
</TD>
</TR>
</TABLE>

<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0 BGCOLOR="##003366"><TR><TD>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=1>
<TR BGCOLOR="##003366">
<CFLOOP INDEX="dow" FROM="1" TO="7">
	<TD ALIGN=CENTER WIDTH="14%"><FONT FACE="#Request.Font#" SIZE=2 COLOR="##FFFFFF"><B>#DayOfWeekAsString(dow)#</B></FONT></TD>
</CFLOOP>
</TR>
<TR VALIGN=TOP>
<!--- empty cells before the first --->
<CFLOOP INDEX="b" FROM="1" TO="#LeadingBlanks#">
	<TD BGCOLOR="##DDDDDD">&nbsp;</TD>
</CFLOOP>
<CFLOOP INDEX="d" FROM="1" TO="#NumDays#">
	<CFSET ThisDate = CreateDate(URL.year, URL.month, d)>
	<CFSET Column = DayOfWeek(ThisDate)>
	<CFIF DateCompare(ThisDate, Now(), "d") EQ 0>
		<CFSET CellColor = "##FFFFCC">
	<CFELSEIF Column EQ 1 OR Column EQ 7>
		<CFSET CellColor = "##EEEEEE">
	<CFELSE>
		<CFSET CellColor = "##FFFFFF">
	</CFIF>
	<TD BGCOLOR="#CellColor#" HEIGHT=70>
		<FONT FACE="#Request.Font#" SIZE=2><A HREF="day.cfm?date=#URLEncodedFormat(DateFormat(ThisDate, 'mm/dd/yyyy'))#"><B>#d#</B></A></FONT><BR>
		<CFLOOP QUERY="GetBookings">
			<CFIF Day(MeetingDate) EQ d>
				<FONT FACE="#Request.Font#" SIZE=1>#TimeFormat(CreateTime(Int(StartTime / 100), StartTime MOD 100, 0), "h:mmt")#
				<A HREF="day.cfm?date=#URLEncodedFormat(DateFormat(ThisDate, 'mm/dd/yyyy'))#" TITLE="#HTMLEditFormat(Purpose)#">#RoomName#</A></FONT><BR>
			</CFIF>
		</CFLOOP>
	</TD>
	<!--- Saturday ends the week: start a new row --->
	<CFIF Column EQ 7 AND d LT NumDays>
		</TR><TR VALIGN=TOP>
	</CFIF>
</CFLOOP>
<!--- pad out the last week --->
<CFSET Trailing = 7 - DayOfWeek(CreateDate(URL.year, URL.month, NumDays))>
<CFLOOP INDEX="b" FROM="1" TO="#Trailing#">
	<TD BGCOLOR="##DDDDDD">&nbsp;</TD>
</CFLOOP>
</TR>
</TABLE>
</TD></TR></TABLE>

<P>
<A HREF="book.cfm?Room_ID=#Val(URL.Room_ID)#"><IMG SRC="#Request.Images#/ic_calendar.gif" WIDTH=32 HEIGHT=32 BORDER=0 ALIGN=ABSMIDDLE> <B>Book a room</B></A>
&nbsp;&nbsp;&nbsp;<A HREF="rooms.cfm">Room list and equipment</A>
&nbsp;&nbsp;&nbsp;<FONT SIZE=1 COLOR="##666666">#GetBookings.RecordCount# booking<CFIF GetBookings.RecordCount NEQ 1>s</CFIF> this month. Click a date to see that day's schedule.</FONT>
</P>
</CFOUTPUT>

<CFINCLUDE TEMPLATE="../footer.cfm">
