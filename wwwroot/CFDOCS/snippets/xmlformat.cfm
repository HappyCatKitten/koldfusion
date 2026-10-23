<CFSET Title = "Tom & Jerry's <Greatest> Hits">
<CFSET Xml = "<item><title>" & XMLFormat(Title) & "</title></item>">
<CFOUTPUT>
<P>Original: #HTMLEditFormat(Title)#</P>
<P>XML: <TT>#HTMLEditFormat(Xml)#</TT></P>
</CFOUTPUT>
