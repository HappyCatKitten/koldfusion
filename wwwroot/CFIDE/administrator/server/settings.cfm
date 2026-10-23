<!--- Server Settings --->
<cfset msg = "">
<cfif IsDefined("Form.Apply")>
	<cfset ok = IsNumeric(Form.LimitSimultaneousRequests) AND IsNumeric(Form.RequestTimeout) AND IsNumeric(Form.RestartAt)>
	<cfif ok>
		<cfloop list="LimitSimultaneousRequests,RequestTimeout,RestartAt,MissingTemplateHandler,SiteWideErrorHandler" index="f">
			<cfmodule template="../_tags/setreg.cfm" key="Server" entry="#f#" value="#Trim(Form[f])#">
		</cfloop>
		<cfloop list="TimeoutRequests,RestartUnresponsive,RestartAbnormal,StrictAttributeValidation,SuppressWhitespace" index="f">
			<cfmodule template="../_tags/setreg.cfm" key="Server" entry="#f#" value="#IIf(IsDefined('Form.' & f), 1, 0)#">
		</cfloop>
		<cfset msg = "The server settings have been applied. Changes to the request limit take effect when the KoldFusion Application Server is restarted.">
	<cfelse>
		<cfset msg = "The request limit, timeout and restart values must be numeric.">
	</cfif>
</cfif>
<cfif IsDefined("Form.Restart")>
	<cfset KFUSION_RESTART()>
	<cfset msg = "The KoldFusion Application Server is restarting. Please wait a few seconds and reload this page.">
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="Server" variable="S">
<cfset pageTitle = "Server Settings">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="settings.cfm" METHOD="POST">
<P>#Request.f#<B>Limit simultaneous requests to</B> <INPUT TYPE="text" NAME="LimitSimultaneousRequests" VALUE="#S.LimitSimultaneousRequests#" SIZE=3><BR>
Limiting the number of simultaneously processed requests increases overall system performance. Requests beyond the limit are queued.
The KoldFusion Application Server must be restarted for this setting to go into effect.</FONT>

<P>#Request.f#<INPUT TYPE="checkbox" NAME="TimeoutRequests" VALUE="1"<cfif S.TimeoutRequests EQ 1> CHECKED</cfif>>
<B>Timeout requests after</B> <INPUT TYPE="text" NAME="RequestTimeout" VALUE="#S.RequestTimeout#" SIZE=3> <B>seconds</B><BR>
Requests that take longer than the timeout will be terminated. This prevents unusually long requests from tying up server resources
and negatively impacting the performance of other requests.</FONT>

<P>#Request.f#<INPUT TYPE="checkbox" NAME="RestartUnresponsive" VALUE="1"<cfif S.RestartUnresponsive EQ 1> CHECKED</cfif>>
<B>Restart at</B> <INPUT TYPE="text" NAME="RestartAt" VALUE="#S.RestartAt#" SIZE=3> <B>unresponsive requests</B><BR>
By enabling this option the engine will track requests that execute component code (e.g., a database driver, a third-party CFX, etc.)
but fail to return in a timely fashion. The service is restarted when the specified number of request threads do not respond in the
allotted time. Requests are tracked only if a request timeout is enabled. The restart threshold will not exceed the request limit.</FONT>

<P>#Request.f#<INPUT TYPE="checkbox" NAME="RestartAbnormal" VALUE="1"<cfif S.RestartAbnormal EQ 1> CHECKED</cfif>>
<B>Restart when requests terminate abnormally</B><BR>
When enabled, the server tracks the ratio of successful requests and restarts itself if too many requests end with an unexpected
internal error.</FONT>

<P>#Request.f#<INPUT TYPE="checkbox" NAME="StrictAttributeValidation" VALUE="1"<cfif S.StrictAttributeValidation EQ 1> CHECKED</cfif>>
<B>Enforce strict attribute validation</B><BR>
In strict mode the engine rejects tags that contain extraneous or invalid attributes, which also improves performance.</FONT>

<P>#Request.f#<INPUT TYPE="checkbox" NAME="SuppressWhitespace" VALUE="1"<cfif S.SuppressWhitespace EQ 1> CHECKED</cfif>>
<B>Suppress whitespace by default</B><BR>
When checked, the engine will compress runs of spaces, tabs, and carriage return/linefeeds into a single space.
Individual templates can override this with the CFPROCESSINGDIRECTIVE tag.</FONT>

<P>#Request.f#<B>Missing Template Handler</B><BR>
<INPUT TYPE="text" NAME="MissingTemplateHandler" VALUE="#HTMLEditFormat(S.MissingTemplateHandler)#" SIZE=50><BR>
The template to execute when a requested template cannot be found.</FONT>

<P>#Request.f#<B>Site-wide Error Handler</B><BR>
<INPUT TYPE="text" NAME="SiteWideErrorHandler" VALUE="#HTMLEditFormat(S.SiteWideErrorHandler)#" SIZE=50><BR>
The template to execute when an error occurs while processing a request. It behaves like
&lt;CFERROR TYPE="EXCEPTION" EXCEPTION="ANY"&gt; in every application.</FONT>

<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Apply" VALUE="Apply"> <INPUT TYPE="reset" VALUE="Cancel">
&nbsp;&nbsp;&nbsp;&nbsp;<INPUT TYPE="submit" NAME="Restart" VALUE="Restart Server..." onClick="return confirm('Restart the KoldFusion Application Server now?')">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
