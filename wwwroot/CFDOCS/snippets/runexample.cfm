<!--- Output frame of the example window: hands over to the snippet itself, so its forms can post back to it --->
<cfinclude template="_validate.cfm">
<cfif Variables.snipRow>
	<cflocation url="/CFDOCS/snippets/#tagname#.cfm" addtoken="No">
</cfif>
<HTML><BODY BGCOLOR="#FFFFFF"><P>No such example.</P></BODY></HTML>
