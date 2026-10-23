<CFSET N = 1234567.891>
<CFOUTPUT>
<P>Locale: #GetLocale()#</P>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Mask</TH><TH>Result</TH></TR>
<TR><TD>(none)</TD><TD>#LSNumberFormat(N)#</TD></TR>
<TR><TD>9,999,999.99</TD><TD>#LSNumberFormat(N, "9,999,999.99")#</TD></TR>
<TR><TD>9999999.9</TD><TD>#LSNumberFormat(N, "9999999.9")#</TD></TR>
<TR><TD>(9,999,999)</TD><TD>#LSNumberFormat(-N, "(9,999,999)")#</TD></TR>
</TABLE>
</CFOUTPUT>
