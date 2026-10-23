<CFSET D = CreateDate(2000, 1, 1)>
<CFOUTPUT>
<P>Locale: #GetLocale()#</P>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Mask</TH><TH>Result</TH></TR>
<TR><TD>(none)</TD><TD>#LSDateFormat(D)#</TD></TR>
<TR><TD>short</TD><TD>#LSDateFormat(D, "short")#</TD></TR>
<TR><TD>medium</TD><TD>#LSDateFormat(D, "medium")#</TD></TR>
<TR><TD>long</TD><TD>#LSDateFormat(D, "long")#</TD></TR>
<TR><TD>full</TD><TD>#LSDateFormat(D, "full")#</TD></TR>
</TABLE>
</CFOUTPUT>
