<CFSET Seats = ArrayNew(1)>
<CFSET Temp = ArrayResize(Seats, 6)>
<CFSET Seats[2] = "Ann">
<CFSET Seats[5] = "Bob">
<CFOUTPUT>
<P>ArrayLen(Seats) = #ArrayLen(Seats)#</P>
<TABLE BORDER=1 CELLPADDING=3>
<TR><CFLOOP INDEX="i" FROM="1" TO="#ArrayLen(Seats)#"><TH>Seat #i#</TH></CFLOOP></TR>
<TR><CFLOOP INDEX="i" FROM="1" TO="#ArrayLen(Seats)#"><TD>#Seats[i]#&nbsp;</TD></CFLOOP></TR>
</TABLE>
</CFOUTPUT>
