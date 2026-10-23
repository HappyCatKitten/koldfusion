<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>number</TH><TH>BitNot(number)</TH><TH>BitAnd(255, BitNot(number))</TH></TR>
<CFLOOP INDEX="n" LIST="0,1,12,255,-1">
<CFOUTPUT><TR><TD ALIGN="RIGHT">#n#</TD><TD ALIGN="RIGHT">#BitNot(n)#</TD>
<TD ALIGN="RIGHT">#BitAnd(255, BitNot(n))#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
