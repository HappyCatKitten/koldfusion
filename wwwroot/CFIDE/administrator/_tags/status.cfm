<!--- red status message between rules, like the 4.x Administrator --->
<cfparam name="Attributes.message" default="">
<cfparam name="Attributes.back" default="">
<cfif Len(Attributes.message)>
<cfoutput>
<HR NOSHADE SIZE=1>
<CENTER><FONT FACE="Arial, Helvetica" SIZE="2" COLOR="##CC0000"><B>#Attributes.message#</B></FONT>
<cfif Len(Attributes.back)><FORM><INPUT TYPE="button" VALUE="Go Back" onClick="location='#Attributes.back#'"></FORM></cfif>
</CENTER>
<HR NOSHADE SIZE=1>
</cfoutput>
</cfif>
