<!--- ch3_group.cfm: national parks, grouped by region --->
<CFQUERY NAME="GetParks" DATASOURCE="cfsnippets">
SELECT Region, ParkName, ParkType, City, State
FROM Parks
ORDER BY Region, ParkName
</CFQUERY>

<CFOUTPUT><H3>#GetParks.RecordCount# parks in the system</H3></CFOUTPUT>

<CFOUTPUT QUERY="GetParks" GROUP="Region">
  <P><B>#Region#</B></P>
  <UL>
  <CFOUTPUT>
    <LI>#ParkName# <FONT SIZE="1">(#ParkType#, #City#, #State#)</FONT>
  </CFOUTPUT>
  </UL>
</CFOUTPUT>
