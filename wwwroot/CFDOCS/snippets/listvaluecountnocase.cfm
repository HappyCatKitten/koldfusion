<CFSET Votes = "Yes yes NO maybe YES no Yes y2k">
<CFOUTPUT>
<P>Votes: #Votes#</P>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Answer</TH><TH>ListValueCount</TH><TH>ListValueCountNoCase</TH></TR>
<TR><TD>yes</TD><TD>#ListValueCount(Votes, "yes", " ")#</TD><TD>#ListValueCountNoCase(Votes, "yes", " ")#</TD></TR>
<TR><TD>no</TD><TD>#ListValueCount(Votes, "no", " ")#</TD><TD>#ListValueCountNoCase(Votes, "no", " ")#</TD></TR>
<TR><TD>maybe</TD><TD>#ListValueCount(Votes, "maybe", " ")#</TD><TD>#ListValueCountNoCase(Votes, "maybe", " ")#</TD></TR>
</TABLE>
</CFOUTPUT>
