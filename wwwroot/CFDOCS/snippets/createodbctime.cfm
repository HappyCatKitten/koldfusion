<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Input</TH><TH>CreateODBCTime</TH></TR>
<TR><TD>"9:42 PM"</TD><TD>#CreateODBCTime("9:42 PM")#</TD></TR>
<TR><TD>CreateTime(8, 30, 0)</TD><TD>#CreateODBCTime(CreateTime(8, 30, 0))#</TD></TR>
<TR><TD>"12/31/1999 23:59:59"</TD><TD>#CreateODBCTime("12/31/1999 23:59:59")#</TD></TR>
</TABLE>
</CFOUTPUT>
