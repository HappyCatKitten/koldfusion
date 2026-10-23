<CFQUERY NAME="GetParks" DATASOURCE="cfsnippets">
SELECT ParkName, State FROM Parks ORDER BY ParkName
</CFQUERY>
<P>Parks whose name contains "canyon" or "mesa", in any case:</P>
<UL>
<CFOUTPUT QUERY="GetParks">
<CFIF REFindNoCase("canyon|mesa", ParkName)><LI>#ParkName#, #State#</CFIF>
</CFOUTPUT>
</UL>
