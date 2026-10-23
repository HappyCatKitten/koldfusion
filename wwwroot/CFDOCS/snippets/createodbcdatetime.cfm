<CFSET Posted = ParseDateTime("October 22, 1999 9:42 PM")>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Function</TH><TH>Result</TH></TR>
<TR><TD>CreateODBCDateTime</TD><TD>#CreateODBCDateTime(Posted)#</TD></TR>
<TR><TD>CreateODBCDate</TD><TD>#CreateODBCDate(Posted)#</TD></TR>
<TR><TD>CreateODBCTime</TD><TD>#CreateODBCTime(Posted)#</TD></TR>
<TR><TD>From a string</TD><TD>#CreateODBCDateTime("12/31/1999 11:59 PM")#</TD></TR>
</TABLE>
</CFOUTPUT>
