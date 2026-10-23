<!--- List the engineers, newest first --->
<CFQUERY NAME="GetEngineers" DATASOURCE="cfsnippets">
SELECT FirstName, LastName, StartDate
FROM Employees
WHERE Department = 'Engineering'
ORDER BY StartDate DESC
</CFQUERY>

<H3>Engineering department</H3>
<CFOUTPUT>
<P>The query returned #GetEngineers.RecordCount# rows
in #CFQUERY.ExecutionTime# ms. Columns: #GetEngineers.ColumnList#</P>
</CFOUTPUT>
<UL>
<CFOUTPUT QUERY="GetEngineers">
  <LI>#FirstName# #LastName#, since #DateFormat(StartDate, "mmmm d, yyyy")#
</CFOUTPUT>
</UL>
