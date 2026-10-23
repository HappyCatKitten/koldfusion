<!---
  /demos/index.cfm - the KoldFusion Demo Gallery ("Cool CFML Scripts Archive").

  Nothing here is hard-coded: every sub-directory of /demos/ that contains a
  SOURCE.txt is a gallery entry.
    SOURCE.txt  - where the scripts came from: "Source:", "Author:", "License:"
                  and "Description:" lines (indented lines continue a field).
    STATUS.txt  - optional, written by whoever tested the scripts on KoldFusion:
                     file | status | note | run
                  status = works, partial, cf5, cfmx, fails, include or shim;
                  run    = another page to open instead ("-" = no Run link).
                  "@title", "@blurb", "@order" and "@new yes" lines describe the folder.
  Any .cfm file found on disk but missing from STATUS.txt is listed as "untested".

  Part of the KoldFusion Demo Gallery - MIT licence.
--->
<cfset demoRoot = GetDirectoryFromPath(GetCurrentTemplatePath())>
<cfset statusWords = "works,partial,cf5,cfmx,fails,include,shim,untested">
<cfset statusLabels = "Works on KoldFusion,Partly works,Needs ColdFusion 5 or later,Needs ColdFusion MX or later,Fails here,Not a page (included file or custom tag),Gallery companion file,Not tested yet">
<cfset textTypes = "txt,css,js,htm,html,sql,xml">

<!--- ============================================== hit counter (Application scope) --->
<cflock scope="application" type="exclusive" timeout="10">
	<cfparam name="Application.galleryHits" default="0">
	<cfparam name="Application.galleryStarted" default="#Now()#">
	<cfset Application.galleryHits = Application.galleryHits + 1>
	<cfset hits = Application.galleryHits>
	<cfset countingSince = Application.galleryStarted>
</cflock>

<!--- ============================================== pass 1: gather every source --->
<cfdirectory action="list" directory="#demoRoot#" name="Folders" sort="name ASC">
<cfset sources = ArrayNew(1)>
<cfset totals = StructNew()>
<cfloop list="#statusWords#" index="w"><cfset totals[w] = 0></cfloop>
<cfset runnable = "">

<cfloop query="Folders">
	<cfif Folders.type IS "Dir" AND Left(Folders.name, 1) IS NOT "." AND Left(Folders.name, 1) IS NOT "_"
		AND FileExists(demoRoot & Folders.name & "/SOURCE.txt")>
		<cfset folder = Folders.name>
		<cfset src = StructNew()>
		<cfset src.folder = folder>
		<cfset src.title = folder>
		<cfset src.blurb = "">
		<cfset src.order = 50>
		<cfset src.isNew = false>
		<cfset src.source = "">
		<cfset src.author = "">
		<cfset src.license = "">
		<cfset src.description = "">

		<!--- SOURCE.txt: "Key: value" lines; indented lines continue the current key --->
		<cffile action="read" file="#demoRoot##folder#/SOURCE.txt" variable="txt">
		<cfset txt = Replace(txt, Chr(13), "", "ALL")>
		<cfset key = "">
		<cfloop list="#txt#" index="line" delimiters="#Chr(10)#">
			<cfif REFind("^[[:space:]]", line)>
				<!--- continuation (only Source and Description keep theirs) --->
				<cfif key IS "description" OR key IS "source">
					<cfset src[key] = src[key] & " " & Trim(line)>
				</cfif>
			<cfelse>
				<cfset key = "">
				<cfset colon = Find(":", line)>
				<cfif colon GT 1>
					<cfset k = LCase(Trim(Left(line, colon - 1)))>
					<cfif k IS "licence"><cfset k = "license"></cfif>
					<cfif ListFind("source,author,license,description", k)>
						<cfset key = k>
						<cfset src[key] = Trim(RemoveChars(line, 1, colon))>
					</cfif>
				</cfif>
			</cfif>
		</cfloop>

		<!--- STATUS.txt: our test results --->
		<cfset src.entries = ArrayNew(1)>
		<cfset listed = "">
		<cfif FileExists(demoRoot & folder & "/STATUS.txt")>
			<cffile action="read" file="#demoRoot##folder#/STATUS.txt" variable="txt">
			<cfset txt = Replace(txt, Chr(13), "", "ALL")>
			<cfloop list="#txt#" index="line" delimiters="#Chr(10)#">
				<cfset line = Trim(line)>
				<cfif Left(line, 1) IS "@">
					<cfset k = LCase(ListFirst(line, " "))>
					<cfset v = Trim(RemoveChars(line, 1, Len(k)))>
					<cfif k IS "@title"><cfset src.title = v>
					<cfelseif k IS "@blurb"><cfset src.blurb = v>
					<cfelseif k IS "@order" AND IsNumeric(v)><cfset src.order = v>
					<cfelseif k IS "@new"><cfset src.isNew = (v IS "yes")>
					</cfif>
				<cfelseif Left(line, 1) IS NOT "##" AND Find("|", line) AND ListLen(line, "|") GTE 2>
					<cfset e = StructNew()>
					<cfset e.file = Trim(ListGetAt(line, 1, "|"))>
					<cfset e.status = LCase(Trim(ListGetAt(line, 2, "|")))>
					<cfset e.note = "">
					<cfset e.run = "">
					<cfif ListLen(line, "|") GTE 3><cfset e.note = Trim(ListGetAt(line, 3, "|"))></cfif>
					<cfif ListLen(line, "|") GTE 4><cfset e.run = Trim(ListGetAt(line, 4, "|"))></cfif>
					<cfif NOT ListFind(statusWords, e.status)><cfset e.status = "untested"></cfif>
					<cfset ArrayAppend(src.entries, e)>
					<cfset listed = ListAppend(listed, LCase(e.file))>
				</cfif>
			</cfloop>
		</cfif>

		<!--- files on disk: unlisted .cfm files are "untested"; text files go under "other files" --->
		<cfdirectory action="list" directory="#demoRoot##folder#" name="Files" sort="name ASC">
		<cfset src.others = "">
		<cfloop query="Files">
			<cfif Files.type IS "File">
				<cfset ext = LCase(ListLast(Files.name, "."))>
				<cfif ext IS "cfm" AND NOT ListFind(listed, LCase(Files.name))>
					<cfset e = StructNew()>
					<cfset e.file = Files.name>
					<cfset e.status = "untested">
					<cfset e.note = "Found on disk; not in STATUS.txt yet">
					<cfset e.run = "">
					<cfset ArrayAppend(src.entries, e)>
				<cfelseif ListFind(textTypes, ext) AND Files.name IS NOT "STATUS.txt">
					<cfset src.others = ListAppend(src.others, Files.name)>
				</cfif>
			</cfif>
		</cfloop>

		<!--- tally the real scripts (not includes and companions) and remember runnable pages --->
		<cfset src.counts = StructNew()>
		<cfloop list="#statusWords#" index="w"><cfset src.counts[w] = 0></cfloop>
		<cfloop from="1" to="#ArrayLen(src.entries)#" index="i">
			<cfset e = src.entries[i]>
			<cfset src.counts[e.status] = src.counts[e.status] + 1>
			<cfset totals[e.status] = totals[e.status] + 1>
			<cfif e.status IS "works" AND e.run IS NOT "-">
				<cfset runnable = ListAppend(runnable, folder & "/" & IIf(Len(e.run), "e.run", "e.file"))>
			</cfif>
		</cfloop>
		<cfset ArrayAppend(sources, src)>
	</cfif>
</cfloop>

<!--- sort by @order, then title (selection order via a sorted list of "order|title|index") --->
<cfset sortKeys = "">
<cfloop from="1" to="#ArrayLen(sources)#" index="i">
	<cfset sortKeys = ListAppend(sortKeys, NumberFormat(sources[i].order, "000") & "|" & Replace(sources[i].title, ",", " ", "ALL") & "|" & i)>
</cfloop>
<cfset sortKeys = ListSort(sortKeys, "textnocase")>

<cfset scriptCount = 0>
<cfloop list="works,partial,cf5,cfmx,fails,untested" index="w"><cfset scriptCount = scriptCount + totals[w]></cfloop>
<cfif Len(runnable)>
	<cfset randomPick = ListGetAt(runnable, RandRange(1, ListLen(runnable)))>
<cfelse>
	<cfset randomPick = "index.cfm">
</cfif>
<cfset hitDigits = NumberFormat(hits, "000000")>

<!--- ============================================== pass 2: the page --->
<html>
<head>
<title>KoldFusion Demo Gallery - The Cool CFML Scripts Archive</title>
<meta name="description" content="The Cool CFML Scripts Archive: open-source ColdFusion scripts running on KoldFusion 4.5">
<meta name="keywords" content="ColdFusion, CFML, KoldFusion, scripts, free, cool, webring, Y2K">
<script language="JavaScript">
<!--
function ws(msg) { window.status = msg; return true; }
// -->
</script>
</head>
<body background="/images/bg_tile.gif" bgcolor="#C0C0C0" text="#000000" link="#0000FF" vlink="#800080" alink="#FF0000">
<center>

<!-- =============================== masthead =============================== -->
<table width="720" border="0" cellpadding="0" cellspacing="0">
<tr><td align="center">
	<img src="/images/kf_welcome.gif" width="468" height="60" alt="Welcome to KoldFusion"><br>
	<font face="Arial Black, Arial, Helvetica" size="6" color="#000080"><b>The Cool CFML Scripts Archive</b></font><br>
	<font face="Arial, Helvetica" size="2"><b>The KoldFusion Demo Gallery</b> &middot; free ColdFusion scripts from all over the 'Net, tested on KoldFusion 4.5</font>
</td></tr>
</table>
<p>
<img src="/images/rainbow_hr.gif" width="500" height="6" alt="------">
<p>

<table width="720" border="2" cellpadding="10" cellspacing="0" bgcolor="#FFFFFF"><tr><td>
<marquee bgcolor="#FFFFCC" scrollamount="4"><font face="Arial, Helvetica" size="2" color="#CC0000"><b>*** NEW! KoldFusion Originals: Game of Life, Tic-Tac-Toe, Mandelbrot Explorer and the Y2K Compliance Self-Test! *** Every script below has been run on KoldFusion - look for the status badges! *** Sign the guestbook! ***</b></font></marquee>
<p>
<font face="Arial, Helvetica" size="2">
Welcome, surfer! This archive collects <b>real CFML</b> from open-source projects, wikis and tutorials - plus a pile of
brand-new scripts written just for this server. Every script was <b>actually run on KoldFusion</b> and wears a badge
saying how it went. Click <b>Run</b> to try one, or <b>View Source</b> to see how it works.
Each folder's <b>SOURCE.txt</b> credits the original author and licence.
</font>
<cfoutput>
<p>
<table border="0" cellpadding="2" cellspacing="0" width="100%">
<tr>
	<td valign="top"><font face="Arial, Helvetica" size="2">
	<b>#ArrayLen(sources)# collections, #scriptCount# scripts:</b>
	#totals.works# work, #totals.partial# partly work, #totals.cf5 + totals.cfmx# need a newer ColdFusion, #totals.fails# fail
	<cfif totals.untested>, #totals.untested# not tested yet</cfif>
	(plus #totals.include# included files and #totals.shim# gallery companions).
	</font></td>
	<td align="right" valign="top"><font face="Arial, Helvetica" size="2"><a href="#randomPick#" onmouseover="return ws('Surprise me!')"><b>Random script!</b></a></font></td>
</tr>
</table>
<p>
<font face="Arial, Helvetica" size="2"><b>Jump to:</b>
<cfloop list="#sortKeys#" index="sk">
	<cfset src = sources[ListLast(sk, "|")]>
	[<a href="###src.folder#">#src.title#</a><cfif src.isNew>&nbsp;<img src="/images/new.gif" width="44" height="22" align="absmiddle" border="0" alt="NEW!"></cfif>]
</cfloop>
</font>
</cfoutput>
</td></tr></table>

<p>
<!-- =============================== the collections =============================== -->
<cfloop list="#sortKeys#" index="sk">
<cfset src = sources[ListLast(sk, "|")]>
<cfoutput>
<a name="#src.folder#"></a>
<img src="/images/rainbow_hr.gif" width="500" height="6" alt="------">
<p>
<table width="720" border="0" cellpadding="0" cellspacing="0" bgcolor="##000080"><tr><td>
<table width="100%" border="0" cellpadding="6" cellspacing="1">
<tr><td bgcolor="##000080" colspan="3">
	<font face="Arial, Helvetica" size="4" color="##FFFFFF"><b>#HTMLEditFormat(src.title)#</b></font>
	<cfif src.isNew><img src="/images/new.gif" width="44" height="22" align="absmiddle" alt="NEW!"></cfif>
	<font face="Courier New, Courier" size="2" color="##99CCFF">/demos/#src.folder#/</font>
</td></tr>
<tr><td bgcolor="##FFFFEE" colspan="3">
	<cfif Len(src.blurb)><font face="Arial, Helvetica" size="2">#HTMLEditFormat(src.blurb)#</font><br><br></cfif>
	<table border="0" cellpadding="1" cellspacing="0">
	<cfif Len(src.author)><tr><td valign="top"><font face="Arial, Helvetica" size="1"><b>Author:</b>&nbsp;</font></td><td><font face="Arial, Helvetica" size="1">#HTMLEditFormat(src.author)#</font></td></tr></cfif>
	<cfif Len(src.license)><tr><td valign="top"><font face="Arial, Helvetica" size="1"><b>Licence:</b>&nbsp;</font></td><td><font face="Arial, Helvetica" size="1">#REReplaceNoCase(HTMLEditFormat(src.license), "(https?://[^ ;,)]+)", "<a href=""\1"">\1</a>", "ALL")#</font></td></tr></cfif>
	<cfif Len(src.source)><tr><td valign="top"><font face="Arial, Helvetica" size="1"><b>Source:</b>&nbsp;</font></td><td><font face="Arial, Helvetica" size="1">#REReplaceNoCase(HTMLEditFormat(src.source), "(https?://[^ ;,)]+)", "<a href=""\1"">\1</a>", "ALL")#</font></td></tr></cfif>
	<cfif Len(src.description)><tr><td valign="top"><font face="Arial, Helvetica" size="1"><b>About:</b>&nbsp;</font></td><td><font face="Arial, Helvetica" size="1">#HTMLEditFormat(src.description)#</font></td></tr></cfif>
	<tr><td valign="top"><font face="Arial, Helvetica" size="1"><b>Files:</b>&nbsp;</font></td><td><font face="Arial, Helvetica" size="1">
		<a href="viewsource.cfm?file=#URLEncodedFormat(src.folder & '/SOURCE.txt')#">SOURCE.txt</a>
		<cfif FileExists(demoRoot & src.folder & "/STATUS.txt")>&middot; <a href="viewsource.cfm?file=#URLEncodedFormat(src.folder & '/STATUS.txt')#">STATUS.txt</a></cfif>
		<cfloop list="#src.others#" index="o"><cfif o IS NOT "SOURCE.txt">&middot; <a href="viewsource.cfm?file=#URLEncodedFormat(src.folder & '/' & o)#">#o#</a></cfif></cfloop>
	</font></td></tr>
	</table>
</td></tr>
<cfloop from="1" to="#ArrayLen(src.entries)#" index="i">
	<cfset e = src.entries[i]>
	<cfset rowColor = IIf(i MOD 2, DE("FFFFFF"), DE("F0F0FF"))>
	<cfif e.status IS "include" OR e.status IS "shim"><cfset rowColor = "E8E8E8"></cfif>
	<tr>
	<td bgcolor="###rowColor#" width="200" valign="top" nowrap>
		<font face="Courier New, Courier" size="2"><b>#e.file#</b></font>
	</td>
	<td bgcolor="###rowColor#" width="100" valign="top" align="center">
		<img src="images/badge_#e.status#.gif" width="88" height="16" alt="#UCase(e.status)#" title="#ListGetAt(statusLabels, ListFind(statusWords, e.status))#">
	</td>
	<td bgcolor="###rowColor#" valign="top">
		<font face="Arial, Helvetica" size="2">
		<cfif e.run IS NOT "-">
			<cfif Len(e.run)><cfset target = e.run><cfelse><cfset target = e.file></cfif>
			<a href="#src.folder#/#target#" onmouseover="return ws('Run #src.folder#/#target#')"><b>Run</b></a>
			<cfif Len(e.run) AND e.run IS NOT e.file AND ListFind("cf5,cfmx,fails", e.status)>
				&middot; <a href="#src.folder#/#e.file#" onmouseover="return ws('Watch the original fail')">Try&nbsp;original</a>
			</cfif>
			&middot;
		</cfif>
		<a href="viewsource.cfm?file=#URLEncodedFormat(src.folder & '/' & e.file)#" onmouseover="return ws('View the source of #e.file#')">View&nbsp;Source</a>
		<cfif Len(e.note)><br><font size="1" color="##333333">#HTMLEditFormat(e.note)#</font></cfif>
		</font>
	</td>
	</tr>
</cfloop>
</table>
</td></tr></table>
<p>
</cfoutput>
</cfloop>

<!-- =============================== legend, counter, webring =============================== -->
<img src="/images/rainbow_hr.gif" width="500" height="6" alt="------">
<p>
<table width="720" border="2" cellpadding="8" cellspacing="0" bgcolor="#FFFFFF">
<tr><td valign="top" width="50%">
	<font face="Arial, Helvetica" size="2"><b>What the badges mean</b></font><br>
	<table border="0" cellpadding="2" cellspacing="0">
	<cfoutput>
	<cfloop list="#statusWords#" index="w">
		<tr><td><img src="images/badge_#w#.gif" width="88" height="16" alt="#UCase(w)#"></td>
		<td><font face="Arial, Helvetica" size="1">#ListGetAt(statusLabels, ListFind(statusWords, w))#</font></td></tr>
	</cfloop>
	</cfoutput>
	</table>
	<font face="Arial, Helvetica" size="1"><br>
	Corpus files are kept exactly as published. Where a script needed help to run, the gallery adds a
	<b>companion</b> next to it (a runner, an Application.cfm, a shim or a mechanical "_cf45port" copy)
	and says so above.</font>
</td>
<td valign="top" align="center">
	<font face="Arial, Helvetica" size="2"><b>You are visitor number</b></font><br>
	<table border="2" cellpadding="2" cellspacing="0" bgcolor="#000000"><tr><td>
	<cfoutput><cfloop from="1" to="#Len(hitDigits)#" index="i"><img src="/images/digit_#Mid(hitDigits, i, 1)#.gif" width="15" height="20" alt="#Mid(hitDigits, i, 1)#"></cfloop></cfoutput>
	</td></tr></table>
	<font face="Arial, Helvetica" size="1"><cfoutput>since #DateFormat(countingSince, "mmmm d, yyyy")#</cfoutput></font>
	<p>
	<img src="/images/construction.gif" width="140" height="50" alt="Under Construction"><br>
	<font face="Arial, Helvetica" size="1">This archive is <b>always</b> under construction.<br>
	Got a cool CFML script? Drop it in a folder under /demos/ with a SOURCE.txt and it shows up here!</font>
</td></tr>
</table>
<p>
<table border="0" cellpadding="4" cellspacing="0">
<tr><td align="center" colspan="5"><img src="/images/webring.gif" width="300" height="40" alt="The CFML Webring"></td></tr>
<tr><cfoutput>
	<td><font face="Arial, Helvetica" size="2">[<a href="#ListFirst(runnable)#">&lt;&lt; Prev</a>]</font></td>
	<td><font face="Arial, Helvetica" size="2">[<a href="#randomPick#">Random</a>]</font></td>
	<td><font face="Arial, Helvetica" size="2">[<a href="index.cfm">Home</a>]</font></td>
	<td><font face="Arial, Helvetica" size="2">[<a href="originals/guestbook.cfm">Guestbook</a>]</font></td>
	<td><font face="Arial, Helvetica" size="2">[<a href="#ListLast(runnable)#">Next &gt;&gt;</a>]</font></td>
</cfoutput></tr>
</table>
<p>
<a href="/"><img src="/images/powered_by_kf.gif" width="88" height="31" border="0" alt="Powered by KoldFusion"></a>
<img src="/images/netscape_now.gif" width="88" height="31" alt="Netscape Now!">
<img src="/images/ie_parody.gif" width="88" height="31" alt="Best viewed with any browser">
<br>
<font face="Arial, Helvetica" size="1">Best viewed at 800x600 in Netscape Navigator 4 or Internet Explorer 5.<br>
Scripts remain the property of their authors and are used under the licences listed in each SOURCE.txt.<br>
The gallery itself and the KoldFusion Originals are MIT-licensed.
<a href="viewsource.cfm?file=index.cfm">View the source of this page</a>.</font>
</center>
</body>
</html>
