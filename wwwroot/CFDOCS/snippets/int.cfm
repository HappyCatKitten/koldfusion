<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>number</TH><TH>Int(number)</TH></TR>
<CFLOOP INDEX="n" LIST="3.7,3.2,3,-3.2,-3.7">
<CFOUTPUT><TR><TD ALIGN="RIGHT">#n#</TD><TD ALIGN="RIGHT">#Int(n)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<CFSET Minutes = 197>
<CFOUTPUT><P>#Minutes# minutes is #Int(Minutes / 60)# hours and #Minutes MOD 60# minutes.</CFOUTPUT>
