<CFSET Sentence = "The quick brown fox jumps over the lazy dog">
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Expression</TH><TH>Result</TH></TR>
<TR><TD>ListLen("a,b,c")</TD><TD>#ListLen("a,b,c")#</TD></TR>
<TR><TD>ListLen("a,,b,")</TD><TD>#ListLen("a,,b,")#</TD></TR>
<TR><TD>ListLen("")</TD><TD>#ListLen("")#</TD></TR>
<TR><TD>ListLen(Sentence, " ")</TD><TD>#ListLen(Sentence, " ")#</TD></TR>
<TR><TD>ListLen("1;2,3 4", ";, ")</TD><TD>#ListLen("1;2,3 4", ";, ")#</TD></TR>
</TABLE>
</CFOUTPUT>
