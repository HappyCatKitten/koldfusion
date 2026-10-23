<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>number</TH><TH>Atn (radians)</TH><TH>degrees</TH></TR>
<CFLOOP INDEX="n" LIST="-1000,-1,0,1,1000">
<CFSET r = Atn(n)>
<CFOUTPUT><TR><TD ALIGN="RIGHT">#n#</TD><TD>#NumberFormat(r, "9.9999")#</TD>
<TD ALIGN="RIGHT">#NumberFormat(r * 180 / Pi(), "99.99")#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<CFOUTPUT><P>4 * Atn(1) = #4 * Atn(1)#</CFOUTPUT>
