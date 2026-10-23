<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>number</TH><TH>Exp(number)</TH></TR>
<CFLOOP INDEX="n" LIST="0,1,2,-1,10">
<CFOUTPUT><TR><TD ALIGN="RIGHT">#n#</TD><TD>#Exp(n)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<CFOUTPUT>
<P>$1,000 at 5% compounded continuously for 10 years:
#DollarFormat(1000 * Exp(0.05 * 10))#
</CFOUTPUT>
