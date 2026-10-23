<CFSET Rate = 1.95583>
<CFSET Marks = "100,250,1999">
<P>Converting German marks at the fixed rate:</P>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>DEM</TH><TH>Euro</TH></TR>
<CFLOOP INDEX="M" LIST="#Marks#">
<CFOUTPUT>
<TR><TD ALIGN="right">#DecimalFormat(M)#</TD><TD ALIGN="right">#LSEuroCurrencyFormat(M / Rate)#</TD></TR>
</CFOUTPUT>
</CFLOOP>
</TABLE>
