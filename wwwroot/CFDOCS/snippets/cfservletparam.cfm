<CFSET Visitor = "Netscape 4.7 user">
<CFTRY>
  <CFSERVLET CODE="GuestCounterServlet">
    <CFSERVLETPARAM NAME="page" VALUE="cfservletparam.cfm">
    <CFSERVLETPARAM NAME="visitor" VARIABLE="Visitor" TYPE="STRING">
  </CFSERVLET>
  <CFCATCH TYPE="Any">
    <CFOUTPUT>
    <P>No servlet engine here, so the parameters went nowhere.<BR>
    <I>#CFCATCH.Detail#</I></P>
    <P>The variable passed by reference still says: <B>#Visitor#</B></P>
    </CFOUTPUT>
  </CFCATCH>
</CFTRY>
