<CFSET Countdown = "">
<CFLOOP INDEX="I" FROM="1" TO="10">
  <CFSET Countdown = ListPrepend(Countdown, I)>
</CFLOOP>
<CFSET Countdown = ListAppend(Countdown, "Happy New Year!")>
<CFOUTPUT>
<P><B>#ListChangeDelims(Countdown, "... ")#</B></P>
</CFOUTPUT>
