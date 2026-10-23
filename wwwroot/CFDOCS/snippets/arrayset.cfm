<!--- Seven zeroed counters, one per weekday --->
<CFSET Hits = ArrayNew(1)>
<CFSET Temp = ArraySet(Hits, 1, 7, 0)>
<CFSET Hits[3] = Hits[3] + 42>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><CFLOOP INDEX="d" FROM="1" TO="7"><TH>#Left(DayOfWeekAsString(d), 3)#</TH></CFLOOP></TR>
<TR><CFLOOP INDEX="d" FROM="1" TO="7"><TD ALIGN="RIGHT">#Hits[d]#</TD></CFLOOP></TR>
</TABLE>
</CFOUTPUT>
