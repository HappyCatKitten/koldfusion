<CFQUERY NAME="Courses" DATASOURCE="cfsnippets" MAXROWS="6">
SELECT CorNumber, CorName, CorLevel FROM CourseList ORDER BY CorNumber
</CFQUERY>
<P>Three alignments in a text table:</P>
<CFTABLE QUERY="Courses" COLHEADERS HEADERLINES="1">
  <CFCOL HEADER="No." WIDTH="6" ALIGN="Right" TEXT="#CorNumber#">
  <CFCOL HEADER="Course" WIDTH="34" ALIGN="Left" TEXT="#CorName#">
  <CFCOL HEADER="Level" WIDTH="14" ALIGN="Center" TEXT="#CorLevel#">
</CFTABLE>
