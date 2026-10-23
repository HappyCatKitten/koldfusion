<CFQUERY NAME="GetDepts" DATASOURCE="cfsnippets">
SELECT Dept_Name, Location FROM Departments
</CFQUERY>
<UL>
<CFOUTPUT QUERY="GetDepts">
<LI>#UCase(Dept_Name)# (#Location#)
</CFOUTPUT>
</UL>
