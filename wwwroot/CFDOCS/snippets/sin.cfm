<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Degrees</TH><TH>Sin</TH><TH>Cos</TH><TH>Tan</TH></TR>
<CFLOOP INDEX="deg" LIST="0,30,45,60,120,180,300">
<CFSET r = deg * Pi() / 180>
<CFOUTPUT><TR><TD ALIGN="RIGHT">#deg#</TD><TD>#NumberFormat(Sin(r), "9.9999")#</TD>
<TD>#NumberFormat(Cos(r), "9.9999")#</TD><TD>#NumberFormat(Tan(r), "9.9999")#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
