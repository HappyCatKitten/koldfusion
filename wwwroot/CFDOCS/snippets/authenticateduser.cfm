<CFSET LoggedIn = IsAuthenticated()>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>IsAuthenticated()</TD><TD>#LoggedIn#</TD></TR>
<TR><TD>AuthenticatedUser()</TD><TD>"#AuthenticatedUser()#"</TD></TR>
</TABLE>
<P>Hello, #IIf(Len(AuthenticatedUser()), "AuthenticatedUser()", DE("guest"))#!
</CFOUTPUT>
