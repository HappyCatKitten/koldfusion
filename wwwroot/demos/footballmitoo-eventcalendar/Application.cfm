<!--- KoldFusion Demo Gallery companion file (not part of the FootballMitoo repo).
      EventCalendar.cfm is a fragment of a much larger league-management app; the
      host application normally sets these session/request variables at login.
      This stand-in supplies just enough of them to run the calendar on its own.

        session.SeasonStartDate / SeasonEndDate - a season that always contains today
        session.LeagueID                        - 1 (the demo league in DSN "demos")
        request.DSN                             - "demos" (table "event", see kfroot/seed/demos.sql)
        request.SecurityLevel                   - "Bronze" (anything but Silver/Skyblue
                                                  selects the read-only InclEventLoop1.cfm)
        LeagueCode                              - used in the prev/next links --->
<cfapplication name="KFDemoFootballMitoo" sessionmanagement="Yes"
	sessiontimeout="#CreateTimeSpan(0,0,30,0)#">

<cfset request.DSN = "demos">
<cfset request.SecurityLevel = "Bronze">
<cfparam name="URL.LeagueCode" default="KFDEMO">
<cfset LeagueCode = URL.LeagueCode>

<cflock scope="session" timeout="10" type="exclusive">
	<cfif NOT IsDefined("session.SeasonStartDate")>
		<!--- season runs August..May, but stretch it so "today" is always inside --->
		<cfset session.SeasonStartDate = CreateDate(Year(Now()) - 1, 8, 1)>
		<cfset session.SeasonEndDate = CreateDate(Year(Now()) + 1, 5, 31)>
		<cfset session.LeagueID = 1>
	</cfif>
</cflock>
