<!---
  calendar.cfm - a month-at-a-glance calendar with week numbers, today's date
  highlighted, fixed and "floating" holidays (Thanksgiving = 4th Thursday of
  November, and so on) and a jump-to form. Pure date arithmetic: CreateDate,
  DayOfWeek, DaysInMonth, DateAdd, Week. KoldFusion Demo Gallery original - MIT licence.
--->
<cfparam name="URL.month" default="#Month(Now())#">
<cfparam name="URL.year" default="#Year(Now())#">
<cfif NOT IsNumeric(URL.month) OR URL.month LT 1 OR URL.month GT 12><cfset URL.month = Month(Now())></cfif>
<cfif NOT IsNumeric(URL.year) OR URL.year LT 1900 OR URL.year GT 2099><cfset URL.year = Year(Now())></cfif>
<cfset firstDay = CreateDate(URL.year, URL.month, 1)>
<cfset prevMonth = DateAdd("m", -1, firstDay)>
<cfset nextMonth = DateAdd("m", 1, firstDay)>
<cfset daysIn = DaysInMonth(firstDay)>
<cfset offset = DayOfWeek(firstDay) - 1>

<!--- holidays as a structure keyed by day of this month --->
<cfset holidays = StructNew()>
<cfset fixed = "1/1=New Year's Day|2/2=Groundhog Day|2/14=Valentine's Day|3/17=St. Patrick's Day|4/1=April Fools' Day|"
	& "4/22=Earth Day|7/4=Independence Day|10/31=Halloween|11/11=Veterans Day|12/24=Christmas Eve|12/25=Christmas Day|12/31=New Year's Eve">
<cfloop list="#fixed#" index="h" delimiters="|">
	<cfset md = ListFirst(h, "=")>
	<cfif ListFirst(md, "/") IS URL.month>
		<cfset holidays[ListLast(md, "/")] = ListLast(h, "=")>
	</cfif>
</cfloop>
<!--- floating holidays: Nth weekday of the month (N = -1 means the last one) --->
<cfset floating = "1,2,3=Martin Luther King Jr. Day|2,2,3=Presidents' Day|5,1,2=Mother's Day|5,2,-1=Memorial Day|"
	& "6,1,3=Father's Day|9,2,1=Labor Day|10,2,2=Columbus Day|11,5,4=Thanksgiving">
<cfloop list="#floating#" index="h" delimiters="|">
	<cfset rule = ListFirst(h, "=")>
	<cfif ListGetAt(rule, 1) IS URL.month>
		<cfset wday = ListGetAt(rule, 2)>
		<cfset nth = ListGetAt(rule, 3)>
		<!--- first such weekday in the month --->
		<cfset d = 1 + ((wday - DayOfWeek(firstDay) + 7) MOD 7)>
		<cfif nth GT 0>
			<cfset d = d + (nth - 1) * 7>
		<cfelse>
			<cfloop condition="d + 7 LTE daysIn"><cfset d = d + 7></cfloop>
		</cfif>
		<cfset holidays[d] = ListLast(h, "=")>
	</cfif>
</cfloop>
<!--- a couple of dates every webmaster of 1999 had circled --->
<cfif URL.year IS 1999 AND URL.month IS 9><cfset holidays[9] = "9/9/99 - the other Y2K bug"></cfif>
<cfif URL.year IS 2000 AND URL.month IS 1><cfset holidays[1] = "Y2K! Did the lights stay on?"></cfif>
<cfif URL.year IS 2000 AND URL.month IS 2><cfset holidays[29] = "Leap day - the Y2K bug's sequel"></cfif>

<html>
<head>
<title>Calendar - <cfoutput>#MonthAsString(URL.month)# #URL.year#</cfoutput></title>
</head>
<body bgcolor="#FFFFFF" background="/images/bg_tile.gif">
<center>
<cfoutput>
<table border="0" cellpadding="0" cellspacing="0" bgcolor="##000066"><tr><td>
<table border="0" cellpadding="4" cellspacing="1" width="620">
<tr bgcolor="##003399">
	<td align="center"><a href="calendar.cfm?month=#Month(prevMonth)#&year=#Year(prevMonth)#"><font face="Arial" size="2" color="##FFFF00"><b>&lt;&lt; #Left(MonthAsString(Month(prevMonth)), 3)#</b></font></a></td>
	<td colspan="6" align="center"><font face="Arial, Helvetica" size="5" color="##FFFFFF"><b>#MonthAsString(URL.month)# #URL.year#</b></font></td>
	<td align="center"><a href="calendar.cfm?month=#Month(nextMonth)#&year=#Year(nextMonth)#"><font face="Arial" size="2" color="##FFFF00"><b>#Left(MonthAsString(Month(nextMonth)), 3)# &gt;&gt;</b></font></a></td>
</tr>
<tr bgcolor="##6699CC">
	<td align="center"><font face="Arial" size="1" color="##FFFFFF">Wk</font></td>
	<cfloop from="1" to="7" index="dw"><td align="center" width="80"><font face="Arial" size="2" color="##FFFFFF"><b>#DayOfWeekAsString(dw)#</b></font></td></cfloop>
</tr>
<cfset cell = 0>
<cfset day = 1>
<cfloop condition="day LTE daysIn">
	<tr bgcolor="##FFFFFF">
	<cfset weekDate = CreateDate(URL.year, URL.month, day)>
	<td align="center" bgcolor="##DDDDEE"><font face="Arial" size="1" color="##666699">#Week(weekDate)#</font></td>
	<cfloop from="1" to="7" index="dw">
		<cfset cell = cell + 1>
		<cfif cell LTE offset OR day GT daysIn>
			<td bgcolor="##EEEEEE">&nbsp;</td>
		<cfelse>
			<cfset isToday = (URL.year IS Year(Now())) AND (URL.month IS Month(Now())) AND (day IS Day(Now()))>
			<cfif isToday><cfset bg = "FFFF99"><cfelseif StructKeyExists(holidays, day)><cfset bg = "FFE0E0"><cfelseif dw IS 1 OR dw IS 7><cfset bg = "F0F0FF"><cfelse><cfset bg = "FFFFFF"></cfif>
			<td valign="top" height="60" bgcolor="###bg#">
				<font face="Arial, Helvetica" size="3"<cfif dw IS 1> color="##CC0000"</cfif>><b>#day#</b></font>
				<cfif isToday><br><font face="Arial" size="1" color="##996600"><b>TODAY</b></font></cfif>
				<cfif StructKeyExists(holidays, day)><br><font face="Arial" size="1" color="##CC0000">#holidays[day]#</font></cfif>
			</td>
			<cfset day = day + 1>
		</cfif>
	</cfloop>
	</tr>
</cfloop>
</table>
</td></tr></table>

<p>
<form action="calendar.cfm" method="get">
<font face="Arial, Helvetica" size="2">Jump to:</font>
<select name="month">
	<cfloop from="1" to="12" index="m"><option value="#m#"<cfif m IS URL.month> selected</cfif>>#MonthAsString(m)#</cfloop>
</select>
<input type="text" name="year" size="5" maxlength="4" value="#URL.year#">
<input type="submit" value="Go">
&nbsp; <font face="Arial, Helvetica" size="2"><a href="calendar.cfm">Today</a> |
<a href="calendar.cfm?month=12&year=1999">December 1999</a> |
<a href="calendar.cfm?month=1&year=2000">January 2000</a></font>
</form>
</cfoutput>
</center>
<cfinclude template="_footer.cfm">
</body>
</html>
