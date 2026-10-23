<CFSET Text = "Netscape or netscape or NETSCAPE: all the same browser.">
<CFSET Word = "netscape">
<CFOUTPUT>
<P>#REReplaceNoCase(Text, "(" & Word & ")", "<B>\1</B>", "ALL")#</P>
<P>#REReplaceNoCase(Text, "NetScape", "Mosaic")#</P>
</CFOUTPUT>
