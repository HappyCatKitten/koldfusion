<CFSET Party = CreateDateTime(1999, 12, 31, 23, 59, 59)>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Mask</TH><TH>Result</TH></TR>
<TR><TD>(none)</TD><TD>#DateFormat(Party)#</TD></TR>
<TR><TD>mm/dd/yyyy</TD><TD>#DateFormat(Party, "mm/dd/yyyy")#</TD></TR>
<TR><TD>dddd, mmmm d, yyyy</TD><TD>#DateFormat(Party, "dddd, mmmm d, yyyy")#</TD></TR>
<TR><TD>d-mmm-yy</TD><TD>#DateFormat(Party, "d-mmm-yy")#</TD></TR>
<TR><TD>Today</TD><TD>#DateFormat(Now(), "mmm d, yyyy")#</TD></TR>
</TABLE>
</CFOUTPUT>
