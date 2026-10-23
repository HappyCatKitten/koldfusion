<CFSET Countdown = ListToArray("2,1,Happy New Year!")>
<CFSET Temp = ArrayPrepend(Countdown, "3")>
<CFSET Temp = ArrayPrepend(Countdown, "4")>
<CFOUTPUT>
<P>#ArrayToList(Countdown, " ... ")#</P>
<P>First element: <B>#Countdown[1]#</B></P>
</CFOUTPUT>
