<!---
	scheduler/rooms.cfm - the meeting rooms and how busy they are
--->
<CFSET Section = "scheduler">
<CFSET PageTitle = "Meeting Rooms">

<CFQUERY NAME="GetRooms" DATASOURCE="#Request.DSN#">
	SELECT r.Room_ID, r.RoomName, r.Location, r.Capacity, r.Equipment, COUNT(b.Booking_ID) AS Upcoming
	FROM Rooms r LEFT JOIN Bookings b
	  ON b.Room_ID = r.Room_ID
	 AND b.MeetingDate >= <CFQUERYPARAM CFSQLTYPE="CF_SQL_DATE" VALUE="#Now()#">
	GROUP BY r.Room_ID, r.RoomName, r.Location, r.Capacity, r.Equipment
	ORDER BY r.RoomName
</CFQUERY>

<CFINCLUDE TEMPLATE="../header.cfm">

<TABLE WIDTH="100%" BORDER=0 CELLPADDING=4 CELLSPACING=0>
<TR BGCOLOR="#003366">
	<TD><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Room</B></FONT></TD>
	<TD><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Location</B></FONT></TD>
	<TD ALIGN=CENTER><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Seats</B></FONT></TD>
	<TD><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Equipment</B></FONT></TD>
	<TD ALIGN=CENTER><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Upcoming</B></FONT></TD>
</TR>
<CFOUTPUT QUERY="GetRooms">
<TR VALIGN=TOP BGCOLOR="###IIf(CurrentRow MOD 2, DE('FFFFFF'), DE('F0F0F0'))#">
	<TD><FONT FACE="#Request.Font#" SIZE=2><A HREF="room.cfm?Room_ID=#Room_ID#"><B>#RoomName#</B></A></FONT></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2>#Location#</FONT></TD>
	<TD ALIGN=CENTER><FONT FACE="#Request.Font#" SIZE=2>#Capacity#</FONT></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=1>#Equipment#</FONT></TD>
	<TD ALIGN=CENTER><FONT FACE="#Request.Font#" SIZE=2>#Upcoming#</FONT></TD>
</TR>
</CFOUTPUT>
</TABLE>
<P><A HREF="index.cfm">Back to the calendar</A> | <A HREF="book.cfm">Book a room</A></P>

<CFINCLUDE TEMPLATE="../footer.cfm">
