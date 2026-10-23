<!--- Map: prints the entire security framework --->
<cfregistry action="getall" branch="#Request.reg#\Security\UserDirectories" name="dirs" type="key">
<cfregistry action="getall" branch="#Request.reg#\Security\Contexts" name="ctxs" type="key">
<cfset pageTitle = "Security Map">
<cfinclude template="../_header.cfm">
<cfoutput>
<PRE>
Advanced Security
|
+-- User Directories
<cfloop query="dirs">|   +-- #dirs.Entry#
<cfregistry action="getall" branch="#Request.reg#\Security\UserDirectories\#dirs.Entry#\Users" name="u" type="key"><cfloop query="u">|   |   +-- user #u.Entry#
</cfloop></cfloop>|
+-- Security Contexts
<cfloop query="ctxs">    +-- #ctxs.Entry#
<cfregistry action="getall" branch="#Request.reg#\Security\Contexts\#ctxs.Entry#\Rules" name="r" type="key"><cfloop query="r">    |   +-- rule #r.Entry#
</cfloop><cfregistry action="getall" branch="#Request.reg#\Security\Contexts\#ctxs.Entry#\Policies" name="p" type="key"><cfloop query="p">    |   +-- policy #p.Entry#
</cfloop></cfloop></PRE>
<FORM><INPUT TYPE="button" VALUE="Print" onClick="window.print()"> <INPUT TYPE="button" VALUE="Back" onClick="location='advancedsecurity.cfm'"></FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
