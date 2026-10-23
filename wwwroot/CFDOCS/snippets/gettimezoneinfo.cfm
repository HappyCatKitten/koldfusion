<CFSET TZ = GetTimeZoneInfo()>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Key</TH><TH>Value</TH></TR>
<TR><TD>utcTotalOffset</TD><TD>#TZ.utcTotalOffset#</TD></TR>
<TR><TD>utcHourOffset</TD><TD>#TZ.utcHourOffset#</TD></TR>
<TR><TD>utcMinuteOffset</TD><TD>#TZ.utcMinuteOffset#</TD></TR>
<TR><TD>isDSTOn</TD><TD>#TZ.isDSTOn#</TD></TR>
</TABLE>
</CFOUTPUT>
