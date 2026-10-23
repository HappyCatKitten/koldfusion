<CFSET Values = "1234567.891,42,-3,0.005,999.999">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Number</TH><TH>DecimalFormat</TH></TR>
<CFLOOP INDEX="N" LIST="#Values#">
<CFOUTPUT>
<TR><TD>#N#</TD><TD ALIGN="right">#DecimalFormat(N)#</TD></TR>
</CFOUTPUT>
</CFLOOP>
</TABLE>
