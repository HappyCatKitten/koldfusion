<CFQUERY NAME="GetPeople" DATASOURCE="cfsnippets" MAXROWS="5">
SELECT FirstName, LastName FROM Employees ORDER BY LastName
</CFQUERY>
<P>Suggested login names:</P>
<UL>
<CFOUTPUT QUERY="GetPeople">
<LI>#FirstName# #LastName#: #LCase(Left(FirstName, 1) & LastName)#
</CFOUTPUT>
</UL>
