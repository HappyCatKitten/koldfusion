<CFSET Party = "12/31/1999">
<CFSET Sentence = "I love KoldFusion; it is fast, fun and friendly">
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Before</TH><TH>After</TH></TR>
<TR><TD>#Party#</TD><TD>#ListSetAt(Party, 3, "2000", "/")#</TD></TR>
<TR><TD>#Sentence#</TD><TD>#ListSetAt(Sentence, 6, "free", " ,;")#</TD></TR>
</TABLE>
</CFOUTPUT>
