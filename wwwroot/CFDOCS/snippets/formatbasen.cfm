<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>number</TH><TH>Base 2</TH><TH>Base 8</TH><TH>Base 16</TH><TH>Base 36</TH></TR>
<CFLOOP INDEX="n" LIST="10,255,1999,-42">
<CFOUTPUT><TR><TD ALIGN="RIGHT">#n#</TD><TD><TT>#FormatBaseN(n, 2)#</TT></TD><TD><TT>#FormatBaseN(n, 8)#</TT></TD>
<TD><TT>#FormatBaseN(n, 16)#</TT></TD><TD><TT>#FormatBaseN(n, 36)#</TT></TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<P>A web-safe palette row:
<CFLOOP INDEX="g" FROM="0" TO="255" STEP="51">
<CFSET hex = Right("0" & FormatBaseN(g, 16), 2)>
<CFOUTPUT><FONT COLOR="##00#hex#00"><B>##00#hex#00</B></FONT> </CFOUTPUT>
</CFLOOP>
