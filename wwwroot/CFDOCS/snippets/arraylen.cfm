<!--- A small two-dimensional array: 2 rows, 3 columns --->
<CFSET Grid = ArrayNew(2)>
<CFSET Grid[1][1] = "A1"><CFSET Grid[1][2] = "B1"><CFSET Grid[1][3] = "C1">
<CFSET Grid[2][1] = "A2"><CFSET Grid[2][2] = "B2"><CFSET Grid[2][3] = "C2">

<CFOUTPUT>
<P>ArrayLen(Grid) = #ArrayLen(Grid)# rows,
ArrayLen(Grid[1]) = #ArrayLen(Grid[1])# columns.</P>
<TABLE BORDER=1 CELLPADDING=4>
<CFLOOP INDEX="r" FROM="1" TO="#ArrayLen(Grid)#">
  <TR><CFLOOP INDEX="c" FROM="1" TO="#ArrayLen(Grid[r])#"><TD>#Grid[r][c]#</TD></CFLOOP></TR>
</CFLOOP>
</TABLE>
</CFOUTPUT>
