<CFQUERY NAME="GetDepts" DATASOURCE="cfsnippets">
SELECT Dept_Name, Location FROM Departments
</CFQUERY>
<PRE>
<CFOUTPUT QUERY="GetDepts">#LJustify(Dept_Name, 16)##Location#
</CFOUTPUT></PRE>
