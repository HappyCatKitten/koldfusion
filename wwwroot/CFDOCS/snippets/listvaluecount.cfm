<CFQUERY NAME="GetStaff" DATASOURCE="cfsnippets">
SELECT Department FROM Employees
</CFQUERY>
<CFSET Depts = ValueList(GetStaff.Department)>
<CFQUERY NAME="GetDepts" DATASOURCE="cfsnippets">
SELECT Dept_Name FROM Departments ORDER BY Dept_Name
</CFQUERY>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Department</TH><TH>Employees</TH></TR>
<CFOUTPUT QUERY="GetDepts">
<TR><TD>#Dept_Name#</TD><TD ALIGN="right">#ListValueCount(Depts, Dept_Name)#</TD></TR>
</CFOUTPUT>
</TABLE>
