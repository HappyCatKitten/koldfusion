<CFSET D = CreateDateTime(1999, 12, 31, 23, 59, 58)>
<CFOUTPUT>
<P>Date: #D#</P>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Datepart</TH><TH>Result</TH></TR>
<CFLOOP INDEX="Part" LIST="yyyy,q,m,y,d,w,ww,h,n,s">
<TR><TD>#Part#</TD><TD ALIGN="RIGHT">#DatePart(Part, D)#</TD></TR>
</CFLOOP>
</TABLE>
</CFOUTPUT>
