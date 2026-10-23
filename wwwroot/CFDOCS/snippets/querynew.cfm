<CFSET Modems = QueryNew("Speed, Year")>
<CFSET Temp = QueryAddRow(Modems, 3)>
<CFSET Temp = QuerySetCell(Modems, "Speed", "14.4K", 1)>
<CFSET Temp = QuerySetCell(Modems, "Year", 1991, 1)>
<CFSET Temp = QuerySetCell(Modems, "Speed", "28.8K", 2)>
<CFSET Temp = QuerySetCell(Modems, "Year", 1994, 2)>
<CFSET Temp = QuerySetCell(Modems, "Speed", "56K", 3)>
<CFSET Temp = QuerySetCell(Modems, "Year", 1998, 3)>

<CFOUTPUT><P>RecordCount: #Modems.RecordCount#, ColumnList: #Modems.ColumnList#</P></CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Speed</TH><TH>Year</TH></TR>
<CFOUTPUT QUERY="Modems">
<TR><TD>#Speed#</TD><TD>#Year#</TD></TR>
</CFOUTPUT>
</TABLE>
