<CFSET Key = "Y2Kready">
<CFSET Secret = Encrypt("Meet me at the server room at midnight", Key)>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>Encrypted</TD><TD><TT>#HTMLEditFormat(Secret)#</TT></TD></TR>
<TR><TD>As Base64</TD><TD><TT>#ToBase64(Secret)#</TT></TD></TR>
<TR><TD>Decrypted</TD><TD>#Decrypt(Secret, Key)#</TD></TR>
</TABLE>
</CFOUTPUT>
