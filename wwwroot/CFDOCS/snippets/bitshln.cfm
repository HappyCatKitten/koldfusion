<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>number</TH><TH>count</TH><TH>BitSHLN(number, count)</TH></TR>
<CFLOOP INDEX="args" LIST="1:0,1:4,3:8,255:8,1:31">
<CFSET n = ListFirst(args, ":")><CFSET c = ListLast(args, ":")>
<CFOUTPUT><TR><TD ALIGN="RIGHT">#n#</TD><TD ALIGN="RIGHT">#c#</TD>
<TD ALIGN="RIGHT">#BitSHLN(n, c)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
