<cfsetting enablecfoutputonly="yes">
<cftry><cfoutput>#nosuchvar#</cfoutput><cfcatch><cfoutput>#cfcatch.Type#:#cfcatch.Message#|</cfoutput></cfcatch></cftry>
<cftry><cfset x = 1 / 0><cfcatch type="Expression"><cfoutput>#cfcatch.Message#|</cfoutput></cfcatch></cftry>
<cftry><cfquery datasource="cfsnippets">SELECT * FROM NoTable</cfquery><cfcatch type="Database"><cfoutput>#cfcatch.Type#|</cfoutput></cfcatch></cftry>
<cftry><cfthrow type="Shop.OutOfStock" message="none left" errorcode="42"><cfcatch type="Shop"><cfoutput>#cfcatch.Type#:#cfcatch.ErrorCode#|</cfoutput></cfcatch></cftry>
<cftry><cftry><cfthrow message="inner"><cfcatch><cfrethrow></cfcatch></cftry><cfcatch><cfoutput>rethrown:#cfcatch.Message#|</cfoutput></cfcatch></cftry>
<cftry><cfset y = ListGetAt("a", 5)><cfcatch><cfoutput>#cfcatch.Message#</cfoutput></cfcatch></cftry>
<cfoutput>
</cfoutput>
