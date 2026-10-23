<!--- AddEmployee returns the new Emp_ID in an output parameter and a status code:
      0 = added, 1 = no such department, 2 = already on file.
      The transaction is rolled back, so the sample data stays the same. --->
<CFTRANSACTION>
  <CFSTOREDPROC PROCEDURE="AddEmployee" DATASOURCE="cfsnippets" RETURNCODE="Yes">
    <CFPROCPARAM TYPE="In" CFSQLTYPE="CF_SQL_VARCHAR" DBVARNAME="@FirstName" VALUE="Wendy">
    <CFPROCPARAM TYPE="In" CFSQLTYPE="CF_SQL_VARCHAR" DBVARNAME="@LastName" VALUE="Okonkwo">
    <CFPROCPARAM TYPE="In" CFSQLTYPE="CF_SQL_VARCHAR" DBVARNAME="@Department" VALUE="Training">
    <CFPROCPARAM TYPE="In" CFSQLTYPE="CF_SQL_MONEY" DBVARNAME="@Salary" VALUE="42500">
    <CFPROCPARAM TYPE="Out" CFSQLTYPE="CF_SQL_INTEGER" DBVARNAME="@NewID" VARIABLE="NewID">
  </CFSTOREDPROC>
  <CFSET Status = CFSTOREDPROC.StatusCode>
  <CFQUERY NAME="Added" DATASOURCE="cfsnippets">
  SELECT FirstName, LastName, Department, Salary FROM Employees WHERE Emp_ID = #NewID#
  </CFQUERY>
  <CFTRANSACTION ACTION="Rollback"/>
</CFTRANSACTION>

<CFOUTPUT>
<P>Status #Status#: employee number #NewID# is
#Added.FirstName# #Added.LastName# (#Added.Department#, #DollarFormat(Added.Salary)#).</P>
</CFOUTPUT>
