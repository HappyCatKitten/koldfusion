<CFPARAM NAME="URL.Dept" DEFAULT="Training">
<CFTRANSACTION>
  <CFSTOREDPROC PROCEDURE="AddEmployee" DATASOURCE="cfsnippets" RETURNCODE="Yes">
    <CFPROCPARAM CFSQLTYPE="CF_SQL_VARCHAR" DBVARNAME="@FirstName" VALUE="Ramona">
    <CFPROCPARAM CFSQLTYPE="CF_SQL_VARCHAR" DBVARNAME="@LastName" VALUE="Flowers">
    <CFPROCPARAM CFSQLTYPE="CF_SQL_VARCHAR" DBVARNAME="@Department" VALUE="#URL.Dept#">
    <CFPROCPARAM TYPE="Out" CFSQLTYPE="CF_SQL_INTEGER" DBVARNAME="@NewID" VARIABLE="NewID">
  </CFSTOREDPROC>
  <!--- this is only a demonstration: undo the insert --->
  <CFTRANSACTION ACTION="ROLLBACK"/>
</CFTRANSACTION>

<CFOUTPUT>
<CFSWITCH EXPRESSION="#CFSTOREDPROC.StatusCode#">
  <CFCASE VALUE="0"><P>Ramona Flowers joined #URL.Dept# as employee number #NewID#.</P></CFCASE>
  <CFCASE VALUE="1"><P>There is no #URL.Dept# department.</P></CFCASE>
  <CFCASE VALUE="2"><P>Ramona Flowers is already employee number #NewID#.</P></CFCASE>
</CFSWITCH>
<P><A HREF="storedproc.cfm?Dept=Sales">Try Sales</A> |
<A HREF="storedproc.cfm?Dept=Catering">Try a department that does not exist</A></P>
</CFOUTPUT>
