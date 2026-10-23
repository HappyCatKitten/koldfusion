<CFPARAM NAME="HeadCount" DEFAULT="(not returned)">
<CFTRY>
  <CFSTOREDPROC PROCEDURE="sp_CountStaff" DATASOURCE="cfsnippets">
    <CFPROCPARAM TYPE="In" CFSQLTYPE="CF_SQL_VARCHAR" DBVARNAME="@dept" VALUE="Engineering">
    <CFPROCPARAM TYPE="Out" CFSQLTYPE="CF_SQL_INTEGER" DBVARNAME="@total" VARIABLE="HeadCount">
  </CFSTOREDPROC>
  <CFCATCH TYPE="Database">
    <CFOUTPUT><P>Caught a #CFCATCH.Type# exception: #CFCATCH.Message#</P></CFOUTPUT>
  </CFCATCH>
</CFTRY>
<CFQUERY NAME="Counted" DATASOURCE="cfsnippets">
SELECT COUNT(*) AS Total FROM Employees WHERE Department = 'Engineering'
</CFQUERY>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>Out parameter HeadCount</TD><TD>#HeadCount#</TD></TR>
<TR><TD>Same answer from CFQUERY</TD><TD>#Counted.Total#</TD></TR>
</TABLE>
</CFOUTPUT>
