<CFSET Employee = StructNew()>
<CFSET Employee.FirstName = "Ann">
<CFSET Employee.LastName = "Achebe">
<CFSET Employee.Phone = "555-0199">
<CFOUTPUT>
<P>The Employee structure has <B>#StructCount(Employee)#</B> keys:
#StructKeyList(Employee, ", ")#</P>
</CFOUTPUT>
