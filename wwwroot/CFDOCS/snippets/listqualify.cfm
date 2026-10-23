<CFSET Wanted = "Sales,Training">
<CFSET InList = ListQualify(Wanted, "'")>
<CFQUERY NAME="GetPeople" DATASOURCE="cfsnippets">
SELECT FirstName, LastName, Department FROM Employees
WHERE Department IN (#PreserveSingleQuotes(InList)#)
ORDER BY Department, LastName
</CFQUERY>
<CFOUTPUT>
<P>IN clause: (#InList#)</P>
<P>Only the text elements: #ListQualify("Joe,42,Jane,3.14", """", ",", "CHAR")#</P>
</CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<CFOUTPUT QUERY="GetPeople">
<TR><TD>#Department#</TD><TD>#FirstName# #LastName#</TD></TR>
</CFOUTPUT>
</TABLE>
