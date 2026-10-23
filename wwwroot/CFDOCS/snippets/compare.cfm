<CFSET Pairs = "apple/apple,apple/Apple,apple/banana,Zebra/apple">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>String 1</TH><TH>String 2</TH><TH>Compare</TH><TH>CompareNoCase</TH></TR>
<CFLOOP LIST="#Pairs#" INDEX="p">
<CFSET a = ListFirst(p, "/")><CFSET b = ListLast(p, "/")>
<CFOUTPUT><TR><TD>#a#</TD><TD>#b#</TD>
<TD ALIGN="CENTER">#Compare(a, b)#</TD><TD ALIGN="CENTER">#CompareNoCase(a, b)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
