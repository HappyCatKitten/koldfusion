<CFSET Start = GetTickCount()>
<CFSET Total = 0>
<CFLOOP INDEX="i" FROM="1" TO="20000">
  <CFSET Total = Total + i>
</CFLOOP>
<CFSET Elapsed = GetTickCount() - Start>
<CFOUTPUT>
<P>Adding up 1 to 20,000 gives #NumberFormat(Total)#.
<P>That took #Elapsed# ms. On a Pentium II/300 in 1999 you could have gone for coffee.
</CFOUTPUT>
