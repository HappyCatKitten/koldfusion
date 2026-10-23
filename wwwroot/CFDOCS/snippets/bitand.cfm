<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>a</TH><TH>b</TH><TH>a (binary)</TH><TH>b (binary)</TH><TH>BitAnd(a, b)</TH></TR>
<CFLOOP INDEX="pair" LIST="12:10,255:15,6:9,1999:2000">
<CFSET a = ListFirst(pair, ":")><CFSET b = ListLast(pair, ":")>
<CFOUTPUT><TR><TD>#a#</TD><TD>#b#</TD><TD><TT>#FormatBaseN(a, 2)#</TT></TD>
<TD><TT>#FormatBaseN(b, 2)#</TT></TD><TD><B>#BitAnd(a, b)#</B> (<TT>#FormatBaseN(BitAnd(a, b), 2)#</TT>)</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
