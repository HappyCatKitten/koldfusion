<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>number</TH><TH>ASin (radians)</TH><TH>degrees</TH></TR>
<CFLOOP INDEX="n" LIST="-1,-0.5,0,0.5,1">
<CFSET r = ASin(n)>
<CFOUTPUT><TR><TD ALIGN="RIGHT">#n#</TD><TD>#NumberFormat(r, "9.9999")#</TD>
<TD ALIGN="RIGHT">#Round(r * 180 / Pi())#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
