<CFSET Lunch = CreateTime(12, 30, 0)>
<CFSET Quitting = CreateTime(17, 0, 0)>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH></TH><TH>Raw value</TH><TH>TimeFormat</TH></TR>
<TR><TD>Lunch</TD><TD>#Lunch#</TD><TD>#TimeFormat(Lunch, "h:mm tt")#</TD></TR>
<TR><TD>Quitting time</TD><TD>#Quitting#</TD><TD>#TimeFormat(Quitting, "h:mm tt")#</TD></TR>
</TABLE>
<P>Afternoon shift: #DateDiff("h", Lunch, Quitting)# hours (and a half).</P>
</CFOUTPUT>
