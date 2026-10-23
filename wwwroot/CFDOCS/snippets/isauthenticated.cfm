<CFIF IsAuthenticated()>
  <CFOUTPUT><P>Welcome back, #AuthenticatedUser()# (context #AuthenticatedContext()#).</CFOUTPUT>
<CFELSE>
  <P>You are not logged in. A real application would show its login form here
  and call CFAUTHENTICATE when it is posted.</P>
</CFIF>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>IsAuthenticated()</TD><TD>#IsAuthenticated()#</TD></TR>
<TR><TD>IsAuthenticated("Intranet")</TD><TD>#IsAuthenticated("Intranet")#</TD></TR>
</TABLE>
</CFOUTPUT>
