<CFSET Inputs = "42,3.5 inches,-12.75 degrees,1999 Party,Y2K,  7 spaces">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>String</TH><TH>Val()</TH><TH>IsNumeric()</TH></TR>
<CFLOOP LIST="#Inputs#" INDEX="s">
<CFOUTPUT><TR><TD>"#s#"</TD><TD ALIGN="RIGHT">#Val(s)#</TD><TD>#IsNumeric(s)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
