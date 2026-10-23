<P>Five random numbers (reload for new ones):
<UL>
<CFLOOP INDEX="i" FROM="1" TO="5">
<CFOUTPUT><LI>#Rand()#</CFOUTPUT>
</CFLOOP>
</UL>
<CFSET Coin = IIf(Rand() LT 0.5, DE("Heads"), DE("Tails"))>
<CFOUTPUT><P>Coin toss: <B>#Coin#</B></CFOUTPUT>
