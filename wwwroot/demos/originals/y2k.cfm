<!---
  y2k.cfm - the Y2K page every 1999 site had. Before 1 January 2000 it counts
  down; afterwards it counts the days since the world didn't end (and points
  at the next one: the Unix time_t rollover of 19 January 2038). Includes a
  Y2K compliance self-test of the server's date functions.
  ?asof=12/31/1999 pretends it is another date. KoldFusion Demo Gallery original - MIT licence.
--->
<cfparam name="URL.asof" default="">
<cfif Len(URL.asof) AND IsDate(URL.asof)>
	<cfset rightNow = ParseDateTime(URL.asof)>
	<cfset pretending = true>
<cfelse>
	<cfset rightNow = Now()>
	<cfset pretending = false>
</cfif>
<cfset y2k = CreateDateTime(2000, 1, 1, 0, 0, 0)>
<cfset y2k38 = CreateDateTime(2038, 1, 19, 3, 14, 7)>
<cfset before = DateCompare(rightNow, y2k) LT 0>

<cfif before>
	<cfset secs = DateDiff("s", rightNow, y2k)>
<cfelse>
	<cfset secs = DateDiff("s", y2k, rightNow)>
</cfif>
<cfset days = Int(secs / 86400)>
<cfset hours = Int((secs MOD 86400) / 3600)>
<cfset mins = Int((secs MOD 3600) / 60)>
<cfset s = secs MOD 60>
<cfset bigDays = NumberFormat(days, "00000")>
<cfset days38 = DateDiff("d", rightNow, y2k38)>

<html>
<head>
<title>Y2K Countdown</title>
<cfif NOT pretending><meta http-equiv="refresh" content="60"></cfif>
</head>
<body background="/images/stars_bg.gif" bgcolor="#000000" text="#FFFFFF" link="#00FFFF" vlink="#00FFFF">
<center>
<img src="/images/globe.gif" width="32" height="32" alt="">
<font face="Arial Black, Arial, Helvetica" size="6" color="#FF3333"><b>Y2K</b></font>
<img src="/images/globe.gif" width="32" height="32" alt=""><br>
<cfoutput>
<font face="Arial, Helvetica" size="3" color="##FFFF00">
<cfif before>
	<b>The Millennium Bug strikes in...</b>
<cfelse>
	<b>The world did not end. It has been...</b>
</cfif>
</font>
<p>
<table border="3" cellpadding="6" bgcolor="##000000"><tr><td align="center">
<cfloop from="1" to="#Len(bigDays)#" index="i"><img src="/images/digit_#Mid(bigDays, i, 1)#.gif" width="30" height="40" alt="#Mid(bigDays, i, 1)#"></cfloop>
<br><font face="Arial, Helvetica" size="2" color="##00FF00"><b>DAYS</b></font>
</td></tr></table>
<p>
<font face="Courier New, Courier" size="4" color="##00FF00"><b>#days# days, #hours# hours, #mins# minutes and #s# seconds</b></font><br>
<font face="Arial, Helvetica" size="2">
<cfif before>until midnight on Saturday, January 1, 2000.<cfelse>since midnight on Saturday, January 1, 2000.</cfif>
<br>(as of #DateFormat(rightNow, "dddd, mmmm d, yyyy")# #TimeFormat(rightNow, "h:mm:ss tt")#<cfif pretending> - pretend mode</cfif>)
</font>
<p>
<img src="/images/rainbow_hr.gif" width="500" height="6" alt="------">
<p>
<font face="Arial, Helvetica" size="3" color="##FF99FF"><b>Next up: Y2K38</b></font><br>
<font face="Arial, Helvetica" size="2">
32-bit Unix clocks overflow on #DateFormat(y2k38, "dddd, mmmm d, yyyy")# at #TimeFormat(y2k38, "HH:mm:ss")# UTC.<br>
<cfif days38 GT 0>That is <b>#NumberFormat(days38, "9,999")#</b> days away. Start stockpiling canned goods now.
<cfelse>That was #NumberFormat(-days38, "9,999")# days ago. Hope you patched.</cfif>
</font>
</cfoutput>
<p>
<img src="/images/rainbow_hr.gif" width="500" height="6" alt="------">
<p>
<!--- the self-test: each row is an expression and the answer a compliant server must give --->
<font face="Arial, Helvetica" size="3" color="#00FFFF"><b>This server's Y2K compliance self-test</b></font>
<table border="1" cellpadding="4" cellspacing="0" bgcolor="#000033" bordercolor="#3333CC">
<tr bgcolor="#3333CC"><th><font face="Arial" size="2">Test</font></th><th><font face="Arial" size="2">Expected</font></th><th><font face="Arial" size="2">Got</font></th><th><font face="Arial" size="2">Result</font></th></tr>
<cfset tests = "Is 2000 a leap year?|IsLeapYear(2000)|YES"
	& "~Is 1900 a leap year?|IsLeapYear(1900)|NO"
	& "~Day after 12/31/1999|DateFormat(DateAdd('d', 1, CreateDate(1999,12,31)), 'mm/dd/yyyy')|01/01/2000"
	& "~Day of the week of 1/1/2000|DayOfWeekAsString(DayOfWeek(CreateDate(2000,1,1)))|Saturday"
	& "~Days in February 2000|DaysInMonth(CreateDate(2000,2,1))|29"
	& "~Day after 2/28/2000|DateFormat(DateAdd('d', 1, CreateDate(2000,2,28)), 'mm/dd/yyyy')|02/29/2000"
	& "~Days in the year 2000|DaysInYear(CreateDate(2000,1,1))|366"
	& "~Two-digit year: 1/1/00|Year(ParseDateTime('1/1/00'))|2000"
	& "~Two-digit year: 12/31/99|Year(ParseDateTime('12/31/99'))|1999"
	& "~Days from 12/31/1999 to 3/1/2000|DateDiff('d', CreateDate(1999,12,31), CreateDate(2000,3,1))|61">
<cfset passed = 0>
<cfloop list="#tests#" index="t" delimiters="~">
	<cfset label = ListGetAt(t, 1, "|")>
	<cfset expr = ListGetAt(t, 2, "|")>
	<cfset want = ListGetAt(t, 3, "|")>
	<cftry>
		<cfset got = Evaluate(expr)>
		<cfcatch type="Any"><cfset got = "ERROR"></cfcatch>
	</cftry>
	<cfset ok = (got IS want)>
	<cfif ok><cfset passed = passed + 1></cfif>
	<cfoutput>
	<tr><td><font face="Arial" size="2">#label#<br><font size="1" color="##9999FF">#HTMLEditFormat(expr)#</font></font></td>
	<td align="center"><font face="Courier New" size="2">#want#</font></td>
	<td align="center"><font face="Courier New" size="2">#HTMLEditFormat(got)#</font></td>
	<td align="center"><font face="Arial" size="2" color="###IIf(ok, DE('00FF00'), DE('FF3333'))#"><b>#IIf(ok, DE('PASS'), DE('FAIL'))#</b></font></td></tr>
	</cfoutput>
</cfloop>
</table>
<cfoutput>
<p><font face="Arial, Helvetica" size="3">
<cfif passed IS ListLen(tests, "~")>
	<font color="##00FF00"><b>#passed# of #ListLen(tests, "~")# passed. This server is Y2K COMPLIANT!</b></font>
<cfelse>
	<font color="##FF3333"><b>Only #passed# of #ListLen(tests, "~")# passed. Head for the bunker.</b></font>
</cfif>
</font>
<p><font face="Arial, Helvetica" size="2">Time travel:
<a href="y2k.cfm?asof=#URLEncodedFormat('12/31/1999 23:59:00')#">one minute to midnight</a> |
<a href="y2k.cfm?asof=#URLEncodedFormat('1/1/1999')#">New Year's Day 1999</a> |
<a href="y2k.cfm">right now</a></font>
</cfoutput>
</center>
<cfinclude template="_footer.cfm">
</body>
</html>
