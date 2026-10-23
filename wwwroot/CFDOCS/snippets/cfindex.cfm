<!--- Make sure the "snippets" collection exists --->
<CFTRY>
  <CFCOLLECTION ACTION="CREATE" COLLECTION="snippets">
<CFCATCH TYPE="Any"><!--- it already does ---></CFCATCH>
</CFTRY>

<CFQUERY NAME="GetCourses" DATASOURCE="cfsnippets">
SELECT Course_ID, Dept_ID, CorName, CorLevel, CorDesc
FROM CourseList
</CFQUERY>

<!--- One document per row; the key is the primary key --->
<CFINDEX COLLECTION="snippets" ACTION="UPDATE" TYPE="CUSTOM"
    QUERY="GetCourses" KEY="Course_ID" TITLE="CorName"
    BODY="CorName,CorDesc" CUSTOM1="Dept_ID" CUSTOM2="CorLevel">

<CFOUTPUT>
<P>Indexed #GetCourses.RecordCount# courses into the collection <B>snippets</B>.
A few of the documents now in it:
</CFOUTPUT>

<CFSEARCH NAME="Peek" COLLECTION="snippets" CRITERIA="*" MAXROWS="6">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Key</TH><TH>Title</TH><TH>Custom1</TH><TH>Custom2</TH></TR>
<CFOUTPUT QUERY="Peek">
<TR><TD>#Key#</TD><TD>#Title#</TD><TD>#Custom1#</TD><TD>#Custom2#</TD></TR>
</CFOUTPUT>
</TABLE>
