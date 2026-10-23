<CFSET Planets = "Mercury,Venus,Earth,Mars,Jupiter,Saturn,Uranus,Neptune,Pluto">
<CFSET Pos = ListFind(Planets, "Earth")>
<CFOUTPUT>
<P>Before: #Planets#</P>
<P>Without element 1: #ListDeleteAt(Planets, 1)#</P>
<P>Without "Earth" (element #Pos#): #ListDeleteAt(Planets, Pos)#</P>
<P>Without the last one: #ListDeleteAt(Planets, ListLen(Planets))#</P>
</CFOUTPUT>
