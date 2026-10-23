<CFPARAM NAME="URL.CFGRIDKEY" DEFAULT="">

<CFQUERY NAME="GetCourses" DATASOURCE="cfsnippets">
SELECT Course_ID, CorNumber, CorName, CorLevel, CorDesc
FROM CourseList WHERE Dept_ID = 'CS' ORDER BY CorNumber
</CFQUERY>

<H3>Computer Science courses</H3>
<CFFORM NAME="Catalog" ACTION="cfgridcolumn.cfm">
<CFGRID NAME="CourseGrid" QUERY="GetCourses" WIDTH="440">
  <CFGRIDCOLUMN NAME="Course_ID" DISPLAY="No">
  <CFGRIDCOLUMN NAME="CorNumber" HEADER="No." WIDTH="40" DATAALIGN="Right">
  <CFGRIDCOLUMN NAME="CorName" HEADER="Course (click for details)"
      HREF="cfgridcolumn.cfm" HREFKEY="Course_ID">
  <CFGRIDCOLUMN NAME="CorLevel" HEADER="Level" DATAALIGN="Center">
</CFGRID>
</CFFORM>

<CFLOOP QUERY="GetCourses">
  <CFIF Course_ID EQ URL.CFGRIDKEY>
    <CFOUTPUT><P><B>CS #CorNumber#, #CorName#:</B> #CorDesc#</CFOUTPUT>
  </CFIF>
</CFLOOP>
