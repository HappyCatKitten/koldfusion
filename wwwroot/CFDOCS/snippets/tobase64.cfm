<CFSET Plain = "Party like it's 1999!">
<CFSET Encoded = ToBase64(Plain)>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>Plain text</TD><TD>#Plain# (#Len(Plain)# characters)</TD></TR>
<TR><TD>ToBase64</TD><TD><TT>#Encoded#</TT> (#Len(Encoded)# characters)</TD></TR>
<TR><TD>Round trip</TD><TD>#ToString(ToBinary(Encoded))#</TD></TR>
</TABLE>
</CFOUTPUT>
