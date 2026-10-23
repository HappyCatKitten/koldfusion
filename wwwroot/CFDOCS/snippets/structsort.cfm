<CFQUERY NAME="Staff" DATASOURCE="cfsnippets" MAXROWS="6">
SELECT Emp_ID, LastName, Salary FROM Employees ORDER BY Emp_ID
</CFQUERY>
<CFSET People = StructNew()>
<CFLOOP QUERY="Staff">
  <CFSET People[LastName] = StructNew()>
  <CFSET People[LastName].Salary = Salary>
</CFLOOP>
<CFSET ByPay = StructSort(People, "numeric", "desc", "Salary")>
<OL>
<CFLOOP FROM="1" TO="#ArrayLen(ByPay)#" INDEX="i">
  <CFOUTPUT><LI>#ByPay[i]#: #DollarFormat(People[ByPay[i]].Salary)#</CFOUTPUT>
</CFLOOP>
</OL>
