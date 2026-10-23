<CFSET T = CreateDateTime(1999, 12, 31, 23, 59, 9)>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Mask</TH><TH>Result</TH></TR>
<TR><TD>(none)</TD><TD>#TimeFormat(T)#</TD></TR>
<TR><TD>HH:mm:ss</TD><TD>#TimeFormat(T, "HH:mm:ss")#</TD></TR>
<TR><TD>h:mm tt</TD><TD>#TimeFormat(T, "h:mm tt")#</TD></TR>
<TR><TD>h:mm t</TD><TD>#TimeFormat(T, "h:mm t")#</TD></TR>
<TR><TD>medium</TD><TD>#TimeFormat(T, "medium")#</TD></TR>
<TR><TD>Right now</TD><TD>#TimeFormat(Now(), "hh:mm:ss tt")#</TD></TR>
</TABLE>
</CFOUTPUT>
