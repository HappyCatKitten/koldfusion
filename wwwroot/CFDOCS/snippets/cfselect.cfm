<CFPARAM NAME="Form.Dept" DEFAULT="3">
<CFPARAM NAME="Form.Perks" DEFAULT="">

<CFQUERY NAME="GetDepts" DATASOURCE="cfsnippets">
SELECT Dept_ID, Dept_Name FROM Departments ORDER BY Dept_Name
</CFQUERY>

<CFIF IsDefined("Form.FieldNames")>
  <CFOUTPUT><P>You picked department #Form.Dept# and the perks: #Form.Perks#</CFOUTPUT>
</CFIF>

<CFFORM NAME="Transfer" ACTION="cfselect.cfm">
<P>Department:
<CFSELECT NAME="Dept" QUERY="GetDepts" VALUE="Dept_ID"
    DISPLAY="Dept_Name" SELECTED="#Form.Dept#">
</CFSELECT>
<P>Perks (pick at least one):<BR>
<CFSELECT NAME="Perks" SIZE="4" MULTIPLE="Yes" REQUIRED="Yes"
    MESSAGE="Choose at least one perk.">
  <OPTION>Free coffee
  <OPTION>Parking space
  <OPTION>Y2K bonus
  <OPTION>Window office
</CFSELECT>
<P><INPUT TYPE="Submit" VALUE="Submit">
</CFFORM>
