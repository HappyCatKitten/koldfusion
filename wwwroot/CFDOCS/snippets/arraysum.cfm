<CFSET Cart = ArrayNew(1)>
<CFSET Cart[1] = 19.95>
<CFSET Cart[2] = 4.50>
<CFSET Cart[3] = 129.00>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<CFLOOP INDEX="i" FROM="1" TO="#ArrayLen(Cart)#">
<TR><TD>Item #i#</TD><TD ALIGN="RIGHT">#DollarFormat(Cart[i])#</TD></TR>
</CFLOOP>
<TR><TH>Total</TH><TH ALIGN="RIGHT">#DollarFormat(ArraySum(Cart))#</TH></TR>
</TABLE>
</CFOUTPUT>
