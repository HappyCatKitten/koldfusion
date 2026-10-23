<cfsetting enablecfoutputonly="yes">
<cfcontent type="text/plain">
<cfparam name="URL.target" default="">
<cfparam name="URL.method" default="GET">
<cfparam name="URL.redirect" default="Yes">
<cfparam name="URL.check" default="Yes">
<cfparam name="URL.proxy" default="">
<cfparam name="URL.proxyport" default="80">
<cfparam name="URL.user" default="">
<cfparam name="URL.port" default="">
<cfparam name="URL.resolve" default="No">
<cfparam name="URL.throw" default="No">
<cfparam name="URL.timeout" default="10">
<cftry>
<cfif Len(URL.port)>
<cfhttp url="#URL.target#" method="#URL.method#" port="#URL.port#" timeout="#URL.timeout#" redirect="#URL.redirect#" checkcertificate="#URL.check#" username="#URL.user#" password="secret" resolveurl="#URL.resolve#" throwonerror="#URL.throw#">
<cfhttpparam type="formfield" name="greeting" value="hello there">
</cfhttp>
<cfelseif Len(URL.proxy)>
<cfhttp url="#URL.target#" method="#URL.method#" timeout="#URL.timeout#" proxyserver="#URL.proxy#" proxyport="#URL.proxyport#" redirect="#URL.redirect#" checkcertificate="#URL.check#" throwonerror="#URL.throw#">
<cfhttpparam type="formfield" name="greeting" value="hello there">
</cfhttp>
<cfelse>
<cfhttp url="#URL.target#" method="#URL.method#" timeout="#URL.timeout#" redirect="#URL.redirect#" checkcertificate="#URL.check#" username="#URL.user#" password="secret" resolveurl="#URL.resolve#" throwonerror="#URL.throw#">
<cfhttpparam type="formfield" name="greeting" value="hello there">
</cfhttp>
</cfif>
<cfoutput>status=#CFHTTP.StatusCode#
mime=#CFHTTP.MimeType#
<cfif StructKeyExists(CFHTTP.ResponseHeader, "Location")>location=#CFHTTP.ResponseHeader.Location#
</cfif>length=#Len(CFHTTP.FileContent)#
content=#CFHTTP.FileContent#
</cfoutput>
<cfcatch type="Any"><cfoutput>error=#CFCATCH.Message# #CFCATCH.Detail#
</cfoutput></cfcatch>
</cftry>
