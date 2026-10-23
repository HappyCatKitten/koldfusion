<!---
	scheduler/book.cfm - booking form
	  ?Room_ID=n&date=mm/dd/yyyy   (both optional)
--->
<CFPARAM NAME="URL.Room_ID" DEFAULT="0">
<CFPARAM NAME="URL.date" DEFAULT="#DateFormat(Now(), 'mm/dd/yyyy')#">
<CFSET Section = "scheduler">
<CFSET PageTitle = "Book a Meeting Room">

<CFQUERY NAME="GetRooms" DATASOURCE="#Request.DSN#">
	SELECT Room_ID, RoomName & ' (' & Capacity & ' seats)' AS RoomLabel
	FROM Rooms ORDER BY RoomName
</CFQUERY>

<CFINCLUDE TEMPLATE="../header.cfm">

<P>Rooms can be booked in half-hour steps between 7:00 AM and 7:00 PM.
If someone already has the room, you'll be told who to talk to.</P>

<CFFORM ACTION="book_action.cfm" METHOD="POST" NAME="BookingForm">
<CFOUTPUT>
<INPUT TYPE="Hidden" NAME="MeetingDate_required" VALUE="Please enter the date of the meeting.">
<INPUT TYPE="Hidden" NAME="MeetingDate_date" VALUE="The meeting date must be a date, like 06/15/2000.">
<INPUT TYPE="Hidden" NAME="Purpose_required" VALUE="Please say what the meeting is for.">
<INPUT TYPE="Hidden" NAME="BookedBy_required" VALUE="Please enter your name.">
<INPUT TYPE="Hidden" NAME="StartTime_integer" VALUE="Please choose a start time.">
<INPUT TYPE="Hidden" NAME="EndTime_integer" VALUE="Please choose an end time.">
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>Room:</B></FONT></TD>
	<TD><CFSELECT NAME="Room_ID" QUERY="GetRooms" VALUE="Room_ID" DISPLAY="RoomLabel" SELECTED="#URL.Room_ID#"></CFSELECT></TD></TR>
<TR><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>Date:</B></FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="MeetingDate" VALUE="#URL.date#" SIZE="12" MAXLENGTH="10" REQUIRED="Yes" VALIDATE="date" MESSAGE="Please enter the meeting date as mm/dd/yyyy.">
	<FONT FACE="#Request.Font#" SIZE=1>mm/dd/yyyy</FONT></TD></TR>
<TR><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>From:</B></FONT></TD>
	<TD><SELECT NAME="StartTime">
		<CFLOOP INDEX="h" FROM="7" TO="18"><CFLOOP INDEX="m" LIST="0,30">
			<OPTION VALUE="#h * 100 + m#"<CFIF h * 100 + m EQ 900> SELECTED</CFIF>>#TimeFormat(CreateTime(h, m, 0), "h:mm tt")#
		</CFLOOP></CFLOOP>
	</SELECT>
	<FONT FACE="#Request.Font#" SIZE=2><B>to</B></FONT>
	<SELECT NAME="EndTime">
		<CFLOOP INDEX="h" FROM="7" TO="19"><CFLOOP INDEX="m" LIST="0,30">
			<CFIF h * 100 + m GT 700 AND h * 100 + m LE 1900>
			<OPTION VALUE="#h * 100 + m#"<CFIF h * 100 + m EQ 1000> SELECTED</CFIF>>#TimeFormat(CreateTime(h, m, 0), "h:mm tt")#
			</CFIF>
		</CFLOOP></CFLOOP>
	</SELECT></TD></TR>
<TR><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>Purpose:</B></FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="Purpose" SIZE="40" MAXLENGTH="80" REQUIRED="Yes" MESSAGE="Please say what the meeting is for."></TD></TR>
<TR><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>Booked by:</B></FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="BookedBy" VALUE="#Request.FullName#" SIZE="30" MAXLENGTH="50" REQUIRED="Yes" MESSAGE="Please enter your name."></TD></TR>
<TR><TD></TD><TD><INPUT TYPE="Submit" VALUE="Book It"> <INPUT TYPE="Button" VALUE="Cancel" onClick="location.href='index.cfm'"></TD></TR>
</TABLE>
</CFOUTPUT>
</CFFORM>

<CFINCLUDE TEMPLATE="../footer.cfm">
