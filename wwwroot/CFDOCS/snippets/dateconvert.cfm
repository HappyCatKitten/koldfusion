<CFSET Local = Now()>
<CFSET UTC = DateConvert("local2Utc", Local)>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>Server local time</TD><TD>#TimeFormat(Local, "HH:mm:ss")#</TD></TR>
<TR><TD>UTC</TD><TD>#TimeFormat(UTC, "HH:mm:ss")#</TD></TR>
<TR><TD>Back to local</TD><TD>#TimeFormat(DateConvert("utc2Local", UTC), "HH:mm:ss")#</TD></TR>
</TABLE>
</CFOUTPUT>
