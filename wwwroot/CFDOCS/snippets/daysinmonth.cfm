<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Month</TH><TH>Days</TH></TR>
<CFLOOP INDEX="Y" LIST="1900,1999,2000">
<TR><TD>February #Y#</TD><TD>#DaysInMonth(CreateDate(Y, 2, 1))#</TD></TR>
</CFLOOP>
<CFLOOP INDEX="M" FROM="9" TO="12">
<TR><TD>#MonthAsString(M)# 1999</TD><TD>#DaysInMonth(CreateDate(1999, M, 1))#</TD></TR>
</CFLOOP>
</TABLE>
</CFOUTPUT>
