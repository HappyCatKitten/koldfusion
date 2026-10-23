<CFSET CRLF = Chr(13) & Chr(10)>
<CFOUTPUT>
<P>Codes 65 to 74 spell:
<CFLOOP INDEX="i" FROM="65" TO="74">#Chr(i)#</CFLOOP></P>
<P>A quote in a string: He said #Chr(34)#Hello#Chr(34)#</P>
<P>Length of a CR/LF pair: #Len(CRLF)# characters</P>
</CFOUTPUT>
