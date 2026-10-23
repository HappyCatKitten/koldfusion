<CFSET Browsers = "Netscape 4.7,Internet Explorer 5,,Mosaic,Lynx">
<CFOUTPUT>
<P>Original: #Browsers#</P>
<P>Slashes: #ListChangeDelims(Browsers, " / ")#</P>
<P>As a bulleted list:</P>
<UL><LI>#ListChangeDelims(Browsers, "<LI>")#</UL>
<P>As a table row:</P>
<TABLE BORDER=1 CELLPADDING=3><TR><TD>#ListChangeDelims(Browsers, "</TD><TD>")#</TD></TR></TABLE>
</CFOUTPUT>
