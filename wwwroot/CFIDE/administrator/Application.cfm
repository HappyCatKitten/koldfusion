<!--- KoldFusion Administrator: application framework and password check --->
<cfapplication name="KFAdministrator" sessionmanagement="no" clientmanagement="no">
<cfset Request.reg = "HKEY_LOCAL_MACHINE\SOFTWARE\Allair\KoldFusion\CurrentVersion">
<cfset Request.f = "<FONT FACE=""Arial, Helvetica"" SIZE=""2"">">
<cfset Request.adm = "/CFIDE/administrator">
<cfsetting showdebugoutput="no">
<cfregistry action="get" branch="#Request.reg#\Server" entry="UseAdminPassword" variable="Request.useAdminPw">
<cfregistry action="get" branch="#Request.reg#\Server" entry="AdminPassword" variable="Request.adminPw">
<cfset Request.authToken = Hash(KFUSION_DECRYPT(Request.adminPw) & "#Request.reg#")>
<cfif Request.useAdminPw EQ "1" AND GetFileFromPath(GetBaseTemplatePath()) NEQ "login.cfm">
	<cfif NOT IsDefined("Cookie.CFADMIN_AUTH") OR Cookie.CFADMIN_AUTH NEQ Request.authToken>
		<cfset wanted = ReplaceNoCase(CGI.SCRIPT_NAME, "/CFIDE/administrator/", "")>
		<cfif wanted EQ "index.cfm" OR wanted EQ "navigation.cfm"><cfset wanted = ""></cfif>
		<cflocation url="/CFIDE/administrator/login.cfm?page=#URLEncodedFormat(wanted)#" addtoken="no">
	</cfif>
</cfif>
