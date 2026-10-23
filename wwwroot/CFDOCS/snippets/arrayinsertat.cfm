<CFSET Planets = ListToArray("Mercury,Earth,Mars")>
<CFSET Temp = ArrayInsertAt(Planets, 2, "Venus")>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Position</TH><TH>Planet</TH></TR>
<CFLOOP INDEX="i" FROM="1" TO="#ArrayLen(Planets)#">
<TR><TD ALIGN="CENTER">#i#</TD><TD>#Planets[i]#</TD></TR>
</CFLOOP>
</TABLE>
</CFOUTPUT>
