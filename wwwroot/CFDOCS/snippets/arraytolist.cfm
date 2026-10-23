<CFSET Colors = ArrayNew(1)>
<CFSET Colors[1] = "Red">
<CFSET Colors[2] = "Green">
<CFSET Colors[3] = "Blue">
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>ArrayToList(Colors)</TD><TD>#ArrayToList(Colors)#</TD></TR>
<TR><TD>ArrayToList(Colors, " + ")</TD><TD>#ArrayToList(Colors, " + ")#</TD></TR>
<TR><TD>ListLen of the result</TD><TD>#ListLen(ArrayToList(Colors))#</TD></TR>
</TABLE>
</CFOUTPUT>
