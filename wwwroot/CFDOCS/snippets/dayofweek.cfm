<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Date</TH><TH>DayOfWeek</TH><TH>Name</TH></TR>
<CFLOOP INDEX="D" LIST="12/31/1999,1/1/2000,2/29/2000">
<TR><TD>#D#</TD><TD>#DayOfWeek(D)#</TD><TD>#DayOfWeekAsString(DayOfWeek(D))#</TD></TR>
</CFLOOP>
</TABLE>
<P>Today is day #DayOfWeek(Now())# of the week.</P>
</CFOUTPUT>
