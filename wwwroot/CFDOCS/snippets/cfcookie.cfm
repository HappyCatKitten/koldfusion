<!--- A visit counter kept in a cookie --->
<CFPARAM NAME="URL.Forget" DEFAULT="No">
<CFPARAM NAME="Cookie.SnipVisits" DEFAULT="0">

<CFIF URL.Forget>
  <CFCOOKIE NAME="SnipVisits" EXPIRES="NOW">
  <P>The cookie has been deleted. The browser will not send it again.</P>
<CFELSE>
  <CFCOOKIE NAME="SnipVisits" VALUE="#Cookie.SnipVisits + 1#" EXPIRES="30">
  <CFOUTPUT>
  <TABLE BORDER=1 CELLPADDING=4>
  <TR><TD BGCOLOR="##FFFFCC">Visits counted by the cookie</TD><TD><B>#Cookie.SnipVisits#</B></TD></TR>
  <TR><TD BGCOLOR="##FFFFCC">Cookie expires</TD><TD>#DateFormat(Now() + 30, "mmmm d, yyyy")#</TD></TR>
  </TABLE>
  </CFOUTPUT>
</CFIF>
<P><A HREF="cfcookie.cfm">Visit again</A> | <A HREF="cfcookie.cfm?Forget=Yes">Delete the cookie</A></P>
