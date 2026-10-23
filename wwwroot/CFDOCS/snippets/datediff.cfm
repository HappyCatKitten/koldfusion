<CFSET Start = CreateDateTime(1999, 1, 1, 9, 0, 0)>
<CFSET Y2K = CreateDateTime(2000, 1, 1, 0, 0, 0)>
<CFOUTPUT>
<P>From #DateFormat(Start, "mmm d, yyyy")# #TimeFormat(Start, "h:mm tt")#
to the year 2000:</P>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Datepart</TH><TH>DateDiff</TH></TR>
<CFLOOP INDEX="Part" LIST="yyyy,q,m,ww,d,h">
<TR><TD>#Part#</TD><TD ALIGN="RIGHT">#DateDiff(Part, Start, Y2K)#</TD></TR>
</CFLOOP>
</TABLE>
<P>Dec 31, 1999 to Jan 1, 2000: #DateDiff("d", "12/31/1999", "1/1/2000")# day,
#DateDiff("yyyy", "12/31/1999", "1/1/2000")# years.</P>
</CFOUTPUT>
