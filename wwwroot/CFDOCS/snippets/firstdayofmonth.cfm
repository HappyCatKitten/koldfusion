<CFSET D = CreateDate(2000, 3, 15)>
<CFSET First = CreateDate(Year(D), Month(D), 1)>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>FirstDayOfMonth(March 15, 2000)</TD><TD>#FirstDayOfMonth(D)#</TD></TR>
<TR><TD>FirstDayOfMonth(March 15, 1999)</TD><TD>#FirstDayOfMonth("3/15/1999")#</TD></TR>
<TR><TD>First of the month as a date</TD><TD>#DateFormat(First, "mmmm d, yyyy")#</TD></TR>
<TR><TD>...falls on a</TD><TD>#DayOfWeekAsString(DayOfWeek(First))#</TD></TR>
</TABLE>
</CFOUTPUT>
