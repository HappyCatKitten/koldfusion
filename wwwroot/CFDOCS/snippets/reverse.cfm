<CFSET Words = "stressed,racecar,KoldFusion,1999">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>String</TH><TH>Reverse</TH><TH>Palindrome?</TH></TR>
<CFLOOP LIST="#Words#" INDEX="w">
<CFOUTPUT><TR><TD>#w#</TD><TD>#Reverse(w)#</TD>
<TD>#YesNoFormat(CompareNoCase(w, Reverse(w)) EQ 0)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
