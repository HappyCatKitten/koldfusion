<!---
	scheduler/day.cfm - every room's bookings for one day
	  ?date=mm/dd/yyyy
--->
<CFPARAM NAME="URL.date" DEFAULT="#DateFormat(Now(), 'mm/dd/yyyy')#">
<CFPARAM NAME="URL.cancelled" DEFAULT="">
<CFSET Section = "scheduler">
<CFIF NOT IsDate(URL.date)><CFSET URL.date = DateFormat(Now(), "mm/dd/yyyy")></CFIF>
<CFSET TheDate = ParseDateTime(URL.date)>
<CFSET TheDate = CreateDate(Year(TheDate), Month(TheDate), Day(TheDate))>
<CFSET PageTitle = DateFormat(TheDate, "dddd, mmmm d, yyyy")>

<CFQUERY NAME="GetSchedule" DATASOURCE="#Request.DSN#">
	SELECT r.Room_ID, r.RoomName, r.Location, r.Capacity,
	       b.Booking_ID, b.StartTime, b.EndTime, b.Purpose, b.BookedBy
	FROM Rooms r LEFT JOIN Bookings b
	  ON b.Room_ID = r.Room_ID
	 AND b.MeetingDate = <CFQUERYPARAM CFSQLTYPE="CF_SQL_DATE" VALUE="#TheDate#">
	ORDER BY r.RoomName, b.StartTime
</CFQUERY>

<CFINCLUDE TEMPLATE="../header.cfm">

<CFOUTPUT>
<FONT FACE="#Request.Font#" SIZE=2>
<A HREF="day.cfm?date=#URLEncodedFormat(DateFormat(DateAdd('d', -1, TheDate), 'mm/dd/yyyy'))#">&lt;&lt; Previous day</A> |
<A HREF="index.cfm?month=#Month(TheDate)#&year=#Year(TheDate)#">#MonthAsString(Month(TheDate))# calendar</A> |
<A HREF="day.cfm?date=#URLEncodedFormat(DateFormat(DateAdd('d', 1, TheDate), 'mm/dd/yyyy'))#">Next day &gt;&gt;</A>
</FONT>
<CFIF URL.cancelled IS "yes"><P><FONT COLOR="##006600"><B>The booking was cancelled.</B></FONT></P></CFIF>
</CFOUTPUT>

<TABLE WIDTH="100%" BORDER=0 CELLPADDING=4 CELLSPACING=0>
<CFOUTPUT QUERY="GetSchedule" GROUP="RoomName">
<TR><TD COLSPAN=3 BGCOLOR="##003366"><FONT FACE="#Request.Font#" SIZE=2 COLOR="##FFFFFF"><B>#RoomName#</B></FONT>
	<FONT FACE="#Request.Font#" SIZE=1 COLOR="##FFCC00">&nbsp; #Location#, seats #Capacity#</FONT></TD>
	<TD ALIGN=RIGHT BGCOLOR="##003366"><FONT FACE="#Request.Font#" SIZE=1><A HREF="book.cfm?Room_ID=#Room_ID#&date=#URLEncodedFormat(DateFormat(TheDate, 'mm/dd/yyyy'))#"><FONT COLOR="##FFFFFF">Book this room</FONT></A></FONT></TD></TR>
	<CFIF Len(Booking_ID) EQ 0>
		<TR><TD COLSPAN=4><FONT FACE="#Request.Font#" SIZE=2 COLOR="##666666"><I>Available all day</I></FONT></TD></TR>
	<CFELSE>
		<CFOUTPUT>
		<TR>
			<TD WIDTH=140 NOWRAP><FONT FACE="#Request.Font#" SIZE=2><B>#TimeFormat(CreateTime(Int(StartTime / 100), StartTime MOD 100, 0), "h:mm tt")# - #TimeFormat(CreateTime(Int(EndTime / 100), EndTime MOD 100, 0), "h:mm tt")#</B></FONT></TD>
			<TD><FONT FACE="#Request.Font#" SIZE=2>#HTMLEditFormat(Purpose)#</FONT></TD>
			<TD><FONT FACE="#Request.Font#" SIZE=1>#HTMLEditFormat(BookedBy)#</FONT></TD>
			<TD ALIGN=RIGHT><CFIF BookedBy IS Request.FullName OR Request.IsAdmin><FONT FACE="#Request.Font#" SIZE=1><A HREF="cancel.cfm?Booking_ID=#Booking_ID#" onClick="return confirm('Cancel this booking?')">cancel</A></FONT></CFIF></TD>
		</TR>
		</CFOUTPUT>
	</CFIF>
</CFOUTPUT>
</TABLE>

<CFINCLUDE TEMPLATE="../footer.cfm">
