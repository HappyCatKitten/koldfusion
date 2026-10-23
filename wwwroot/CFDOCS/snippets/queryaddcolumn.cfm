<CFSET Movies = QueryNew("Title")>
<CFSET Temp = QueryAddRow(Movies, 3)>
<CFSET Temp = QuerySetCell(Movies, "Title", "The Matrix", 1)>
<CFSET Temp = QuerySetCell(Movies, "Title", "Toy Story 2", 2)>
<CFSET Temp = QuerySetCell(Movies, "Title", "The Phantom Menace", 3)>

<CFSET Stars = ListToArray("4,5,3")>
<CFSET ColNum = QueryAddColumn(Movies, "Rating", Stars)>

<CFOUTPUT><P>Rating is column #ColNum#. Columns: #Movies.ColumnList#</P></CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Title</TH><TH>Rating</TH></TR>
<CFOUTPUT QUERY="Movies">
<TR><TD>#Title#</TD><TD>#RepeatString("*", Rating)#</TD></TR>
</CFOUTPUT>
</TABLE>
