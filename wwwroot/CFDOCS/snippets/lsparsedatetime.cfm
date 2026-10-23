<CFSET Tests = "12/31/1999 11:59 PM|January 1, 2000|Feb 29, 2000 8:00 AM">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>String</TH><TH>Date/time value</TH><TH>Day of week</TH></TR>
<CFLOOP INDEX="S" LIST="#Tests#" DELIMITERS="|">
<CFSET D = LSParseDateTime(S)>
<CFOUTPUT>
<TR><TD>#S#</TD><TD>#D#</TD><TD>#DayOfWeekAsString(DayOfWeek(D))#</TD></TR>
</CFOUTPUT>
</CFLOOP>
</TABLE>
