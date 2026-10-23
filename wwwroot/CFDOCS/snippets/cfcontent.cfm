<!--- Everything before CFCONTENT is thrown away by RESET="Yes" --->
<H1>You will not see this heading</H1>
<CFQUERY NAME="Depts" DATASOURCE="cfsnippets">
SELECT Dept_Name, Location FROM Departments ORDER BY Dept_Name
</CFQUERY>
<CFCONTENT TYPE="text/plain" RESET="Yes"><CFOUTPUT>KoldFusion department report (text/plain)
Generated #DateFormat(Now(), "mm/dd/yyyy")# #TimeFormat(Now(), "HH:mm")#

<CFLOOP QUERY="Depts">#LJustify(Dept_Name, 16)##Location#
</CFLOOP>
#Depts.RecordCount# departments. <B>Tags</B> are shown as text in a text/plain page.
</CFOUTPUT>
