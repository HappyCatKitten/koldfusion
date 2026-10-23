<!--- ch6app/login.cfm --->
<CFIF IsDefined("Form.UserName") AND Trim(Form.UserName) IS NOT "">
  <CFLOCK SCOPE="Session" TYPE="Exclusive" TIMEOUT="10">
    <CFSET Session.UserName = HTMLEditFormat(Left(Trim(Form.UserName), 20))>
  </CFLOCK>
  <CFLOCATION URL="index.cfm" ADDTOKEN="No">
</CFIF>

<CFSET Request.PageTitle = "Please sign in">
<CFINCLUDE TEMPLATE="../ch6_header.cfm">
<FORM ACTION="login.cfm" METHOD="POST">
Pick a nickname: <INPUT TYPE="text" NAME="UserName" SIZE="20" MAXLENGTH="20">
<INPUT TYPE="submit" VALUE="Sign in">
</FORM>
<CFINCLUDE TEMPLATE="../ch6_footer.cfm">
