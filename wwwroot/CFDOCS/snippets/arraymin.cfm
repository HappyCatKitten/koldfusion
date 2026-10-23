<CFSET Temps = ListToArray("12,-3,7,0,-8,4")>
<CFOUTPUT>
<P>Overnight temperatures this week: #ArrayToList(Temps, ", ")#</P>
<P>Coldest night: <B>#ArrayMin(Temps)#</B> degrees.
Bring a sweater to the server room.</P>
</CFOUTPUT>
