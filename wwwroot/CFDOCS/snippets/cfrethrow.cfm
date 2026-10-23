<!--- The inner handler notes the error, then passes it to the outer one --->
<CFSET Log = "">
<CFTRY>
  <CFTRY>
    <CFQUERY NAME="Report" DATASOURCE="cfsnippets">
    SELECT ParkName FROM ParksOf1999
    </CFQUERY>
  <CFCATCH TYPE="Database">
    <CFSET Log = "Inner handler saw a Database error at " & TimeFormat(Now(), "h:mm:ss tt")>
    <CFRETHROW>
  </CFCATCH>
  </CFTRY>
  <P>This line is never reached.</P>
<CFCATCH TYPE="Any">
  <CFOUTPUT>
  <TABLE BORDER=1 CELLPADDING=3>
  <TR><TD BGCOLOR="##FFFFCC">Inner handler</TD><TD>#Log#</TD></TR>
  <TR><TD BGCOLOR="##FFFFCC">Outer handler</TD><TD>Caught the same error again:<BR>
      Type <B>#CFCATCH.Type#</B>, SQLState <B>#CFCATCH.SQLState#</B><BR>#CFCATCH.Message#</TD></TR>
  </TABLE>
  </CFOUTPUT>
</CFCATCH>
</CFTRY>
