<!---
  mandelbrot.cfm - the Mandelbrot set, rendered by the server as an HTML table
  (one <TD BGCOLOR> per pixel) or as ASCII art in a <PRE>. Click any cell to
  zoom in on it. KoldFusion Demo Gallery original - MIT licence.
--->
<cfparam name="URL.cx" default="-0.6">
<cfparam name="URL.cy" default="0">
<cfparam name="URL.zoom" default="1">
<cfparam name="URL.mode" default="table">
<cfif NOT IsNumeric(URL.cx)><cfset URL.cx = -0.6></cfif>
<cfif NOT IsNumeric(URL.cy)><cfset URL.cy = 0></cfif>
<cfif NOT IsNumeric(URL.zoom) OR URL.zoom LT 1><cfset URL.zoom = 1></cfif>
<cfif URL.zoom GT 1000000><cfset URL.zoom = 1000000></cfif>
<cfif URL.mode IS NOT "ascii"><cfset URL.mode = "table"></cfif>
<cfparam name="URL.p" default="">

<cfset cols = 64>
<cfset rows = 32>
<cfset maxIter = 40 + Int(Log10(URL.zoom) * 20)>
<!--- the full view is 3.2 units wide; cells are twice as tall as wide (ASCII characters, and 8x16 table cells) --->
<cfset stepX = 3.2 / cols / URL.zoom>
<cfset stepY = stepX * 2>
<cfset left = URL.cx - stepX * cols / 2>
<cfset top = URL.cy + stepY * rows / 2>

<!--- a click on cell "column,row" re-centres on that cell and zooms in 4x --->
<cfif ListLen(URL.p) IS 2 AND IsNumeric(ListFirst(URL.p)) AND IsNumeric(ListLast(URL.p))>
	<cfset URL.cx = left + (ListFirst(URL.p) - 1) * stepX>
	<cfset URL.cy = top - (ListLast(URL.p) - 1) * stepY>
	<cfset URL.zoom = Min(URL.zoom * 4, 1000000)>
	<cfset stepX = 3.2 / cols / URL.zoom>
	<cfset stepY = stepX * 2>
	<cfset left = URL.cx - stepX * cols / 2>
	<cfset top = URL.cy + stepY * rows / 2>
	<cfset maxIter = 40 + Int(Log10(URL.zoom) * 20)>
</cfif>
<cfset base = "mandelbrot.cfm?cx=#URLEncodedFormat(URL.cx)#&cy=#URLEncodedFormat(URL.cy)#&zoom=#URL.zoom#&mode=table&p=">

<cfset palette = "000033,000066,000099,0000CC,0033FF,0066FF,0099FF,00CCFF,00FFFF,33FFCC,66FF99,99FF66,CCFF33,FFFF00,FFCC00,FF9900,FF6600,FF3300,FF0000,CC0033">
<cfset ramp = " .:-=+*##%@">
<cfset rampLen = Len(ramp)>
<cfset paletteLen = ListLen(palette)>

<!--- compute every cell once into a 2D array of iteration counts --->
<cfset tick = GetTickCount()>
<cfset grid = ArrayNew(2)>
<cfscript>
	for (r = 1; r LTE rows; r = r + 1) {
		ci = top - (r - 1) * stepY;
		for (c = 1; c LTE cols; c = c + 1) {
			cr = left + (c - 1) * stepX;
			zr = 0; zi = 0; n = 0;
			while (n LT maxIter AND (zr * zr + zi * zi) LT 4) {
				t = zr * zr - zi * zi + cr;
				zi = 2 * zr * zi + ci;
				zr = t;
				n = n + 1;
			}
			grid[r][c] = n;
		}
	}
</cfscript>
<cfset elapsed = GetTickCount() - tick>

<html>
<head>
<title>Mandelbrot Explorer</title>
</head>
<body background="/images/stars_bg.gif" bgcolor="#000000" text="#FFFFFF" link="#FFFF00" vlink="#FFCC00">
<center>
<font face="Arial, Helvetica" size="5" color="#00FFFF"><b>The KoldFusion Mandelbrot Explorer</b></font><br>
<font face="Arial, Helvetica" size="2">Computed on the <i>server</i>, 100% CFML. Click anywhere to zoom in 4x!</font>
<p>
<cfoutput>
<cfif URL.mode IS "table">
<table border="0" cellpadding="0" cellspacing="0" bgcolor="##000000">
<cfloop from="1" to="#rows#" index="r"><tr><cfloop from="1" to="#cols#" index="c"><cfif grid[r][c] GTE maxIter><cfset color = "000000"><cfelse><cfset color = ListGetAt(palette, (grid[r][c] MOD paletteLen) + 1)></cfif><td bgcolor="###color#"><a href="#base##c#,#r#"><img src="/demos/images/spacer.gif" width=8 height=16 border=0 alt=""></a></td></cfloop></tr>
</cfloop>
</table>
<cfelse>
<table border="2" cellpadding="6" bgcolor="##000000"><tr><td>
<pre><font color="##66FF66"><cfloop from="1" to="#rows#" index="r"><cfloop from="1" to="#cols#" index="c"><cfset n = grid[r][c]><cfif n GTE maxIter>@<cfelse>#Mid(ramp, Int(n * (rampLen - 1) / maxIter) + 1, 1)#</cfif></cfloop>
</cfloop></font></pre>
</td></tr></table>
</cfif>

<p>
<font face="Arial, Helvetica" size="2">
Centre (#NumberFormat(URL.cx, "-9.999999")#, #NumberFormat(URL.cy, "-9.999999")#) &middot;
zoom #URL.zoom#x &middot; #maxIter# iterations &middot; #rows * cols# points in #elapsed# ms
<br>
<a href="mandelbrot.cfm?cx=#URLEncodedFormat(URL.cx)#&cy=#URLEncodedFormat(URL.cy)#&zoom=#URL.zoom#&mode=#IIf(URL.mode IS 'table', DE('ascii'), DE('table'))#">Switch to #IIf(URL.mode IS 'table', DE('ASCII art'), DE('colour table'))#</a> |
<cfif URL.zoom GT 1><a href="mandelbrot.cfm?cx=#URLEncodedFormat(URL.cx)#&cy=#URLEncodedFormat(URL.cy)#&zoom=#Max(1, URL.zoom / 4)#&mode=#URL.mode#">Zoom out</a> |</cfif>
<a href="mandelbrot.cfm?mode=#URL.mode#">Reset</a> |
<a href="mandelbrot.cfm?cx=-0.748&cy=0.1&zoom=16&mode=#URL.mode#">Seahorse Valley</a> |
<a href="mandelbrot.cfm?cx=-1.25&cy=0.02&zoom=16&mode=#URL.mode#">The Antenna</a>
</font>
</cfoutput>
</center>
<cfinclude template="_footer.cfm">
</body>
</html>
