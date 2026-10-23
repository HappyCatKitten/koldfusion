<!---
	scheduler/book_action.cfm - checks for conflicts, then saves the booking.
	Two meetings overlap when each one starts before the other one ends:
	    existing.StartTime < new.EndTime  AND  existing.EndTime > new.StartTime
	so a single query finds every booking that would collide with this one.
--->
<CFIF NOT IsDefined("Form.Room_ID")>
	<CFLOCATION URL="index.cfm" ADDTOKEN="No">
</CFIF>
<CFSET Section = "scheduler">
<CFSET Problem = "">
<CFSET TheDate = ParseDateTime(Form.MeetingDate)>
<CFSET TheDate = CreateDate(Year(TheDate), Month(TheDate), Day(TheDate))>
<CFSET NewStart = Val(Form.StartTime)>
<CFSET NewEnd = Val(Form.EndTime)>

<CFIF NewEnd LE NewStart>
	<CFSET Problem = "The meeting has to end after it starts.">
<CFELSEIF DateCompare(TheDate, Now(), "d") LT 0>
	<CFSET Problem = "That date is in the past. Even KoldFusion can't book rooms yesterday.">
</CFIF>

<CFIF NOT Len(Problem)>
	<!--- lock so two people can't grab the same slot at the same moment --->
	<CFLOCK NAME="GlobalCorpRoomBooking" TYPE="Exclusive" TIMEOUT="15">
		<CFQUERY NAME="Conflicts" DATASOURCE="#Request.DSN#">
			SELECT b.StartTime, b.EndTime, b.Purpose, b.BookedBy, r.RoomName
			FROM Bookings b, Rooms r
			WHERE b.Room_ID = r.Room_ID
			  AND b.Room_ID = #Val(Form.Room_ID)#
			  AND b.MeetingDate = <CFQUERYPARAM CFSQLTYPE="CF_SQL_DATE" VALUE="#TheDate#">
			  AND b.StartTime < #NewEnd#
			  AND b.EndTime > #NewStart#
			ORDER BY b.StartTime
		</CFQUERY>
		<CFIF Conflicts.RecordCount EQ 0>
			<CFQUERY DATASOURCE="#Request.DSN#">
				INSERT INTO Bookings (Room_ID, MeetingDate, StartTime, EndTime, Purpose, BookedBy)
				VALUES (#Val(Form.Room_ID)#, <CFQUERYPARAM CFSQLTYPE="CF_SQL_DATE" VALUE="#TheDate#">,
				        #NewStart#, #NewEnd#, '#Left(Trim(Form.Purpose), 80)#', '#Left(Trim(Form.BookedBy), 50)#')
			</CFQUERY>
		</CFIF>
	</CFLOCK>
</CFIF>

<CFQUERY NAME="GetRoom" DATASOURCE="#Request.DSN#">
	SELECT RoomName FROM Rooms WHERE Room_ID = #Val(Form.Room_ID)#
</CFQUERY>

<CFIF Len(Problem)>
	<CFSET PageTitle = "Booking Not Saved">
<CFELSEIF Conflicts.RecordCount>
	<CFSET PageTitle = "Sorry, That Room Is Taken">
<CFELSE>
	<CFSET PageTitle = "Room Booked">
</CFIF>
<CFINCLUDE TEMPLATE="../header.cfm">

<CFOUTPUT>
<CFIF Len(Problem)>
	<P><IMG SRC="/CFIDE/administrator/images/warn.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE> #Problem#</P>
	<FORM><INPUT TYPE="Button" VALUE="Go Back" onClick="history.back()"></FORM>
<CFELSEIF Conflicts.RecordCount>
	<P><IMG SRC="/CFIDE/administrator/images/x.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
	The <B>#GetRoom.RoomName#</B> is already booked on #DateFormat(TheDate, "dddd, mmmm d")# at that time:</P>
	<UL>
	<CFLOOP QUERY="Conflicts">
		<LI>#TimeFormat(CreateTime(Int(StartTime / 100), StartTime MOD 100, 0), "h:mm tt")# - #TimeFormat(CreateTime(Int(EndTime / 100), EndTime MOD 100, 0), "h:mm tt")#:
		#HTMLEditFormat(Purpose)# (#HTMLEditFormat(BookedBy)#)
	</CFLOOP>
	</UL>
	<P>Try another time, or <A HREF="day.cfm?date=#URLEncodedFormat(DateFormat(TheDate, 'mm/dd/yyyy'))#">see which rooms are free that day</A>.</P>
	<FORM><INPUT TYPE="Button" VALUE="Go Back" onClick="history.back()"></FORM>
<CFELSE>
	<P><IMG SRC="/CFIDE/administrator/images/check.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
	The <B>#GetRoom.RoomName#</B> is yours on <B>#DateFormat(TheDate, "dddd, mmmm d, yyyy")#</B>
	from <B>#TimeFormat(CreateTime(Int(NewStart / 100), NewStart MOD 100, 0), "h:mm tt")#</B>
	to <B>#TimeFormat(CreateTime(Int(NewEnd / 100), NewEnd MOD 100, 0), "h:mm tt")#</B>.</P>
	<P><A HREF="day.cfm?date=#URLEncodedFormat(DateFormat(TheDate, 'mm/dd/yyyy'))#">See the day's schedule</A> |
	<A HREF="index.cfm?month=#Month(TheDate)#&year=#Year(TheDate)#">Back to the calendar</A></P>
</CFIF>
</CFOUTPUT>

<CFINCLUDE TEMPLATE="../footer.cfm">
