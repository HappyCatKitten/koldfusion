<CFSET Lineup = "Monday,Tuesday,Thursday,Friday">
<CFSET Lineup = ListInsertAt(Lineup, 3, "Wednesday")>
<CFSET Lineup = ListInsertAt(Lineup, 1, "Sunday")>
<CFSET Lineup = ListAppend(Lineup, "Saturday")>
<OL>
<CFLOOP INDEX="Day" LIST="#Lineup#">
  <CFOUTPUT><LI>#Day#</CFOUTPUT>
</CFLOOP>
</OL>
