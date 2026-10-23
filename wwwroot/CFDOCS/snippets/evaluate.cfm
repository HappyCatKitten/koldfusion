<!--- three "form fields" with numbered names --->
<CFSET Item1 = "56K modem">
<CFSET Item2 = "Netscape 4.7 CD">
<CFSET Item3 = "Y2K patch">
<UL>
<CFLOOP INDEX="i" FROM="1" TO="3">
  <CFOUTPUT><LI>Item#i# = #Evaluate("Item#i#")#</CFOUTPUT>
</CFLOOP>
</UL>
<CFSET Formula = "Len(Item1) * 2 + 1">
<CFOUTPUT>
<P>Evaluate("#Formula#") = #Evaluate(Formula)#
<P>Evaluate("Total = 10", "Total * 3") = #Evaluate("Total = 10", "Total * 3")#
</CFOUTPUT>
