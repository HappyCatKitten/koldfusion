<CFSET Midnight = CreateDateTime(1999, 12, 31, 23, 59, 59)>
<CFSET Rollover = DateAdd("s", 1, Midnight)>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH></TH><TH>Raw value</TH><TH>Formatted</TH></TR>
<TR><TD>Last second of 1999</TD><TD>#Midnight#</TD>
    <TD>#DateFormat(Midnight, "mmm d, yyyy")# #TimeFormat(Midnight, "HH:mm:ss")#</TD></TR>
<TR><TD>One second later</TD><TD>#Rollover#</TD>
    <TD>#DateFormat(Rollover, "mmm d, yyyy")# #TimeFormat(Rollover, "HH:mm:ss")#</TD></TR>
</TABLE>
<P>Still running? Then your server is Y2K-ready.</P>
</CFOUTPUT>
