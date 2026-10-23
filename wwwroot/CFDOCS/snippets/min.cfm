<CFQUERY NAME="GetEmps" DATASOURCE="cfsnippets">
SELECT FirstName, LastName FROM Employees
</CFQUERY>
<CFSET StartRow = 21>
<CFSET EndRow = Min(StartRow + 9, GetEmps.RecordCount)>
<CFOUTPUT>
<P>Min(3, 7) = #Min(3, 7)#, Min(-1, -1.5) = #Min(-1, -1.5)#
<P>Showing employees #StartRow# to #EndRow# of #GetEmps.RecordCount#:
</CFOUTPUT>
<UL>
<CFOUTPUT QUERY="GetEmps" STARTROW="#StartRow#" MAXROWS="10"><LI>#FirstName# #LastName#</CFOUTPUT>
</UL>
