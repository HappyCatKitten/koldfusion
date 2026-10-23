<cfsetting enablecfoutputonly="yes">
<cfcontent type="text/plain">
<cfparam name="Form.FieldNames" default="">
<cfoutput>method=#CGI.REQUEST_METHOD#
length=#CGI.CONTENT_LENGTH#
fields=#Form.FieldNames#
</cfoutput>
<cfloop list="#Form.FieldNames#" index="f"><cfoutput>#f#=#Form[f]#
</cfoutput></cfloop>
