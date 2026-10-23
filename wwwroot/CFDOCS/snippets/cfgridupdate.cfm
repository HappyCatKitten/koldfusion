<!--- The edits go to a scratch copy of Departments that is dropped at
      the end, so the sample data never changes. --->
<CFSET Scratch = "GridDemo" & RandRange(1000, 9999)>
<CFQUERY DATASOURCE="cfsnippets">
CREATE TABLE #Scratch# (Dept_ID INTEGER PRIMARY KEY,
    Dept_Name VARCHAR(30), Location VARCHAR(40))
</CFQUERY>
<CFQUERY DATASOURCE="cfsnippets">
INSERT INTO #Scratch# (Dept_ID, Dept_Name, Location)
SELECT Dept_ID, Dept_Name, Location FROM Departments
</CFQUERY>

<CFIF IsDefined("Form.FieldNames")>
  <CFTRY>
    <CFGRIDUPDATE GRID="DeptGrid" DATASOURCE="cfsnippets" TABLENAME="#Scratch#">
  <CFCATCH TYPE="Any">
    <CFOUTPUT><P><B>Update failed:</B> #CFCATCH.Message#</CFOUTPUT>
  </CFCATCH>
  </CFTRY>
  <CFQUERY NAME="After" DATASOURCE="cfsnippets">
  SELECT * FROM #Scratch# ORDER BY Dept_ID
  </CFQUERY>
  <P>After <B>CFGRIDUPDATE</B> the copy holds:
  <TABLE BORDER=1 CELLPADDING=2>
  <CFOUTPUT QUERY="After">
  <TR><TD>#Dept_ID#</TD><TD>#Dept_Name#</TD><TD>#Location#</TD></TR>
  </CFOUTPUT>
  </TABLE>
</CFIF>
<CFQUERY DATASOURCE="cfsnippets">DROP TABLE #Scratch#</CFQUERY>

<CFQUERY NAME="GetDepts" DATASOURCE="cfsnippets">
SELECT Dept_ID, Dept_Name, Location FROM Departments ORDER BY Dept_ID
</CFQUERY>
<P>Edit, tick "Del" or fill in the yellow row, then save:
<CFFORM NAME="Depts" ACTION="cfgridupdate.cfm">
<CFGRID NAME="DeptGrid" QUERY="GetDepts" SELECTMODE="EDIT"
    INSERT="Yes" DELETE="Yes" WIDTH="420">
  <CFGRIDCOLUMN NAME="Dept_ID" HEADER="ID" SELECT="No">
  <CFGRIDCOLUMN NAME="Dept_Name" HEADER="Department">
  <CFGRIDCOLUMN NAME="Location" HEADER="Location">
</CFGRID>
<INPUT TYPE="Submit" VALUE="Save changes">
</CFFORM>
