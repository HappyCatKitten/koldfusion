<CFSET Balances = "250.00,0,-75.50">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Balance</TH><TH>Sgn</TH><TH>Status</TH></TR>
<CFLOOP INDEX="b" LIST="#Balances#">
<CFSET Status = ListGetAt("Overdrawn,Even,In credit", Sgn(b) + 2)>
<CFOUTPUT><TR><TD ALIGN="RIGHT">#DollarFormat(b)#</TD><TD ALIGN="RIGHT">#Sgn(b)#</TD><TD>#Status#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
