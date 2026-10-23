<CFSET D = CreateDate(2000, 12, 31)>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>DayOfYear("3/1/1999")</TD><TD>#DayOfYear("3/1/1999")#</TD></TR>
<TR><TD>DayOfYear("3/1/2000")</TD><TD>#DayOfYear("3/1/2000")#</TD></TR>
<TR><TD>DayOfYear(Dec 31, 2000)</TD><TD>#DayOfYear(D)#</TD></TR>
<TR><TD>Days left this year</TD><TD>#DaysInYear(Now()) - DayOfYear(Now())#</TD></TR>
</TABLE>
</CFOUTPUT>
