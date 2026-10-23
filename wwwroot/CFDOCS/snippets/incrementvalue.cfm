<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>number</TH><TH>IncrementValue(number)</TH><TH>number + 1</TH></TR>
<CFLOOP INDEX="n" LIST="10,17.5,0,1998.9">
<CFOUTPUT><TR><TD ALIGN="RIGHT">#n#</TD><TD ALIGN="RIGHT">#IncrementValue(n)#</TD><TD ALIGN="RIGHT">#n + 1#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<CFSET Visitors = 0>
<CFLOOP INDEX="i" FROM="1" TO="3"><CFSET Visitors = IncrementValue(Visitors)></CFLOOP>
<CFOUTPUT><P>You are visitor number #Visitors#!</CFOUTPUT>
