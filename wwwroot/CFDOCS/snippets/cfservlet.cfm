<CFTRY>
  <CFSERVLET CODE="HelloWorldServlet" WRITEOUTPUT="Yes" TIMEOUT="10">
    <CFSERVLETPARAM NAME="greeting" VALUE="Hello from KoldFusion">
  </CFSERVLET>
  <CFCATCH TYPE="Application">
    <CFOUTPUT>
    <TABLE BORDER=1 CELLPADDING=3>
    <TR BGCOLOR="##FFCCCC"><TH COLSPAN=2>The servlet could not run</TH></TR>
    <TR><TD>Message</TD><TD>#CFCATCH.Message#</TD></TR>
    <TR><TD>Detail</TD><TD>#CFCATCH.Detail#</TD></TR>
    </TABLE>
    </CFOUTPUT>
  </CFCATCH>
</CFTRY>
