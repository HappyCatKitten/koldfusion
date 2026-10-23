<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Argument</TH><TH>ExpandPath()</TH></TR>
<TR><TD>"expandpath.cfm"</TD><TD>#ExpandPath("expandpath.cfm")#</TD></TR>
<TR><TD>"images/logo.gif"</TD><TD>#ExpandPath("images/logo.gif")#</TD></TR>
<TR><TD>"/CFDOCS/dochome.htm"</TD><TD>#ExpandPath("/CFDOCS/dochome.htm")#</TD></TR>
</TABLE>
<P>Does this page exist where ExpandPath says? #FileExists(ExpandPath("expandpath.cfm"))#
</CFOUTPUT>
