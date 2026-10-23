<CFSET Amounts = "1234.5,-99.95,1000000">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Amount</TH><TH>local</TH><TH>international</TH><TH>none</TH></TR>
<CFLOOP INDEX="A" LIST="#Amounts#">
<CFOUTPUT>
<TR><TD>#A#</TD>
    <TD ALIGN="right">#LSCurrencyFormat(A)#</TD>
    <TD ALIGN="right">#LSCurrencyFormat(A, "international")#</TD>
    <TD ALIGN="right">#LSCurrencyFormat(A, "none")#</TD></TR>
</CFOUTPUT>
</CFLOOP>
</TABLE>
