<!---
  tictactoe.cfm - Tic-Tac-Toe against the server. You are X and move first;
  the computer (O) wins if it can, blocks if it must, and otherwise prefers
  the centre, then a corner, then a side. Board and score live in SESSION.
  KoldFusion Demo Gallery original - MIT licence.
--->
<cfset lines = "1,2,3|4,5,6|7,8,9|1,4,7|2,5,8|3,6,9|1,5,9|3,5,7">
<cfparam name="URL.sq" default="0">
<cfparam name="URL.action" default="">

<cflock scope="session" type="exclusive" timeout="10">
	<cfif NOT IsDefined("session.ttt") OR URL.action IS "new">
		<cfif NOT IsDefined("session.ttt")>
			<cfset session.ttt = StructNew()>
			<cfset session.ttt.won = 0>
			<cfset session.ttt.lost = 0>
			<cfset session.ttt.drawn = 0>
		</cfif>
		<cfset session.ttt.board = "---------">
		<cfset session.ttt.over = false>
		<cfset session.ttt.message = "Your move. You are X.">
	</cfif>
	<cfset game = Duplicate(session.ttt)>
</cflock>

<!--- the human moves --->
<cfif NOT game.over AND IsNumeric(URL.sq) AND URL.sq GTE 1 AND URL.sq LTE 9 AND Mid(game.board, URL.sq, 1) IS "-">
	<cfset game.board = Left(game.board, URL.sq - 1) & "X" & Right(game.board, 9 - URL.sq)>

	<!--- did X just win? --->
	<cfset winner = "">
	<cfloop list="#lines#" index="line" delimiters="|">
		<cfif Mid(game.board, ListGetAt(line, 1), 1) IS "X" AND Mid(game.board, ListGetAt(line, 2), 1) IS "X" AND Mid(game.board, ListGetAt(line, 3), 1) IS "X">
			<cfset winner = "X"><cfset winLine = line>
		</cfif>
	</cfloop>

	<cfif winner IS "X">
		<cfset game.over = true>
		<cfset game.won = game.won + 1>
		<cfset game.message = "You win! The server is speechless.">
	<cfelseif Find("-", game.board) IS 0>
		<cfset game.over = true>
		<cfset game.drawn = game.drawn + 1>
		<cfset game.message = "Cat's game - a draw.">
	<cfelse>
		<!--- the computer thinks: first try to win (O), then to block (X) --->
		<cfset move = 0>
		<cfloop list="O,X" index="who">
			<cfif move IS 0>
				<cfloop list="#lines#" index="line" delimiters="|">
					<cfset mine = 0><cfset empty = 0>
					<cfloop list="#line#" index="sq">
						<cfif Mid(game.board, sq, 1) IS who><cfset mine = mine + 1></cfif>
						<cfif Mid(game.board, sq, 1) IS "-"><cfset empty = sq></cfif>
					</cfloop>
					<cfif mine IS 2 AND empty GT 0 AND move IS 0>
						<cfset move = empty>
					</cfif>
				</cfloop>
			</cfif>
		</cfloop>
		<!--- otherwise centre, a random free corner, a random free side --->
		<cfif move IS 0 AND Mid(game.board, 5, 1) IS "-"><cfset move = 5></cfif>
		<cfloop list="1;3;7;9|2;4;6;8" index="group" delimiters="|">
			<cfif move IS 0>
				<cfset free = "">
				<cfloop list="#group#" index="sq" delimiters=";">
					<cfif Mid(game.board, sq, 1) IS "-"><cfset free = ListAppend(free, sq)></cfif>
				</cfloop>
				<cfif ListLen(free)><cfset move = ListGetAt(free, RandRange(1, ListLen(free)))></cfif>
			</cfif>
		</cfloop>

		<cfset game.board = Left(game.board, move - 1) & "O" & Right(game.board, 9 - move)>
		<cfset winner = "">
		<cfloop list="#lines#" index="line" delimiters="|">
			<cfif Mid(game.board, ListGetAt(line, 1), 1) IS "O" AND Mid(game.board, ListGetAt(line, 2), 1) IS "O" AND Mid(game.board, ListGetAt(line, 3), 1) IS "O">
				<cfset winner = "O"><cfset winLine = line>
			</cfif>
		</cfloop>
		<cfif winner IS "O">
			<cfset game.over = true>
			<cfset game.lost = game.lost + 1>
			<cfset game.message = "The server wins. Resistance is futile.">
		<cfelseif Find("-", game.board) IS 0>
			<cfset game.over = true>
			<cfset game.drawn = game.drawn + 1>
			<cfset game.message = "Cat's game - a draw.">
		<cfelse>
			<cfset game.message = "I took square #move#. Your move.">
		</cfif>
	</cfif>
</cfif>
<cfparam name="winLine" default="">

<cflock scope="session" type="exclusive" timeout="10">
	<cfset session.ttt = Duplicate(game)>
</cflock>

<html>
<head>
<title>Tic-Tac-Toe vs. the Server</title>
</head>
<body bgcolor="#FFFFCC" background="/images/bg_tile.gif">
<center>
<table border="4" cellpadding="10" bgcolor="#FFFFFF"><tr><td align="center">
<font face="Comic Sans MS, Arial" size="5" color="#990000"><b>Tic-Tac-Toe vs. the Server</b></font>
<p>
<cfoutput>
<table border="0" cellpadding="0" cellspacing="4" bgcolor="##000000">
<cfloop from="0" to="2" index="r">
	<tr>
	<cfloop from="1" to="3" index="c">
		<cfset sq = r * 3 + c>
		<cfset mark = Mid(game.board, sq, 1)>
		<td width="70" height="70" align="center" valign="middle" bgcolor="###IIf(ListFind(winLine, sq), DE('FFFF66'), DE('FFFFFF'))#">
		<cfif mark IS "X">
			<font face="Arial Black, Arial" size="7" color="##0000CC"><b>X</b></font>
		<cfelseif mark IS "O">
			<font face="Arial Black, Arial" size="7" color="##CC0000"><b>O</b></font>
		<cfelseif game.over>
			&nbsp;
		<cfelse>
			<a href="tictactoe.cfm?sq=#sq#"><img src="/demos/images/spacer.gif" width="64" height="64" border="0" alt="Play square #sq#"></a>
		</cfif>
		</td>
	</cfloop>
	</tr>
</cfloop>
</table>
<p>
<font face="Arial, Helvetica" size="3"><b>#game.message#</b></font>
<p>
<font face="Arial, Helvetica" size="2">
You: <b>#game.won#</b> &nbsp; Server: <b>#game.lost#</b> &nbsp; Draws: <b>#game.drawn#</b><br>
<a href="tictactoe.cfm?action=new">#IIf(game.over, DE("Play again"), DE("Start over"))#</a>
</font>
</cfoutput>
</td></tr></table>
</center>
<cfinclude template="_footer.cfm">
</body>
</html>
