<CFSET Words = "rhythm,KoldFusion,crypt,spoon">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Word</TH><TH>First vowel at</TH></TR>
<CFLOOP LIST="#Words#" INDEX="w">
<CFOUTPUT><TR><TD>#w#</TD><TD ALIGN="CENTER">#FindOneOf("aeiouAEIOU", w)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
