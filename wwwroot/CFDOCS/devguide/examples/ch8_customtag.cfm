<!--- ch8_customtag.cfm: calling a custom tag --->
<CF_CH8_GREETING NAME="Frostbite Falls" COLOR="CC0000">

<CFOUTPUT><P>The tag says it greeted us at #GreetingTime#.</P></CFOUTPUT>

<!--- The same tag, called with CFMODULE and a path --->
<CFMODULE TEMPLATE="ch8_greeting.cfm" NAME="CFMODULE caller">

<!--- Variables set inside the tag stay inside the tag --->
<CFOUTPUT>
<P>Does this page see the tag's Attributes scope? #YesNoFormat(IsDefined("Attributes.Color"))#</P>
</CFOUTPUT>
