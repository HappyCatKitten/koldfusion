<!--- Source frame of the example window: the snippet's CFML, HTML-escaped --->
<cfinclude template="_validate.cfm">
<HTML>
<HEAD><TITLE>Example source</TITLE><LINK REL="stylesheet" TYPE="text/css" HREF="/CFDOCS/kfdocs.css"></HEAD>
<BODY BGCOLOR="#FFFFFF">
<cfif Variables.snipRow>
	<cffile action="read" file="#Variables.snipFile#" variable="Variables.source">
	<FONT FACE="Verdana, Arial, Helvetica" SIZE=1 COLOR="#666666"><cfoutput>/CFDOCS/snippets/#tagname#.cfm</cfoutput></FONT>
	<cfoutput>#HTMLCodeFormat(Variables.source)#</cfoutput>
<cfelse>
	<P>No such example.</P>
</cfif>
</BODY>
</HTML>
