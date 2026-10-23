<!--- Try ?Dept=Marketing&MinID=7 or ?MinID=abc --->
<CFPARAM NAME="URL.Dept" DEFAULT="Engineering">
<CFPARAM NAME="URL.MinID" DEFAULT="10">
<CFTRY>
  <CFQUERY NAME="GetStaff" DATASOURCE="cfsnippets">
  SELECT Emp_ID, FirstName, LastName
  FROM Employees
  WHERE Department = <CFQUERYPARAM VALUE="#URL.Dept#" CFSQLTYPE="CF_SQL_VARCHAR" MAXLENGTH="35">
    AND Emp_ID >= <CFQUERYPARAM VALUE="#URL.MinID#" CFSQLTYPE="CF_SQL_INTEGER">
  ORDER BY Emp_ID
  </CFQUERY>
  <CFOUTPUT><H3>#HTMLEditFormat(URL.Dept)#, employee ID #HTMLEditFormat(URL.MinID)# and up</H3></CFOUTPUT>
  <TABLE BORDER=1 CELLPADDING=3>
  <TR><TH>ID</TH><TH>Name</TH></TR>
  <CFOUTPUT QUERY="GetStaff">
  <TR><TD>#Emp_ID#</TD><TD>#FirstName# #LastName#</TD></TR>
  </CFOUTPUT>
  </TABLE>
  <CFCATCH TYPE="Database">
    <CFOUTPUT><P><B>Rejected:</B> #CFCATCH.Message#</P></CFOUTPUT>
  </CFCATCH>
</CFTRY>

<!--- A hostile value never reaches the database --->
<CFTRY>
  <CFQUERY NAME="Sneaky" DATASOURCE="cfsnippets">
  SELECT * FROM Employees
  WHERE Emp_ID = <CFQUERYPARAM VALUE="3; DELETE FROM Employees" CFSQLTYPE="CF_SQL_INTEGER">
  </CFQUERY>
  <CFCATCH TYPE="Database">
    <CFOUTPUT><P><B>Also rejected:</B> #CFCATCH.Message#</P></CFOUTPUT>
  </CFCATCH>
</CFTRY>
