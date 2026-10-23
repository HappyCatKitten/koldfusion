<CFSET Secret = 1999><CFSET Key = 1234>
<CFSET Scrambled = BitXor(Secret, Key)>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Value</TH><TH>Decimal</TH><TH>Binary</TH></TR>
<TR><TD>Secret</TD><TD ALIGN="RIGHT">#Secret#</TD><TD><TT>#FormatBaseN(Secret, 2)#</TT></TD></TR>
<TR><TD>Key</TD><TD ALIGN="RIGHT">#Key#</TD><TD><TT>#FormatBaseN(Key, 2)#</TT></TD></TR>
<TR><TD>BitXor(Secret, Key)</TD><TD ALIGN="RIGHT">#Scrambled#</TD><TD><TT>#FormatBaseN(Scrambled, 2)#</TT></TD></TR>
<TR><TD>BitXor(that, Key)</TD><TD ALIGN="RIGHT">#BitXor(Scrambled, Key)#</TD><TD><TT>#FormatBaseN(BitXor(Scrambled, Key), 2)#</TT></TD></TR>
</TABLE>
</CFOUTPUT>
