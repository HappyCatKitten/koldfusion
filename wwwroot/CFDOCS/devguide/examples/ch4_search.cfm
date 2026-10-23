<!--- ch4_search.cfm: search the employee table --->
<CFPARAM NAME="Form.LastName" DEFAULT="">
<CFPARAM NAME="Form.Department" DEFAULT="">

<CFQUERY NAME="GetDepts" DATASOURCE="cfsnippets">
SELECT Dept_Name FROM Departments ORDER BY Dept_Name
</CFQUERY>

<FORM ACTION="ch4_search.cfm" METHOD="POST">
<CFOUTPUT>
Last name starts with:
<INPUT TYPE="text" NAME="LastName" SIZE="15" VALUE="#HTMLEditFormat(Form.LastName)#">
in
</CFOUTPUT>
<SELECT NAME="Department">
  <OPTION VALUE="">any department
  <CFOUTPUT QUERY="GetDepts">
  <OPTION VALUE="#Dept_Name#" <CFIF Dept_Name IS Form.Department>SELECTED</CFIF>>#Dept_Name#
  </CFOUTPUT>
</SELECT>
<INPUT TYPE="submit" VALUE="Search">
</FORM>

<CFQUERY NAME="Found" DATASOURCE="cfsnippets">
SELECT FirstName, LastName, Department, Phone
FROM Employees
WHERE 1 = 1
<CFIF Trim(Form.LastName) IS NOT "">
  AND LastName LIKE <CFQUERYPARAM VALUE="#Trim(Form.LastName)#%" CFSQLTYPE="CF_SQL_VARCHAR">
</CFIF>
<CFIF Form.Department IS NOT "">
  AND Department = <CFQUERYPARAM VALUE="#Form.Department#" CFSQLTYPE="CF_SQL_VARCHAR">
</CFIF>
ORDER BY LastName
</CFQUERY>

<CFOUTPUT><P><B>#Found.RecordCount#</B> match(es).</P></CFOUTPUT>
<CFOUTPUT QUERY="Found">
  #LastName#, #FirstName# (#Department#) #Phone#<BR>
</CFOUTPUT>
