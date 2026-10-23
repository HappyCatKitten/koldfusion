<CFQUERY NAME="GetCourses" DATASOURCE="cfsnippets">
SELECT CorName FROM CourseList ORDER BY CorName
</CFQUERY>
<P>Courses with "intro" anywhere in the name:</P>
<UL>
<CFOUTPUT QUERY="GetCourses">
<CFIF FindNoCase("intro", CorName)><LI>#CorName# (at position #FindNoCase("intro", CorName)#)</CFIF>
</CFOUTPUT>
</UL>
