<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>number</TH><TH>DecrementValue(number)</TH><TH>number - 1</TH></TR>
<CFLOOP INDEX="n" LIST="10,17.5,1,0.25">
<CFOUTPUT><TR><TD ALIGN="RIGHT">#n#</TD><TD ALIGN="RIGHT">#DecrementValue(n)#</TD><TD ALIGN="RIGHT">#n - 1#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<P>Countdown:
<CFSET n = 5>
<CFLOOP CONDITION="n GT 0"><CFOUTPUT>#n#... </CFOUTPUT><CFSET n = DecrementValue(n)></CFLOOP>
Happy New Year!
