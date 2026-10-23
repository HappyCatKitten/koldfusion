<!---
  life.cfm - John Conway's Game of Life. The board lives in the SESSION scope
  (one string of 0s and 1s); each click on "Next generation" advances it one
  step on the server. Click a cell to flip it. The board wraps around at the
  edges (a torus). KoldFusion Demo Gallery original - MIT licence.
--->
<cfset rows = 18>
<cfset cols = 30>
<cfset size = rows * cols>
<cfparam name="URL.action" default="">
<cfparam name="URL.cell" default="0">

<cflock scope="session" type="exclusive" timeout="10">
<cfif NOT IsDefined("session.lifeBoard") OR Len(session.lifeBoard) IS NOT size OR URL.action IS "glider">
	<!--- a glider gun's worth of fun: a glider plus a blinker and a "toad" --->
	<cfset board = RepeatString("0", size)>
	<cfset seed = "2,3|3,4|4,2|4,3|4,4|10,20|10,21|10,22|14,9|14,10|14,11|15,8|15,9|15,10">
	<cfloop list="#seed#" index="rc" delimiters="|">
		<cfset i = (ListFirst(rc) - 1) * cols + ListLast(rc)>
		<cfset board = Left(board, i - 1) & "1" & Right(board, size - i)>
	</cfloop>
	<cfset session.lifeBoard = board>
	<cfset session.lifeGeneration = 0>
</cfif>
<cfset board = session.lifeBoard>
<cfset generation = session.lifeGeneration>
</cflock>

<cfset steps = 0>
<cfswitch expression="#URL.action#">
	<cfcase value="clear">
		<cfset board = RepeatString("0", size)>
		<cfset generation = 0>
	</cfcase>
	<cfcase value="random">
		<cfset board = "">
		<cfloop from="1" to="#size#" index="i">
			<cfif RandRange(1, 100) LTE 30><cfset board = board & "1"><cfelse><cfset board = board & "0"></cfif>
		</cfloop>
		<cfset generation = 0>
	</cfcase>
	<cfcase value="flip">
		<cfif IsNumeric(URL.cell) AND URL.cell GTE 1 AND URL.cell LTE size>
			<cfset i = Int(URL.cell)>
			<cfset board = Left(board, i - 1) & IIf(Mid(board, i, 1) IS "1", DE("0"), DE("1")) & Right(board, size - i)>
		</cfif>
	</cfcase>
	<cfcase value="step"><cfset steps = 1></cfcase>
	<cfcase value="step10"><cfset steps = 10></cfcase>
</cfswitch>

<!--- advance the board: count the eight neighbours of every cell --->
<cfloop from="1" to="#steps#" index="s">
	<cfscript>
		next = "";
		for (r = 0; r LT rows; r = r + 1) {
			up = ((r + rows - 1) MOD rows) * cols;
			here = r * cols;
			down = ((r + 1) MOD rows) * cols;
			for (c = 0; c LT cols; c = c + 1) {
				lc = (c + cols - 1) MOD cols;
				rc = (c + 1) MOD cols;
				n = Mid(board, up + lc + 1, 1) + Mid(board, up + c + 1, 1) + Mid(board, up + rc + 1, 1)
				  + Mid(board, here + lc + 1, 1) + Mid(board, here + rc + 1, 1)
				  + Mid(board, down + lc + 1, 1) + Mid(board, down + c + 1, 1) + Mid(board, down + rc + 1, 1);
				alive = Mid(board, here + c + 1, 1);
				if (n EQ 3 OR (n EQ 2 AND alive EQ 1)) next = next & "1";
				else next = next & "0";
			}
		}
		board = next;
		generation = generation + 1;
	</cfscript>
</cfloop>

<cflock scope="session" type="exclusive" timeout="10">
	<cfset session.lifeBoard = board>
	<cfset session.lifeGeneration = generation>
</cflock>

<cfset population = Len(board) - Len(Replace(board, "1", "", "ALL"))>

<html>
<head>
<title>Conway's Game of Life</title>
</head>
<body bgcolor="#003300" background="/images/bg_tile.gif" text="#FFFFFF" link="#CCFF66" vlink="#CCFF66">
<center>
<table border="0" cellpadding="8" bgcolor="#000000"><tr><td align="center">
<font face="Arial, Helvetica" size="5" color="#66FF66"><b>Conway's Game of Life</b></font><br>
<font face="Arial, Helvetica" size="2">One generation per click, computed by the server and kept in your SESSION.</font>
<p>
<cfoutput>
<table border="1" cellpadding="0" cellspacing="0" bordercolor="##336633">
<cfloop from="0" to="#rows - 1#" index="r"><tr><cfloop from="1" to="#cols#" index="c"><cfset i = r * cols + c><cfif Mid(board, i, 1) IS "1"><td bgcolor="##33FF33"><cfelse><td bgcolor="##000000"></cfif><a href="life.cfm?action=flip&cell=#i#"><img src="/demos/images/spacer.gif" width=14 height=14 border=0 alt=""></a></td></cfloop></tr>
</cfloop>
</table>
<p>
<font face="Courier New, Courier" size="3" color="##CCFFCC">GENERATION #NumberFormat(generation, "00000")# &nbsp; POPULATION #NumberFormat(population, "000")#</font>
<p>
<form action="life.cfm" method="get">
<input type="hidden" name="action" value="step">
<input type="submit" value=" Next generation &gt; ">
</form>
<font face="Arial, Helvetica" size="2">
<a href="life.cfm?action=step10">Jump 10 generations</a> |
<a href="life.cfm?action=random">Random soup</a> |
<a href="life.cfm?action=glider">Glider + blinker + toad</a> |
<a href="life.cfm?action=clear">Clear</a>
</font>
</cfoutput>
</td></tr></table>
</center>
<cfinclude template="_footer.cfm">
</body>
</html>
