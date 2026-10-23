<CFSET Stored = ToBase64(Encrypt("Account 1999-A", "secret key"))>
<CFSET Restored = ToString(ToBinary(Stored))>
<CFOUTPUT>
<P>Stored in the cookie: <TT>#Stored#</TT></P>
<P>Right key: #Decrypt(Restored, "secret key")#</P>
<P>Wrong key: #HTMLEditFormat(REReplace(Decrypt(Restored, "wrong key"), "[^[:print:]]", "?", "ALL"))#</P>
</CFOUTPUT>
