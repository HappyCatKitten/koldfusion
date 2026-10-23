<CFSET Podium = ListToArray("Silver,Gold,Bronze")>
<CFOUTPUT>
<P>Before: #ArrayToList(Podium, " | ")#</P>
<CFSET Temp = ArraySwap(Podium, 1, 2)>
<P>After ArraySwap(Podium, 1, 2): #ArrayToList(Podium, " | ")#</P>
</CFOUTPUT>
