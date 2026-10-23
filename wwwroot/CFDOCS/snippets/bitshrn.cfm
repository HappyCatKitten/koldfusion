<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>number</TH><TH>count</TH><TH>BitSHRN(number, count)</TH></TR>
<CFLOOP INDEX="args" LIST="256:4,255:4,65535:8,1999:1,-1:28">
<CFSET n = ListFirst(args, ":")><CFSET c = ListLast(args, ":")>
<CFOUTPUT><TR><TD ALIGN="RIGHT">#n#</TD><TD ALIGN="RIGHT">#c#</TD>
<TD ALIGN="RIGHT">#BitSHRN(n, c)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
