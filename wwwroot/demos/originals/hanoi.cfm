<!---
  hanoi.cfm - Towers of Hanoi solver. The solution is computed by the
  recursive custom tag hanoi_move.cfm (CFMODULE calling itself), then replayed
  move by move. Step through it, or let <META REFRESH> animate it for you.
  KoldFusion Demo Gallery original - MIT licence.
--->
<cfparam name="URL.disks" default="4">
<cfparam name="URL.step" default="0">
<cfparam name="URL.auto" default="0">
<cfif NOT IsNumeric(URL.disks) OR URL.disks LT 1 OR URL.disks GT 8><cfset URL.disks = 4></cfif>
<cfset disks = Int(URL.disks)>
<cfset total = 2 ^ disks - 1>
<cfif NOT IsNumeric(URL.step) OR URL.step LT 0><cfset URL.step = 0></cfif>
<cfset step = Min(Int(URL.step), total)>
<cfset auto = (URL.auto IS 1) AND (step LT total)>

<!--- solve: the custom tag recurses and fills Request.hanoiMoves --->
<cfset Request.hanoiMoves = ArrayNew(1)>
<cfmodule template="hanoi_move.cfm" n="#disks#" from="1" to="3" via="2">

<!--- replay the first STEP moves on three pegs (each peg is a list, top disk last) --->
<cfset pegs = ArrayNew(1)>
<cfset pegs[1] = "">
<cfset pegs[2] = "">
<cfset pegs[3] = "">
<cfloop from="#disks#" to="1" step="-1" index="d">
	<cfset pegs[1] = ListAppend(pegs[1], d)>
</cfloop>
<cfloop from="1" to="#step#" index="m">
	<cfset mv = Request.hanoiMoves[m]>
	<cfset src = ListGetAt(mv, 2)>
	<cfset dst = ListGetAt(mv, 3)>
	<cfset pegs[dst] = ListAppend(pegs[dst], ListLast(pegs[src]))>
	<cfset pegs[src] = ListDeleteAt(pegs[src], ListLen(pegs[src]))>
</cfloop>

<cfset colors = "FF0000,FF9900,FFFF00,00CC00,00CCCC,0066FF,9933FF,FF66CC">
<cfset pegNames = "A,B,C">

<html>
<head>
<title>Towers of Hanoi</title>
<cfif auto>
	<cfoutput><meta http-equiv="refresh" content="1;URL=hanoi.cfm?disks=#disks#&step=#step + 1#&auto=1"></cfoutput>
</cfif>
</head>
<body bgcolor="#FFFFFF" background="/images/bg_tile.gif">
<center>
<font face="Arial, Helvetica" size="5" color="#003399"><b>The Towers of Hanoi</b></font><br>
<font face="Arial, Helvetica" size="2">Solved by a custom tag that calls itself. No UDFs were harmed.</font>
<p>
<cfoutput>
<table border="2" cellpadding="10" cellspacing="0" bgcolor="##FFFFEE">
<tr>
<cfloop from="1" to="3" index="p">
	<td width="200" align="center" valign="bottom">
	<!--- draw the peg top-down: empty slots first, then disks from the top --->
	<cfset height = ListLen(pegs[p])>
	<table border="0" cellpadding="0" cellspacing="1">
	<cfloop from="#disks#" to="1" step="-1" index="level">
		<tr><td align="center" height="18">
		<cfif level LTE height>
			<cfset d = ListGetAt(pegs[p], level)>
			<table border="1" cellpadding="0" cellspacing="0" width="#d * 20 + 10#" bgcolor="###ListGetAt(colors, d)#"><tr><td align="center"><font face="Arial" size="1"><b>#d#</b></font></td></tr></table>
		<cfelse>
			<table border="0" cellpadding="0" cellspacing="0" width="6" bgcolor="##663300"><tr><td height="16"><img src="/demos/images/spacer.gif" width="6" height="16" alt=""></td></tr></table>
		</cfif>
		</td></tr>
	</cfloop>
	</table>
	<table border="0" cellpadding="0" cellspacing="0" width="190" bgcolor="##663300"><tr><td height="6"><img src="/demos/images/spacer.gif" width="1" height="6" alt=""></td></tr></table>
	<font face="Arial, Helvetica" size="3"><b>Peg #ListGetAt(pegNames, p)#</b></font>
	</td>
</cfloop>
</tr>
</table>

<p>
<font face="Arial, Helvetica" size="3">
<cfif step IS 0>
	Start position: #disks# disks on peg A. Goal: move them all to peg C.
<cfelse>
	<cfset mv = Request.hanoiMoves[step]>
	Move <b>#step#</b> of #total#: disk #ListGetAt(mv, 1)# from peg #ListGetAt(pegNames, ListGetAt(mv, 2))# to peg #ListGetAt(pegNames, ListGetAt(mv, 3))#
</cfif>
<cfif step IS total><br><font color="##009900"><b>Solved in #total# moves - the minimum possible (2<sup>#disks#</sup> - 1).</b></font></cfif>
</font>
<p>
<font face="Arial, Helvetica" size="2">
<a href="hanoi.cfm?disks=#disks#&step=0">|&lt; Start</a> &nbsp;
<cfif step GT 0><a href="hanoi.cfm?disks=#disks#&step=#step - 1#">&lt; Back</a><cfelse>&lt; Back</cfif> &nbsp;
<cfif step LT total><a href="hanoi.cfm?disks=#disks#&step=#step + 1#">Next &gt;</a><cfelse>Next &gt;</cfif> &nbsp;
<a href="hanoi.cfm?disks=#disks#&step=#total#">End &gt;|</a> &nbsp;
<cfif auto><a href="hanoi.cfm?disks=#disks#&step=#step#"><b>Stop</b></a><cfelse><a href="hanoi.cfm?disks=#disks#&step=#step#&auto=1"><b>Play</b></a></cfif>
<br><br>
Disks:
<cfloop from="1" to="8" index="n">
	<cfif n IS disks><b>[#n#]</b><cfelse><a href="hanoi.cfm?disks=#n#">#n#</a></cfif>
</cfloop>
</font>
<p>
<table border="0"><tr><td>
<font face="Courier New, Courier" size="2">
<b>All #total# moves:</b><br>
<cfloop from="1" to="#total#" index="m">
	<cfset mv = Request.hanoiMoves[m]>
	<cfif m IS step><font color="##CC0000"><b></cfif>#NumberFormat(m, "000")#. disk #ListGetAt(mv, 1)#: #ListGetAt(pegNames, ListGetAt(mv, 2))# -&gt; #ListGetAt(pegNames, ListGetAt(mv, 3))#<cfif m IS step></b></font></cfif><cfif m MOD 4 IS 0><br><cfelse> &nbsp; &nbsp; </cfif>
</cfloop>
</font>
</td></tr></table>
</cfoutput>
</center>
<cfinclude template="_footer.cfm">
</body>
</html>
