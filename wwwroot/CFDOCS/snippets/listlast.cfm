<CFSET File = "/home/web/reports/sales_1999.xls">
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Expression</TH><TH>Result</TH></TR>
<TR><TD>ListLast("Larry,Moe,Curly")</TD><TD>#ListLast("Larry,Moe,Curly")#</TD></TR>
<TR><TD>ListLast(File, "/")</TD><TD>#ListLast(File, "/")#</TD></TR>
<TR><TD>ListLast(File, ".")</TD><TD>#ListLast(File, ".")#</TD></TR>
<TR><TD>ListLast("a,b,c,,,")</TD><TD>#ListLast("a,b,c,,,")#</TD></TR>
</TABLE>
</CFOUTPUT>
