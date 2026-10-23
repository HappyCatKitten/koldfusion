<CFPARAM NAME="Form.Criteria" DEFAULT="web">

<!--- Set up the course index (see CFINDEX) so this page stands alone --->
<CFTRY>
  <CFCOLLECTION ACTION="CREATE" COLLECTION="snippets">
<CFCATCH TYPE="Any"></CFCATCH>
</CFTRY>
<CFQUERY NAME="GetCourses" DATASOURCE="cfsnippets">
SELECT Course_ID, Dept_ID, CorName, CorLevel, CorDesc FROM CourseList
</CFQUERY>
<CFINDEX COLLECTION="snippets" ACTION="UPDATE" QUERY="GetCourses"
    KEY="Course_ID" TITLE="CorName" BODY="CorName,CorDesc"
    CUSTOM1="Dept_ID" CUSTOM2="CorLevel">

<CFSEARCH NAME="Results" COLLECTION="snippets"
    CRITERIA="#Form.Criteria#" MAXROWS="10">

<CFOUTPUT>
<FORM ACTION="cfsearch.cfm" METHOD="POST">
Search the course catalog:
<INPUT TYPE="Text" NAME="Criteria" VALUE="#HTMLEditFormat(Form.Criteria)#" SIZE="25">
<INPUT TYPE="Submit" VALUE="Search"><BR>
<FONT SIZE="1">Try: chemistry NOT organic, "safety goggles", crypt*, web, database</FONT>
</FORM>
<P>#Results.RecordCount# match(es) for <B>#HTMLEditFormat(Form.Criteria)#</B>
</CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Score</TH><TH>Course</TH><TH>Dept</TH><TH>Level</TH></TR>
<CFOUTPUT QUERY="Results">
<TR><TD>#Score#</TD><TD>#Title#</TD><TD>#Custom1#</TD><TD>#Custom2#</TD></TR>
</CFOUTPUT>
</TABLE>
