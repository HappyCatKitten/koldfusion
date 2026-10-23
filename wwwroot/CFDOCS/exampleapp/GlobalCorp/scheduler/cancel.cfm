<!---
	scheduler/cancel.cfm - cancel a booking (your own, or any if you're an admin)
	  ?Booking_ID=n
--->
<CFPARAM NAME="URL.Booking_ID" DEFAULT="0">
<CFQUERY NAME="GetBooking" DATASOURCE="#Request.DSN#">
	SELECT Booking_ID, MeetingDate, BookedBy FROM Bookings WHERE Booking_ID = #Val(URL.Booking_ID)#
</CFQUERY>
<CFIF GetBooking.RecordCount EQ 0>
	<CFLOCATION URL="index.cfm" ADDTOKEN="No">
</CFIF>
<CFIF GetBooking.BookedBy IS Request.FullName OR Request.IsAdmin>
	<CFQUERY DATASOURCE="#Request.DSN#">
		DELETE FROM Bookings WHERE Booking_ID = #GetBooking.Booking_ID#
	</CFQUERY>
	<CFLOCATION URL="day.cfm?date=#URLEncodedFormat(DateFormat(GetBooking.MeetingDate, 'mm/dd/yyyy'))#&cancelled=yes" ADDTOKEN="No">
</CFIF>
<CFLOCATION URL="day.cfm?date=#URLEncodedFormat(DateFormat(GetBooking.MeetingDate, 'mm/dd/yyyy'))#" ADDTOKEN="No">
