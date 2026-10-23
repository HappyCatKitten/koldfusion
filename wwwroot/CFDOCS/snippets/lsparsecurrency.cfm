<CFSET Prices = "$1,234.50|($19.99)|  $ 5|2000">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>String</TH><TH>LSParseCurrency</TH><TH>Plus 10%</TH></TR>
<CFLOOP INDEX="P" LIST="#Prices#" DELIMITERS="|">
<CFOUTPUT>
<TR><TD>#P#</TD><TD>#LSParseCurrency(P)#</TD><TD>#DollarFormat(LSParseCurrency(P) * 1.1)#</TD></TR>
</CFOUTPUT>
</CFLOOP>
</TABLE>
