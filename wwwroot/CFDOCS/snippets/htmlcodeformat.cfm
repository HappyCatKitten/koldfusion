<CFSET Source = "<TABLE BORDER=1>" & Chr(13) & Chr(10)
    & "  <TR><TD>Hello & welcome</TD></TR>" & Chr(13) & Chr(10)
    & "</TABLE>">
<P>The HTML source:</P>
<CFOUTPUT>#HTMLCodeFormat(Source)#</CFOUTPUT>
<P>The same HTML, rendered:</P>
<CFOUTPUT>#Source#</CFOUTPUT>
