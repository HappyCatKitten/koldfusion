<CFSET Team = QueryNew("Name, Role")>
<CFLOOP LIST="Ann:Coder,Bob:Tester,Cy:Pizza runner" INDEX="Pair">
  <CFSET Rows = QueryAddRow(Team)>
  <CFSET Temp = QuerySetCell(Team, "Name", ListFirst(Pair, ":"))>
  <CFSET Temp = QuerySetCell(Team, "Role", ListLast(Pair, ":"))>
</CFLOOP>
<CFOUTPUT><P>The query has #Rows# rows (RecordCount = #Team.RecordCount#).</P></CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<CFOUTPUT QUERY="Team">
<TR><TD>#CurrentRow#</TD><TD>#Name#</TD><TD>#Role#</TD></TR>
</CFOUTPUT>
</TABLE>
