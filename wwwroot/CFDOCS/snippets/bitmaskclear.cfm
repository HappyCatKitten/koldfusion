<CFSET n = 255>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Call</TH><TH>Result</TH><TH>Binary</TH></TR>
<CFLOOP INDEX="args" LIST="0:4,4:4,2:3,7:1">
<CFSET s = ListFirst(args, ":")><CFSET l = ListLast(args, ":")>
<CFSET r = BitMaskClear(n, s, l)>
<CFOUTPUT><TR><TD><TT>BitMaskClear(#n#, #s#, #l#)</TT></TD><TD ALIGN="RIGHT">#r#</TD>
<TD><TT>#Right("00000000" & FormatBaseN(r, 2), 8)#</TT></TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
