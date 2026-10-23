<CFSET Allowed = "Netscape;Explorer;Opera">
<CFSET Tests = "netscape,EXPLORER,Mosaic">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Browser</TH><TH>ListFind</TH><TH>ListFindNoCase</TH></TR>
<CFLOOP INDEX="B" LIST="#Tests#">
<CFOUTPUT>
<TR><TD>#B#</TD><TD>#ListFind(Allowed, B, ";")#</TD><TD>#ListFindNoCase(Allowed, B, ";")#</TD></TR>
</CFOUTPUT>
</CFLOOP>
</TABLE>
