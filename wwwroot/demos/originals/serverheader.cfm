<!---
  serverheader.cfm - "What's my server header?" The page uses CFHTTP to fetch
  a page from this very server (loopback, same port) and shows the status line,
  the Server: header and every other response header the server sent back.
  Only paths on this server are allowed. KoldFusion Demo Gallery original - MIT licence.
--->
<cfparam name="URL.path" default="/">
<cfset path = Trim(URL.path)>
<!--- only local paths: must start with "/", no "//", no spaces or control characters --->
<cfif Left(path, 1) IS NOT "/" OR Find("//", path) OR REFind("[[:space:][:cntrl:]]", path)>
	<cfset path = "/">
</cfif>
<cfset target = "#IIf(CGI.HTTPS IS 'on', DE('https'), DE('http'))#://127.0.0.1:#CGI.SERVER_PORT##path#">

<cfset started = GetTickCount()>
<cfhttp url="#target#" method="GET" resolveurl="No" timeout="15" throwonerror="No"></cfhttp>
<cfset elapsed = GetTickCount() - started>

<html>
<head>
<title>What's My Server Header?</title>
</head>
<body bgcolor="#000000" text="#00FF00" link="#FFFF00" vlink="#FFFF00">
<center>
<font face="Courier New, Courier" size="5"><b>&gt; WHAT'S MY SERVER HEADER?_</b></font>
<p>
<table border="1" cellpadding="8" cellspacing="0" bordercolor="#00FF00" width="620"><tr><td>
<font face="Courier New, Courier" size="2">
<cfoutput>
C:\&gt; CFHTTP GET #HTMLEditFormat(target)#<br>
<br>
<cfif IsDefined("CFHTTP.StatusCode") AND Len(CFHTTP.StatusCode)>
	HTTP status ..... <b>#HTMLEditFormat(CFHTTP.StatusCode)#</b><br>
</cfif>
<cfif IsDefined("CFHTTP.ResponseHeader") AND IsStruct(CFHTTP.ResponseHeader) AND StructKeyExists(CFHTTP.ResponseHeader, "Server")>
	Server says ..... <font size="4" color="##FFFFFF"><b>#HTMLEditFormat(CFHTTP.ResponseHeader.Server)#</b></font><br>
<cfelse>
	Server says ..... <b>(no Server: header received)</b><br>
</cfif>
MIME type ....... #HTMLEditFormat(CFHTTP.MimeType)#<br>
Body ............ #NumberFormat(Len(CFHTTP.FileContent), "9,999")# bytes in #elapsed# ms<br>
<br>
<cfif IsDefined("CFHTTP.ResponseHeader") AND IsStruct(CFHTTP.ResponseHeader)>
	All response headers:<br>
	<table border="0" cellpadding="1" cellspacing="0">
	<cfloop list="#ListSort(StructKeyList(CFHTTP.ResponseHeader), 'textnocase')#" index="h">
		<cfif IsSimpleValue(CFHTTP.ResponseHeader[h])>
		<tr><td valign="top"><font face="Courier New, Courier" size="2" color="##00CC00">#HTMLEditFormat(h)#:&nbsp;</font></td>
		<td><font face="Courier New, Courier" size="2">#HTMLEditFormat(CFHTTP.ResponseHeader[h])#</font></td></tr>
		</cfif>
	</cfloop>
	</table>
</cfif>
<cfif IsDefined("CFHTTP.Header")>
	<br>Raw header block (CFHTTP.Header):<br>
	<pre>#HTMLEditFormat(CFHTTP.Header)#</pre>
</cfif>
</cfoutput>
</font>
</td></tr></table>
<p>
<form action="serverheader.cfm" method="get">
<font face="Courier New, Courier" size="2">Fetch another path on this server:</font>
<cfoutput><input type="text" name="path" size="40" value="#HTMLEditFormat(path)#"></cfoutput>
<input type="submit" value="CFHTTP it">
</form>
<font face="Courier New, Courier" size="2">
Try: <a href="serverheader.cfm?path=/">/</a> |
<a href="serverheader.cfm?path=/images/new.gif">/images/new.gif</a> |
<a href="serverheader.cfm?path=/demos/originals/SOURCE.txt">a .txt file</a> |
<a href="serverheader.cfm?path=/no/such/page.cfm">a 404</a>
</font>
</center>
<cfinclude template="_footer.cfm">
</body>
</html>
