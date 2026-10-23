<CFSET Visitor = "Netscape 4.7 user">
<CFSET Wishlist = ListToArray("Zip drive,56K modem,Palm V")>
<CFTRY>
  <!--- SnoopServlet (in java/samples) lists everything it receives --->
  <CFSERVLET CODE="SnoopServlet" WRITEOUTPUT="No">
    <CFSERVLETPARAM NAME="page" VALUE="cfservletparam.cfm">
    <CFSERVLETPARAM NAME="visitor" VARIABLE="Visitor" TYPE="STRING">
    <CFSERVLETPARAM NAME="wishlist" VARIABLE="Wishlist">
  </CFSERVLET>
  <CFOUTPUT>
  <P>SnoopServlet sent back #Len(CFSERVLET.Output)# bytes:</P>
  #CFSERVLET.Output#
  </CFOUTPUT>
  <CFCATCH TYPE="Any">
    <CFOUTPUT>
    <P>The servlet could not run, so the parameters went nowhere.<BR>
    <I>#CFCATCH.Message#</I></P>
    <P>The variable passed by reference still says: <B>#Visitor#</B></P>
    </CFOUTPUT>
  </CFCATCH>
</CFTRY>
