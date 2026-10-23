<CFQUERY NAME="GetParks" DATASOURCE="cfsnippets">
SELECT ParkName FROM Parks
</CFQUERY>
<CFOUTPUT>
<P>#GetParks.RecordCount# parks at 10 per page need #Ceiling(GetParks.RecordCount / 10)# pages.
</CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>number</TH><TH>Ceiling</TH><TH>Int</TH></TR>
<CFLOOP INDEX="n" LIST="3.2,3.7,3,-3.2,-3.7">
<CFOUTPUT><TR><TD ALIGN="RIGHT">#n#</TD><TD ALIGN="RIGHT">#Ceiling(n)#</TD><TD ALIGN="RIGHT">#Int(n)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
