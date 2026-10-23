<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>number</TH><TH>Fix</TH><TH>Int</TH><TH>Round</TH><TH>Ceiling</TH></TR>
<CFLOOP INDEX="n" LIST="3.7,3.2,-3.2,-3.7">
<CFOUTPUT><TR><TD ALIGN="RIGHT">#n#</TD><TD ALIGN="RIGHT"><B>#Fix(n)#</B></TD><TD ALIGN="RIGHT">#Int(n)#</TD>
<TD ALIGN="RIGHT">#Round(n)#</TD><TD ALIGN="RIGHT">#Ceiling(n)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
