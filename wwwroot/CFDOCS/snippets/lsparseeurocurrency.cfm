<CFSET Amounts = "1,234.50|(99.95)|2002">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>String</TH><TH>LSParseEuroCurrency</TH><TH>Formatted</TH></TR>
<CFLOOP INDEX="A" LIST="#Amounts#" DELIMITERS="|">
<CFOUTPUT>
<TR><TD>#A#</TD><TD>#LSParseEuroCurrency(A)#</TD><TD>#LSEuroCurrencyFormat(LSParseEuroCurrency(A))#</TD></TR>
</CFOUTPUT>
</CFLOOP>
</TABLE>
