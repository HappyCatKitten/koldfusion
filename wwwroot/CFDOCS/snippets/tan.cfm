<CFSET Distance = 100>
<P>How tall is a tree that you see at a given angle from 100 feet away?
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Angle (degrees)</TH><TH>Tan</TH><TH>Height (feet)</TH></TR>
<CFLOOP INDEX="deg" LIST="10,30,45,60">
<CFSET t = Tan(deg * Pi() / 180)>
<CFOUTPUT><TR><TD ALIGN="RIGHT">#deg#</TD><TD>#NumberFormat(t, "9.9999")#</TD>
<TD ALIGN="RIGHT">#NumberFormat(Distance * t, "9.9")#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
