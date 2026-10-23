<CFSET Tests = "$1,234.50|($19.99)|1999|12 dollars|$|abc">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>String</TH><TH>LSIsCurrency</TH></TR>
<CFLOOP INDEX="S" LIST="#Tests#" DELIMITERS="|">
<CFOUTPUT>
<TR><TD>#S#</TD><TD>#LSIsCurrency(S)#</TD></TR>
</CFOUTPUT>
</CFLOOP>
</TABLE>
