<!--- Shared by the example launcher frames: validates URL.tagname against the snippet catalog --->
<cfparam name="URL.tagname" default="">
<cfinclude template="_catalog.cfm">
<cfset Variables.tagname = LCase(Trim(URL.tagname))>
<cfset Variables.snipRow = 0>
<cfif REFind("^[a-z0-9_]+$", Variables.tagname)>
	<cfloop query="Snippets">
		<cfif Snippets.Name EQ Variables.tagname><cfset Variables.snipRow = Snippets.CurrentRow><cfbreak></cfif>
	</cfloop>
</cfif>
<cfif Variables.snipRow>
	<cfset Variables.snipTitle = Snippets.Title[Variables.snipRow]>
	<cfset Variables.snipKind = Snippets.Kind[Variables.snipRow]>
	<cfset Variables.snipSummary = Snippets.Summary[Variables.snipRow]>
	<cfset Variables.snipCategory = Snippets.Category[Variables.snipRow]>
	<cfset Variables.snipFile = GetDirectoryFromPath(GetCurrentTemplatePath()) & Variables.tagname & ".cfm">
	<cfif NOT FileExists(Variables.snipFile)><cfset Variables.snipRow = 0></cfif>
</cfif>
