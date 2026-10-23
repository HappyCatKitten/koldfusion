<!---
  viewsource.cfm - shows the source of any text file under /demos/ with
  HTMLCodeFormat(). ?file= is a path relative to /demos/ (e.g.
  rosettacode/fizzbuzz.cfm). Anything that could leave the /demos/ directory
  (absolute paths, drive letters, "..", backslashes, odd characters) is refused,
  as is any file type that is not plain text.
  Part of the KoldFusion Demo Gallery - MIT licence.
--->
<cfparam name="URL.file" default="">
<cfparam name="URL.lines" default="0">
<cfset demoRoot = GetDirectoryFromPath(GetCurrentTemplatePath())>
<cfset file = Trim(URL.file)>
<cfset problem = "">
<cfset textTypes = "cfm,cfml,txt,css,js,htm,html,sql,xml,wddx">

<cfif NOT Len(file)>
	<cfset problem = "No file was given.">
<cfelseif Find("..", file) OR Find("\", file) OR Find(":", file) OR Find("//", file) OR Left(file, 1) IS "/" OR Left(file, 1) IS ".">
	<cfset problem = "That path points outside the Demo Gallery.">
<cfelseif REFind("[^A-Za-z0-9_./-]", file)>
	<cfset problem = "That file name contains characters the gallery does not allow.">
<cfelseif NOT ListFindNoCase(textTypes, ListLast(GetFileFromPath(file), "."))>
	<cfset problem = "Only text files (#textTypes#) can be viewed.">
<cfelseif NOT FileExists(demoRoot & file)>
	<cfset problem = "There is no such file in the Demo Gallery.">
</cfif>

<cfif Len(problem)>
	<cfheader statuscode="404" statustext="Not Found">
<cfelse>
	<cffile action="read" file="#demoRoot##file#" variable="source">
	<cfset lineCount = ListLen(source, Chr(10)) >
	<cfif URL.lines IS 1>
		<!--- prefix line numbers; walk the text line by line so blank lines keep their number --->
		<cfset numbered = "">
		<cfset rest = Replace(source, Chr(13), "", "ALL")>
		<cfset n = 0>
		<cfloop condition="Len(rest) GT 0">
			<cfset n = n + 1>
			<cfset nl = Find(Chr(10), rest)>
			<cfif nl IS 0>
				<cfset line = rest>
				<cfset rest = "">
			<cfelse>
				<cfset line = Left(rest, nl - 1)>
				<cfset rest = RemoveChars(rest, 1, nl)>
			</cfif>
			<cfset numbered = numbered & RJustify(n, 4) & ": " & line & Chr(10)>
		</cfloop>
		<cfset lineCount = n>
		<cfset shown = numbered>
	<cfelse>
		<cfset shown = source>
	</cfif>
</cfif>

<html>
<head>
<title>View Source<cfif NOT Len(problem)>: <cfoutput>#HTMLEditFormat(file)#</cfoutput></cfif></title>
</head>
<body bgcolor="#FFFFFF" background="/images/bg_tile.gif" link="#0000FF" vlink="#663399">
<table width="100%" border="0" cellpadding="8" cellspacing="0" bgcolor="#FFFFFF">
<tr><td bgcolor="#000080">
	<font face="Arial, Helvetica" size="4" color="#FFFFFF"><b>View Source</b></font>
	<cfif NOT Len(problem)><font face="Courier New, Courier" size="3" color="#FFFF00"><b><cfoutput>/demos/#HTMLEditFormat(file)#</cfoutput></b></font></cfif>
</td></tr>
<tr><td>
<font face="Arial, Helvetica" size="2">
<a href="index.cfm">&lt;&lt; Back to the Demo Gallery</a>
<cfif NOT Len(problem)>
	<cfoutput>
	<cfset folder = ListFirst(file, "/")>
	<cfif ListLen(file, "/") GT 1 AND FileExists(demoRoot & folder & "/SOURCE.txt") AND file IS NOT folder & "/SOURCE.txt">
		| <a href="viewsource.cfm?file=#URLEncodedFormat(folder & '/SOURCE.txt')#">Credits and licence (SOURCE.txt)</a>
	</cfif>
	<cfif ListFindNoCase("cfm,cfml,htm,html,txt,css", ListLast(file, "."))>
		| <a href="#file#">Open it</a>
	</cfif>
	| <cfif URL.lines IS 1><a href="viewsource.cfm?file=#URLEncodedFormat(file)#">Hide line numbers</a><cfelse><a href="viewsource.cfm?file=#URLEncodedFormat(file)#&lines=1">Show line numbers</a></cfif>
	<br>#NumberFormat(Len(source), "9,999")# bytes, #lineCount# lines
	</cfoutput>
</cfif>
</font>
</td></tr>
<tr><td>
<cfif Len(problem)>
	<p><font face="Arial, Helvetica" size="3" color="#CC0000"><b><cfoutput>#problem#</cfoutput></b></font></p>
	<p><font face="Arial, Helvetica" size="2">Ask for a path relative to /demos/, for example
	<a href="viewsource.cfm?file=rosettacode/fizzbuzz.cfm">viewsource.cfm?file=rosettacode/fizzbuzz.cfm</a>.</font></p>
<cfelse>
	<cfoutput>#HTMLCodeFormat(shown)#</cfoutput>
</cfif>
</td></tr>
</table>
</body>
</html>
