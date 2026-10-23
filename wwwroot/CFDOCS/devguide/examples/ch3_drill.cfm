<!--- ch3_drill.cfm: employee list with a drill-down detail view --->
<CFPARAM NAME="URL.EmpID" DEFAULT="0">
<CFIF NOT IsNumeric(URL.EmpID)>
  <CFSET URL.EmpID = 0>
</CFIF>

<CFIF URL.EmpID GT 0>
  <!--- Detail view: one employee, joined to the department table --->
  <CFQUERY NAME="GetEmp" DATASOURCE="cfsnippets">
  SELECT e.FirstName, e.LastName, e.Email, e.Phone, e.Department,
         e.StartDate, d.Location
  FROM Employees e, Departments d
  WHERE e.Department = d.Dept_Name
    AND e.Emp_ID = <CFQUERYPARAM VALUE="#URL.EmpID#" CFSQLTYPE="CF_SQL_INTEGER">
  </CFQUERY>
  <CFIF GetEmp.RecordCount IS 0>
    <P>Sorry, there is no employee with that ID.</P>
  <CFELSE>
    <CFOUTPUT QUERY="GetEmp">
    <H3>#FirstName# #LastName#</H3>
    <P>#Department# department, #Location#<BR>
    Phone: #Phone#<BR>
    E-mail: <A HREF="mailto:#Email#">#Email#</A><BR>
    With the company since #DateFormat(StartDate, "mmmm yyyy")#.</P>
    </CFOUTPUT>
  </CFIF>
  <P><A HREF="ch3_drill.cfm">Back to the list</A></P>
<CFELSE>
  <!--- List view --->
  <CFQUERY NAME="GetAll" DATASOURCE="cfsnippets">
  SELECT Emp_ID, FirstName, LastName, Department
  FROM Employees
  ORDER BY LastName, FirstName
  </CFQUERY>
  <H3>Staff Directory</H3>
  <P>Click a name for details.</P>
  <CFOUTPUT QUERY="GetAll">
    <A HREF="ch3_drill.cfm?EmpID=#Emp_ID#">#LastName#, #FirstName#</A>
    <FONT SIZE="1">#Department#</FONT><BR>
  </CFOUTPUT>
</CFIF>
