<CFTRY>
  <CFSTOREDPROC PROCEDURE="sp_DeptReport" DATASOURCE="cfsnippets">
    <CFPROCRESULT NAME="Depts" RESULTSET="1">
    <CFPROCRESULT NAME="Courses" RESULTSET="2" MAXROWS="5">
  </CFSTOREDPROC>
  <CFCATCH TYPE="Database">
    <P>No stored procedures on this driver. Running the two queries by hand instead.</P>
    <CFQUERY NAME="Depts" DATASOURCE="cfsnippets">
    SELECT Dept_Name, Location FROM Departments ORDER BY Dept_Name
    </CFQUERY>
    <CFQUERY NAME="Courses" DATASOURCE="cfsnippets" MAXROWS="5">
    SELECT CorName, CorLevel FROM CourseList ORDER BY CorName
    </CFQUERY>
  </CFCATCH>
</CFTRY>
<CFOUTPUT>
<P>IsQuery(Depts): #IsQuery(Depts)#, IsQuery(Courses): #IsQuery(Courses)#</P>
</CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Department</TH><TH>Location</TH></TR>
<CFOUTPUT QUERY="Depts"><TR><TD>#Dept_Name#</TD><TD>#Location#</TD></TR>
</CFOUTPUT>
</TABLE>
<UL>
<CFOUTPUT QUERY="Courses"><LI>#CorName# (#CorLevel#)
</CFOUTPUT>
</UL>
