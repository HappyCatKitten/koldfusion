<CFSET Words = ListToArray("modem,Browser,applet,Cookie")>
<CFSET Nums = ListToArray("10,9,100,1")>
<CFSET Temp = ArraySort(Nums, "numeric", "desc")>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Call</TH><TH>Result</TH></TR>
<TR><TD>numeric, desc</TD><TD>#ArrayToList(Nums, ", ")#</TD></TR>
<CFSET Temp = ArraySort(Nums, "text")>
<TR><TD>text (on numbers!)</TD><TD>#ArrayToList(Nums, ", ")#</TD></TR>
<CFSET Temp = ArraySort(Words, "text")>
<TR><TD>text</TD><TD>#ArrayToList(Words, ", ")#</TD></TR>
<CFSET Temp = ArraySort(Words, "textnocase")>
<TR><TD>textnocase</TD><TD>#ArrayToList(Words, ", ")#</TD></TR>
</TABLE>
</CFOUTPUT>
