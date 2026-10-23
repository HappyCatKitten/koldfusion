<CFPARAM NAME="URL.CFGRIDKEY" DEFAULT="">

<CFIF IsNumeric(URL.CFGRIDKEY)>
  <CFQUERY NAME="GetOne" DATASOURCE="cfsnippets">
  SELECT FirstName, LastName, Email, StartDate
  FROM Employees WHERE Emp_ID = #Val(URL.CFGRIDKEY)#
  </CFQUERY>
  <CFOUTPUT QUERY="GetOne">
  <P><B>#FirstName# #LastName#</B> (#Email#) joined us on
  #DateFormat(StartDate, "mmmm d, yyyy")#.</P>
  </CFOUTPUT>
</CFIF>

<CFQUERY NAME="GetEmps" DATASOURCE="cfsnippets" MAXROWS="8">
SELECT Emp_ID, LastName, FirstName, Department, Phone
FROM Employees ORDER BY LastName
</CFQUERY>

<P>Click a name for details:
<CFFORM NAME="Staff" ACTION="cfgrid.cfm">
<CFGRID NAME="EmpGrid" QUERY="GetEmps" WIDTH="460" FONT="Verdana"
    HREF="cfgrid.cfm" HREFKEY="Emp_ID">
  <CFGRIDCOLUMN NAME="LastName" HEADER="Last name">
  <CFGRIDCOLUMN NAME="FirstName" HEADER="First name">
  <CFGRIDCOLUMN NAME="Department" HEADER="Department">
  <CFGRIDCOLUMN NAME="Phone" HEADER="Phone">
</CFGRID>
</CFFORM>
