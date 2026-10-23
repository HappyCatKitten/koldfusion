<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>number</TH><TH>Round(number)</TH></TR>
<CFLOOP INDEX="n" LIST="3.49,3.5,3.51,-2.5,-2.51">
<CFOUTPUT><TR><TD ALIGN="RIGHT">#n#</TD><TD ALIGN="RIGHT">#Round(n)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<CFSET Price = 19.98765>
<CFOUTPUT><P>#Price# to two places: #Round(Price * 100) / 100#</CFOUTPUT>
