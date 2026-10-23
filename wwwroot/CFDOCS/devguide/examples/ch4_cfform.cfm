<!--- ch4_cfform.cfm: browser-side validation with CFFORM --->
<CFQUERY NAME="GetDepts" DATASOURCE="cfsnippets">
SELECT Dept_Name FROM Departments ORDER BY Dept_Name
</CFQUERY>

<CFIF IsDefined("Form.FieldNames")>
  <CFOUTPUT>
  <P>Request received: #HTMLEditFormat(Form.Qty)# training seat(s) in
  #HTMLEditFormat(Form.Department)#, starting #HTMLEditFormat(Form.StartDate)#.
  Confirmation goes to #HTMLEditFormat(Form.Email)#.</P>
  </CFOUTPUT>
  <P><A HREF="ch4_cfform.cfm">Another request</A></P>
<CFELSE>
  <H3>Training seat request</H3>
  <CFFORM ACTION="ch4_cfform.cfm" METHOD="POST" NAME="SeatForm">
  <TABLE>
  <TR><TD>E-mail:</TD>
      <TD><CFINPUT TYPE="text" NAME="Email" SIZE="30" REQUIRED="Yes"
           MESSAGE="Please enter your e-mail address."></TD></TR>
  <TR><TD>Seats (1-12):</TD>
      <TD><CFINPUT TYPE="text" NAME="Qty" SIZE="3" VALIDATE="integer" RANGE="1,12"
           REQUIRED="Yes" MESSAGE="Seats must be a whole number from 1 to 12."></TD></TR>
  <TR><TD>Start date:</TD>
      <TD><CFINPUT TYPE="text" NAME="StartDate" SIZE="10" VALIDATE="date"
           REQUIRED="Yes" MESSAGE="Please enter the start date as mm/dd/yyyy."></TD></TR>
  <TR><TD>Department:</TD>
      <TD><CFSELECT NAME="Department" QUERY="GetDepts" VALUE="Dept_Name"
           DISPLAY="Dept_Name" SELECTED="Training"></CFSELECT></TD></TR>
  </TABLE>
  <INPUT TYPE="submit" VALUE="Request seats">
  </CFFORM>
</CFIF>
