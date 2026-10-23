<!---
	scheduler/room.cfm - all upcoming bookings for one room
	  ?Room_ID=n
--->
<CFPARAM NAME="URL.Room_ID" DEFAULT="0">
<CFSET Section = "scheduler">

<CFQUERY NAME="GetRoom" DATASOURCE="#Request.DSN#">
	SELECT * FROM Rooms WHERE Room_ID = #Val(URL.Room_ID)#
</CFQUERY>
<CFIF GetRoom.RecordCount EQ 0>
	<CFLOCATION URL="rooms.cfm" ADDTOKEN="No">
</CFIF>

<CFQUERY NAME="GetBookings" DATASOURCE="#Request.DSN#">
	SELECT Booking_ID, MeetingDate, StartTime, EndTime, Purpose, BookedBy
	FROM Bookings
	WHERE Room_ID = #GetRoom.Room_ID#
	  AND MeetingDate >= <CFQUERYPARAM CFSQLTYPE="CF_SQL_DATE" VALUE="#Now()#">
	ORDER BY MeetingDate, StartTime
</CFQUERY>

<CFSET PageTitle = GetRoom.RoomName>
<CFINCLUDE TEMPLATE="../header.cfm">

<CFOUTPUT>
<P><B>#GetRoom.Location#</B> &middot; seats #GetRoom.Capacity#<BR>
<FONT SIZE=1>Equipment: #GetRoom.Equipment#</FONT></P>
<P><A HREF="book.cfm?Room_ID=#GetRoom.Room_ID#">Book the #GetRoom.RoomName#</A> |
<A HREF="index.cfm?Room_ID=#GetRoom.Room_ID#">Calendar for this room</A> |
<A HREF="rooms.cfm">All rooms</A></P>
</CFOUTPUT>

<CFIF GetBookings.RecordCount EQ 0>
	<P>Nothing booked. It's all yours.</P>
<CFELSE>
	<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%">
	<TR BGCOLOR="#CCCCCC">
		<TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Date</B></FONT></TD>
		<TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Time</B></FONT></TD>
		<TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Meeting</B></FONT></TD>
		<TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Booked by</B></FONT></TD>
	</TR>
	<CFOUTPUT QUERY="GetBookings">
	<TR>
		<TD NOWRAP><FONT FACE="#Request.Font#" SIZE=2><A HREF="day.cfm?date=#URLEncodedFormat(DateFormat(MeetingDate, 'mm/dd/yyyy'))#">#DateFormat(MeetingDate, "ddd mmm d")#</A></FONT></TD>
		<TD NOWRAP><FONT FACE="#Request.Font#" SIZE=2>#TimeFormat(CreateTime(Int(StartTime / 100), StartTime MOD 100, 0), "h:mm tt")# - #TimeFormat(CreateTime(Int(EndTime / 100), EndTime MOD 100, 0), "h:mm tt")#</FONT></TD>
		<TD><FONT FACE="#Request.Font#" SIZE=2>#HTMLEditFormat(Purpose)#</FONT></TD>
		<TD><FONT FACE="#Request.Font#" SIZE=2>#HTMLEditFormat(BookedBy)#</FONT></TD>
	</TR>
	</CFOUTPUT>
	</TABLE>
</CFIF>

<CFINCLUDE TEMPLATE="../footer.cfm">
