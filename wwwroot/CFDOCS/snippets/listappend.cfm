<CFQUERY NAME="GetDepts" DATASOURCE="cfsnippets">
SELECT Dept_Name FROM Departments
</CFQUERY>
<CFSET DeptList = "">
<CFLOOP QUERY="GetDepts">
  <CFSET DeptList = ListAppend(DeptList, Dept_Name)>
</CFLOOP>
<CFOUTPUT>
<P>Departments: <B>#DeptList#</B></P>
<P>With a semicolon: <B>#ListAppend("red;green", "blue", ";")#</B></P>
<P>Appended to an empty list: <B>#ListAppend("", "lonely")#</B></P>
</CFOUTPUT>
