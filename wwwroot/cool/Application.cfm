<cfapplication name="CoolStuff" sessionmanagement="yes">
<cflock scope="application" type="exclusive" timeout="10">
	<cfparam name="Application.counter" default="1999">
	<cfif NOT IsDefined("Session.counted")>
		<cfset Application.counter = Application.counter + 1>
	</cfif>
	<cfset Request.counter = Application.counter>
</cflock>
<cfset Session.counted = true>
