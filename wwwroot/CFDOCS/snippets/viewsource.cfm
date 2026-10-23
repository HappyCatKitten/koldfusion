<!--- 
	/CFDOCS/snippets/viewsource.cfm?file=devguide/examples/ch1_hello.cfm
	Shows the source of an example template that lives under /CFDOCS/.
	Only plain relative paths to .cfm files inside an "examples" or "snippets" folder are accepted.
--->
<cfparam name="URL.file" default="">
<cfset Variables.ok = REFind("^[A-Za-z0-9_]+(/[A-Za-z0-9_]+)*\.cfm$", URL.file) GT 0
	AND REFindNoCase("(^|/)(examples|snippets)/", URL.file) GT 0>
<cfset Variables.path = ExpandPath("/CFDOCS/" & URL.file)>
<HTML>
<HEAD><TITLE>Source of <cfoutput>#HTMLEditFormat(URL.file)#</cfoutput></TITLE>
<LINK REL="stylesheet" TYPE="text/css" HREF="/CFDOCS/kfdocs.css"></HEAD>
<BODY BGCOLOR="#FFFFFF">
<cfif Variables.ok AND FileExists(Variables.path)>
	<cffile action="read" file="#Variables.path#" variable="Variables.source">
	<cfoutput><FONT FACE="Verdana, Arial, Helvetica" SIZE=1 COLOR="##666666">/CFDOCS/#HTMLEditFormat(URL.file)#
	&middot; <A HREF="/CFDOCS/#URL.file#">Run it</A></FONT>
	#HTMLCodeFormat(Variables.source)#</cfoutput>
<cfelse>
	<P><IMG SRC="/CFIDE/administrator/images/warn.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
	Sorry, that is not an example file I can show you.</P>
</cfif>
</BODY>
</HTML>
