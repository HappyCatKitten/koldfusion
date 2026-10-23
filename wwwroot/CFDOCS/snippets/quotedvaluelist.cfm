<CFQUERY NAME="GetDepts" DATASOURCE="cfsnippets">
SELECT Dept_Name FROM Departments
WHERE Dept_Name IN ('Sales', 'Training')
</CFQUERY>
<CFQUERY NAME="GetPeople" DATASOURCE="cfsnippets">
SELECT FirstName, LastName, Department FROM Employees
WHERE Department IN (#PreserveSingleQuotes(QuotedValueList(GetDepts.Dept_Name))#)
ORDER BY Department, LastName
</CFQUERY>
<CFOUTPUT>
<P>QuotedValueList: <TT>#QuotedValueList(GetDepts.Dept_Name)#</TT></P>
</CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<CFOUTPUT QUERY="GetPeople">
<TR><TD>#Department#</TD><TD>#FirstName# #LastName#</TD></TR>
</CFOUTPUT>
</TABLE>
