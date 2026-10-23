<CFTRY>
  <CFSTOREDPROC PROCEDURE="sp_GetDeptStaff" DATASOURCE="cfsnippets">
    <CFPROCPARAM TYPE="In" CFSQLTYPE="CF_SQL_VARCHAR" VALUE="Training" DBVARNAME="@dept">
    <CFPROCRESULT NAME="Staff">
  </CFSTOREDPROC>
  <CFCATCH TYPE="Database">
    <CFOUTPUT>
    <P><B>The procedure call failed</B> (SQLState #CFCATCH.SQLState#):<BR>
    <I>#CFCATCH.Message#</I></P>
    </CFOUTPUT>
    <!--- Fall back on a plain query that does the same job --->
    <CFQUERY NAME="Staff" DATASOURCE="cfsnippets">
    SELECT FirstName, LastName FROM Employees
    WHERE Department = 'Training' ORDER BY LastName
    </CFQUERY>
  </CFCATCH>
</CFTRY>
<P>Training department, from the fallback query:</P>
<UL>
<CFOUTPUT QUERY="Staff"><LI>#FirstName# #LastName#
</CFOUTPUT>
</UL>
