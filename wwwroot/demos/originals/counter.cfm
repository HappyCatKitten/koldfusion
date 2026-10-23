<!---
  counter.cfm - the classic "This page has been visited N times" hit counter,
  drawn with odometer digit GIFs. The count is kept in the Counters table of
  DSN "demos", so it survives server restarts; a named CFLOCK around the
  UPDATE/SELECT pair stops two simultaneous hits from reading the same number.
  KoldFusion Demo Gallery original - MIT licence.
--->
<cfset counterName = "originals/counter.cfm">

<cflock name="KFDemoCounter" type="exclusive" timeout="10">
	<cftransaction>
		<cfquery name="Bump" datasource="demos">
			UPDATE Counters SET Hits = Hits + 1
			WHERE CounterName = <cfqueryparam value="#counterName#" cfsqltype="CF_SQL_VARCHAR">
		</cfquery>
		<cfquery name="Hits" datasource="demos">
			SELECT Hits FROM Counters
			WHERE CounterName = <cfqueryparam value="#counterName#" cfsqltype="CF_SQL_VARCHAR">
		</cfquery>
		<cfif Hits.RecordCount IS 0>
			<!--- first hit ever (or someone emptied the table) --->
			<cfquery datasource="demos">
				INSERT INTO Counters (CounterName, Hits)
				VALUES (<cfqueryparam value="#counterName#" cfsqltype="CF_SQL_VARCHAR">, 1)
			</cfquery>
			<cfset count = 1>
		<cfelse>
			<cfset count = Hits.Hits>
		</cfif>
	</cftransaction>
</cflock>

<!--- how many of those were you? --->
<cflock scope="session" type="exclusive" timeout="10">
	<cfparam name="session.myCounterHits" default="0">
	<cfset session.myCounterHits = session.myCounterHits + 1>
	<cfset mine = session.myCounterHits>
</cflock>

<cfset digits = NumberFormat(count, "000000")>

<html>
<head>
<title>Hit Counter</title>
</head>
<body background="/images/bg_tile.gif" bgcolor="#FFFFFF">
<center>
<p>&nbsp;</p>
<table border="3" cellpadding="16" bgcolor="#FFFFFF"><tr><td align="center">
<img src="/images/fire.gif" width="120" height="30" alt="">
<p>
<font face="Times New Roman, Times" size="5"><b>This page has been visited</b></font>
<p>
<table border="2" cellpadding="3" cellspacing="0" bgcolor="#000000"><tr><td>
<cfoutput><cfloop from="1" to="#Len(digits)#" index="i"><img src="/images/digit_#Mid(digits, i, 1)#.gif" width="15" height="20" alt="#Mid(digits, i, 1)#"></cfloop></cfoutput>
</td></tr></table>
<p>
<font face="Times New Roman, Times" size="5"><b>times!</b></font>
<p>
<font face="Arial, Helvetica" size="2">
<cfoutput>
<cfif mine IS 1>
	Welcome, visitor ###NumberFormat(count, "9,999")#! Bookmark this page and come back soon.
<cfelse>
	You personally have reloaded this page #mine# times this session. Stop that. ;-)
</cfif>
</cfoutput>
</font>
<p>
<font face="Arial, Helvetica" size="1">Counter stored in DSN <b>demos</b>, table <b>Counters</b>.<br>
(Hit reload. Go on, you know you want to.)</font>
</td></tr></table>
</center>
<cfinclude template="_footer.cfm">
</body>
</html>
