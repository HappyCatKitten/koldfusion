<!--- Defaults for the form fields; the form posts back to this page --->
<CFPARAM NAME="URL.Department" DEFAULT="Engineering">
<CFPARAM NAME="URL.MinSalary" DEFAULT="50000">

<FORM ACTION="cfparam.cfm" METHOD="GET">
Department <INPUT TYPE="Text" NAME="Department" VALUE="<CFOUTPUT>#URL.Department#</CFOUTPUT>" SIZE=12>
earning at least <INPUT TYPE="Text" NAME="MinSalary" VALUE="<CFOUTPUT>#URL.MinSalary#</CFOUTPUT>" SIZE=8>
<INPUT TYPE="Submit" VALUE="Show">
</FORM>

<CFTRY>
  <CFPARAM NAME="URL.MinSalary" TYPE="numeric">
  <CFQUERY NAME="Staff" DATASOURCE="cfsnippets">
  SELECT FirstName, LastName, Salary FROM Employees
  WHERE Department = '#URL.Department#' AND Salary >= #URL.MinSalary#
  ORDER BY Salary DESC
  </CFQUERY>
  <CFOUTPUT><P>#Staff.RecordCount# employee(s) found.</P></CFOUTPUT>
  <UL>
  <CFOUTPUT QUERY="Staff"><LI>#FirstName# #LastName#, #DollarFormat(Salary)#</CFOUTPUT>
  </UL>
<CFCATCH TYPE="Application">
  <CFOUTPUT><P><B>#CFCATCH.Message#</B> #CFCATCH.Detail#</P></CFOUTPUT>
</CFCATCH>
</CFTRY>
