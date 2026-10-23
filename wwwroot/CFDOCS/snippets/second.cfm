<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>Second("11:59:42 PM")</TD><TD>#Second("11:59:42 PM")#</TD></TR>
<TR><TD>Second(CreateTime(12, 0, 7))</TD><TD>#Second(CreateTime(12, 0, 7))#</TD></TR>
<TR><TD>Seconds on the server clock</TD><TD>#Second(Now())#</TD></TR>
</TABLE>
</CFOUTPUT>
