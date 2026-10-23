<!--- Try to start Excel; on UNIX, plan B is a plain HTML table --->
<CFTRY>
  <CFOBJECT TYPE="COM" ACTION="Create" CLASS="Excel.Application" NAME="Excel">
  <P>Excel is running. Remarkable.</P>
  <CFCATCH TYPE="Object">
    <CFOUTPUT>
    <P><B>No COM today:</B> #CFCATCH.Message#<BR>
    <I>#CFCATCH.Detail#</I></P>
    </CFOUTPUT>
    <CFQUERY NAME="Depts" DATASOURCE="cfsnippets">
    SELECT Dept_Name, Location FROM Departments ORDER BY Dept_Name
    </CFQUERY>
    <P>Here is the spreadsheet as an HTML table instead:</P>
    <TABLE BORDER=1 CELLPADDING=3>
    <CFOUTPUT QUERY="Depts"><TR><TD>#Dept_Name#</TD><TD>#Location#</TD></TR></CFOUTPUT>
    </TABLE>
  </CFCATCH>
</CFTRY>
