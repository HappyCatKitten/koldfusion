<CFQUERY NAME="GetStaff" DATASOURCE="cfsnippets">
SELECT Department, Emp_ID, LastName, FirstName
FROM Employees ORDER BY Department, LastName
</CFQUERY>

<CFIF StructKeyExists(Form, "StaffTree.node")>
  <CFSET Picked = StructFind(Form, "StaffTree.node")>
  <CFOUTPUT><P>You selected the item <B>#Picked#</B>
  <CFLOOP QUERY="GetStaff">
    <CFIF Emp_ID EQ ListLast(Picked, "/")>: #FirstName# #LastName#, #Department#</CFIF>
  </CFLOOP>
  </CFOUTPUT>
</CFIF>

<CFFORM NAME="Directory" ACTION="cftree.cfm">
<P>Open a department, click a name, then press Show.
<CFTREE NAME="StaffTree" WIDTH="300" REQUIRED="Yes"
    MESSAGE="Click a name in the tree first.">
  <CFTREEITEM VALUE="Department,Emp_ID" DISPLAY="Department,LastName"
      QUERY="GetStaff">
</CFTREE>
<INPUT TYPE="Submit" VALUE="Show">
</CFFORM>
