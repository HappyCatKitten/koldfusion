<!--- One pass per region, one line per state, every park listed --->
<CFQUERY NAME="GetParks" DATASOURCE="cfsnippets">
SELECT ParkName, Region, State
FROM Parks
WHERE Region IN ('Southwest', 'Pacific West')
ORDER BY Region, State, ParkName
</CFQUERY>

<CFOUTPUT QUERY="GetParks" GROUP="Region">
  <H4>#Region#</H4>
  <UL>
  <CFOUTPUT GROUP="State">
    <LI><B>#State#</B>:
    <CFOUTPUT>&middot; #ParkName# </CFOUTPUT>
  </CFOUTPUT>
  </UL>
</CFOUTPUT>

<H4>Rows 3 and 4 only (STARTROW="3" MAXROWS="2")</H4>
<TABLE BORDER=1 CELLPADDING=3>
<CFOUTPUT QUERY="GetParks" STARTROW="3" MAXROWS="2">
  <TR><TD>#CurrentRow#</TD><TD>#ParkName#</TD><TD>#State#</TD></TR>
</CFOUTPUT>
</TABLE>
