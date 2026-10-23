<!--- ch8_greeting.cfm: a custom tag.
      Call it as <CF_CH8_GREETING NAME="..." COLOR="...">.
      Opened on its own, it simply uses its default values. --->
<CFPARAM NAME="Attributes.Name" DEFAULT="World">
<CFPARAM NAME="Attributes.Color" DEFAULT="003399">

<CFOUTPUT>
<P><FONT FACE="Arial, Helvetica" SIZE="4" COLOR="###Attributes.Color#">
<B>Hello, #HTMLEditFormat(Attributes.Name)#!</B></FONT></P>
</CFOUTPUT>

<!--- Hand a value back to the calling page --->
<CFSET Caller.GreetingTime = TimeFormat(Now(), "h:mm tt")>
