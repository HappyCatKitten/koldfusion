<CFSET Fruit = "banana,Cherry,apple,date,Elderberry">
<CFSET Scores = "100,9,42,1999,7">
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Expression</TH><TH>Result</TH></TR>
<TR><TD>ListSort(Fruit, "text")</TD><TD>#ListSort(Fruit, "text")#</TD></TR>
<TR><TD>ListSort(Fruit, "textnocase")</TD><TD>#ListSort(Fruit, "textnocase")#</TD></TR>
<TR><TD>ListSort(Fruit, "textnocase", "desc")</TD><TD>#ListSort(Fruit, "textnocase", "desc")#</TD></TR>
<TR><TD>ListSort(Scores, "numeric")</TD><TD>#ListSort(Scores, "numeric")#</TD></TR>
<TR><TD>ListSort(Scores, "text")</TD><TD>#ListSort(Scores, "text")#</TD></TR>
</TABLE>
</CFOUTPUT>
