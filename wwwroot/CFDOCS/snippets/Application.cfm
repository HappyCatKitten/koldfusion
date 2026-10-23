<!--- 
	/CFDOCS/snippets/Application.cfm
	The Language Reference examples run real CFML on this server (files, mail,
	the registry...), so like the 1999 original they only answer to the machine
	the server runs on. The launcher list and the "sorry" page are public.
--->
<cfset Request.snippetsLocal = ListFind("127.0.0.1,::1", CGI.REMOTE_ADDR) GT 0>
<cfif NOT Request.snippetsLocal
	AND NOT ListFindNoCase("index.cfm,sorry.cfm", GetFileFromPath(GetBaseTemplatePath()))>
	<cfinclude template="sorry.cfm">
	<cfabort>
</cfif>
