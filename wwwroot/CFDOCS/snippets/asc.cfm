<CFSET Letters = "A,a,Z,0,~">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Character</TH><TH>Asc()</TH></TR>
<CFLOOP LIST="#Letters#" INDEX="ch">
<CFOUTPUT><TR><TD ALIGN="CENTER">#ch#</TD><TD ALIGN="RIGHT">#Asc(ch)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<CFOUTPUT><P>Asc("KoldFusion") looks only at the K: #Asc("KoldFusion")#</P></CFOUTPUT>
