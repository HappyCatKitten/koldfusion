<CFSET Words = "password,Password,KoldFusion">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>String</TH><TH>Hash()</TH></TR>
<CFLOOP LIST="#Words#" INDEX="w">
<CFOUTPUT><TR><TD>#w#</TD><TD><TT>#Hash(w)#</TT></TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<CFIF Hash("password") EQ "5F4DCC3B5AA765D61D8327DEB882CF99"><P>Password accepted.</P></CFIF>
