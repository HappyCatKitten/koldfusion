<CFQUERY NAME="GetDepts" DATASOURCE="cfsnippets">
SELECT Department, COUNT(*) AS Staff FROM Employees GROUP BY Department ORDER BY Department
</CFQUERY>
<PRE>
<CFOUTPUT QUERY="GetDepts">#LJustify(Department, 15)# #RepeatString("*", Staff)# #Staff#
</CFOUTPUT><CFOUTPUT>#RepeatString("=", 40)#</CFOUTPUT>
</PRE>
