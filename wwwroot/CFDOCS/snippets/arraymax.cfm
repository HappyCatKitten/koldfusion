<CFSET Scores = ListToArray("4200,15750,980,8800")>
<CFOUTPUT>
<P>Pinball scores: #ArrayToList(Scores, ", ")#</P>
<P>High score: <B>#NumberFormat(ArrayMax(Scores), ",")#</B><BR>
Low score: #NumberFormat(ArrayMin(Scores), ",")#</P>
</CFOUTPUT>
