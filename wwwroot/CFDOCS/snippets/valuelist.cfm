<CFQUERY NAME="GetSales" DATASOURCE="cfsnippets">
SELECT FirstName, LastName
FROM Employees
WHERE Department = 'Sales'
ORDER BY LastName
</CFQUERY>
<CFOUTPUT>
<P>Sales staff (#GetSales.RecordCount#): #ValueList(GetSales.LastName, ", ")#</P>
<P>As a list, ListLen = #ListLen(ValueList(GetSales.LastName))#
and the first one is #ListFirst(ValueList(GetSales.LastName))#.</P>
</CFOUTPUT>
