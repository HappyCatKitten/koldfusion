<CFIF IsDefined("Form.FieldNames")>
  <H3>You sent:</H3>
  <UL>
  <CFLOOP LIST="#Form.FieldNames#" INDEX="Field">
    <CFOUTPUT><LI>#Field# = #HTMLEditFormat(Evaluate("Form." & Field))#</CFOUTPUT>
  </CFLOOP>
  </UL>
</CFIF>

<CFFORM NAME="Signup" ACTION="cfform.cfm">
<TABLE>
<TR><TD>Name:</TD>
  <TD><CFINPUT TYPE="Text" NAME="FullName" SIZE="25" REQUIRED="Yes"
      MESSAGE="Please tell us your name."></TD></TR>
<TR><TD>Year of birth:</TD>
  <TD><CFINPUT TYPE="Text" NAME="BirthYear" SIZE="4" VALIDATE="integer"
      RANGE="1900,1999" MESSAGE="A year between 1900 and 1999, please."></TD></TR>
<TR><TD>Connection:</TD>
  <TD><CFSELECT NAME="Modem">
      <OPTION>28.8K modem<OPTION SELECTED>56K modem<OPTION>ISDN<OPTION>T1 at work
      </CFSELECT></TD></TR>
</TABLE>
<INPUT TYPE="Submit" VALUE="Sign me up">
</CFFORM>
