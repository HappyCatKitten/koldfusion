<!--- Caching (new in 4.5) --->
<cfset msg = "">
<cfif IsDefined("Form.Apply")>
	<cfif IsNumeric(Form.TemplateCacheSize) AND IsNumeric(Form.DBConnectionInactiveTime) AND IsNumeric(Form.MaxCachedQueries)>
		<cfif Form.MaxCachedQueries GT 100><cfset Form.MaxCachedQueries = 100></cfif>
		<cfloop list="TemplateCacheSize,DBConnectionInactiveTime,MaxCachedQueries" index="f">
			<cfmodule template="../_tags/setreg.cfm" key="Server" entry="#f#" value="#Trim(Form[f])#">
		</cfloop>
		<cfmodule template="../_tags/setreg.cfm" key="Server" entry="TrustedCache" value="#IIf(IsDefined('Form.TrustedCache'), 1, 0)#">
		<cfset msg = "The caching settings have been applied.">
	<cfelse>
		<cfset msg = "All caching values must be numeric.">
	</cfif>
</cfif>
<cfif IsDefined("Form.FlushTemplates")><cfset KFUSION_FLUSHCACHE("template")><cfset msg = "The template cache has been cleared."></cfif>
<cfif IsDefined("Form.FlushQueries")><cfset KFUSION_FLUSHCACHE("query")><cfset msg = "All cached queries have been discarded."></cfif>
<cfmodule template="../_tags/getreg.cfm" key="Server" variable="S">
<cfset info = KFUSION_SERVERINFO()>
<cfset pageTitle = "Caching">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="caching.cfm" METHOD="POST">
<P>#Request.f#<B>Template cache size</B> <INPUT TYPE="text" NAME="TemplateCacheSize" VALUE="#S.TemplateCacheSize#" SIZE=6> <B>kilobytes</B><BR>
The maximum amount of memory used to cache compiled templates. Memory is allocated as needed, not reserved in advance;
ideally set this a little above the total size of all your templates.
<I>(Currently #info.CachedTemplates# templates, #NumberFormat(info.CachedTemplateBytes / 1024, "9.9")# KB.)</I></FONT>

<P>#Request.f#<INPUT TYPE="checkbox" NAME="TrustedCache" VALUE="1"<cfif S.TrustedCache EQ 1> CHECKED</cfif>>
<B>Trusted cache</B><BR>
When checked, cached templates are served without checking whether the template file has changed on disk. Use this on stable
production sites; leave it off while you are developing.</FONT>

<P>#Request.f#<B>Limit database connection inactive time to</B> <INPUT TYPE="text" NAME="DBConnectionInactiveTime" VALUE="#S.DBConnectionInactiveTime#" SIZE=4> <B>minutes</B><BR>
Pooled database connections are closed after being idle for this long. Applies only to data sources with
"Maintain database connections" enabled.</FONT>

<P>#Request.f#<B>Limit the maximum number of cached queries on the server to</B> <INPUT TYPE="text" NAME="MaxCachedQueries" VALUE="#S.MaxCachedQueries#" SIZE=4> <B>queries</B><BR>
When the limit is exceeded the oldest cached query is dropped. The maximum number of cached queries allowed at any given time is 100.
<I>(Currently #info.CachedQueries# cached.)</I></FONT>

<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Apply" VALUE="Apply"> <INPUT TYPE="reset" VALUE="Cancel">
&nbsp;&nbsp;<INPUT TYPE="submit" NAME="FlushTemplates" VALUE="Clear Template Cache"> <INPUT TYPE="submit" NAME="FlushQueries" VALUE="Clear Query Cache">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
