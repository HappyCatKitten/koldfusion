<!--- KoldFusion Demo Gallery companion (not part of the FootballMitoo repo).
      The calendar links each highlighted day to EventCalendarShow.cfm, which was
      not published with the calendar. This stand-in lists that day's events from
      the "event" table in DSN demos. URL.event_date arrives as an ODBC date
      literal such as {d '2026-10-22'}; it is validated before use. --->
<cfparam name="URL.event_date" default="">
<cfset ok = REFind("^\{d '[0-9]{4}-[0-9]{2}-[0-9]{2}'\}$", URL.event_date)>
<html>
<head>
	<title>Diary</title>
	<link rel="stylesheet" type="text/css" href="EventCalendarStyle.css">
</head>
<body bgcolor="#EEEEEE">
<cfif ok>
	<cfset y = Mid(URL.event_date, 5, 4)>
	<cfset m = Mid(URL.event_date, 10, 2)>
	<cfset d = Mid(URL.event_date, 13, 2)>
	<cfquery name="DaysEvents" datasource="#request.DSN#">
		SELECT EventText
		FROM event
		WHERE LeagueID = #Val(session.LeagueID)#
		  AND MONTH(EventDate) = #Val(m)#
		  AND DAY(EventDate) = #Val(d)#
	</cfquery>
	<table align="center" width="90%" border="0" cellpadding="4" cellspacing="0">
	<tr class="toprow"><td><cfoutput><span class="showheader">#DateFormat(CreateDate(y, m, d), "dddd d mmmm yyyy")#</span></cfoutput></td></tr>
	<cfoutput query="DaysEvents">
	<tr><td class="event">#EventText#</td></tr>
	</cfoutput>
	<cfif DaysEvents.RecordCount IS 0>
	<tr><td class="non-event">Nothing in the diary for this day.</td></tr>
	</cfif>
	</table>
<cfelse>
	<p>No date given.</p>
</cfif>
<p align="center"><a href="EventCalendar.cfm">Back to the calendar</a></p>
</body>
</html>
