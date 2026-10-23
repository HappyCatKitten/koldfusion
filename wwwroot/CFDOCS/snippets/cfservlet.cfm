<!--- HelloServlet ships in java/samples; it counts the visits it is handed by reference --->
<CFPARAM NAME="Visits" DEFAULT="0">
<CFTRY>
  <CFSERVLET CODE="HelloServlet" WRITEOUTPUT="Yes" TIMEOUT="10">
    <CFSERVLETPARAM NAME="name" VALUE="KoldFusion developer">
    <CFSERVLETPARAM NAME="visits" VARIABLE="Visits" TYPE="INT">
  </CFSERVLET>
  <CFOUTPUT>
  <P>The servlet answered with status #CFSERVLET.StatusCode# and Content-Type
  #CFSERVLET["Content-Type"]#, and set Visits to #Visits#.</P>
  </CFOUTPUT>
  <CFCATCH TYPE="Any">
    <CFOUTPUT>
    <TABLE BORDER=1 CELLPADDING=3>
    <TR BGCOLOR="##FFCCCC"><TH COLSPAN=2>The servlet could not run</TH></TR>
    <TR><TD>Message</TD><TD>#CFCATCH.Message#</TD></TR>
    <TR><TD>Detail</TD><TD>#CFCATCH.Detail#</TD></TR>
    </TABLE>
    </CFOUTPUT>
  </CFCATCH>
</CFTRY>
