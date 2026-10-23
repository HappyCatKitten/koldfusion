<!--- ch4_form.cfm: a form that posts to itself --->
<CFPARAM NAME="Form.FullName" DEFAULT="">
<CFPARAM NAME="Form.Modem" DEFAULT="">
<CFPARAM NAME="Form.Browser" DEFAULT="">

<CFIF IsDefined("Form.FieldNames")>
  <!--- The form was posted: show what came in --->
  <CFOUTPUT>
  <P>Thanks, <B>#HTMLEditFormat(Form.FullName)#</B>!</P>
  <P>You surf at #HTMLEditFormat(Form.Modem)#
  <CFIF Form.Browser IS NOT "">with #HTMLEditFormat(Form.Browser)#</CFIF>.
  The fields posted were: #Form.FieldNames#</P>
  </CFOUTPUT>
  <P><A HREF="ch4_form.cfm">Fill it in again</A></P>
<CFELSE>
  <H3>Visitor survey</H3>
  <FORM ACTION="ch4_form.cfm" METHOD="POST">
  <!--- Server-side validation: KoldFusion checks these before the page runs --->
  <INPUT TYPE="hidden" NAME="FullName_required" VALUE="Please tell us your name.">
  <INPUT TYPE="hidden" NAME="Modem_required" VALUE="Please choose a connection speed.">
  <TABLE>
  <TR><TD>Your name:</TD>
      <TD><INPUT TYPE="text" NAME="FullName" SIZE="30" MAXLENGTH="50"></TD></TR>
  <TR><TD>Connection:</TD>
      <TD><INPUT TYPE="radio" NAME="Modem" VALUE="28.8K">28.8K
          <INPUT TYPE="radio" NAME="Modem" VALUE="56K">56K
          <INPUT TYPE="radio" NAME="Modem" VALUE="ISDN">ISDN
          <INPUT TYPE="radio" NAME="Modem" VALUE="a T1 at work">T1</TD></TR>
  <TR><TD>Browser:</TD>
      <TD><SELECT NAME="Browser">
          <OPTION VALUE="">(rather not say)
          <OPTION>Netscape Navigator 4.7
          <OPTION>Internet Explorer 5
          <OPTION>Lynx
          </SELECT></TD></TR>
  </TABLE>
  <INPUT TYPE="submit" VALUE="Send">
  </FORM>
</CFIF>
