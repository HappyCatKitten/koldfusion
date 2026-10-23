<CFQUERY NAME="GetCourses" DATASOURCE="cfsnippets" MAXROWS="6">
SELECT CorName, CorDesc FROM CourseList
</CFQUERY>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Course</TH><TH>Description (first 30 characters)</TH></TR>
<CFOUTPUT QUERY="GetCourses">
<TR><TD>#CorName#</TD><TD>#Left(CorDesc, 30)#<CFIF Len(CorDesc) GT 30>...</CFIF></TD></TR>
</CFOUTPUT>
</TABLE>
