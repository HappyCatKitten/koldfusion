<CFPARAM NAME="Form.UserName" DEFAULT="guest">
<CFPARAM NAME="Form.Password" DEFAULT="guest">

<CFOUTPUT>
<FORM ACTION="cfauthenticate.cfm" METHOD="POST">
User: <INPUT TYPE="Text" NAME="UserName" VALUE="#HTMLEditFormat(Form.UserName)#" SIZE="12">
Password: <INPUT TYPE="Password" NAME="Password" SIZE="12">
<INPUT TYPE="Submit" VALUE="Log in">
</FORM>
</CFOUTPUT>

<!--- The "Snippets" context exists only if an administrator created it --->
<CFTRY>
  <CFAUTHENTICATE SECURITYCONTEXT="Snippets" USERNAME="#Form.UserName#"
      PASSWORD="#Form.Password#" SETCOOKIE="No">
  <CFOUTPUT><P>Welcome, <B>#AuthenticatedUser()#</B>!
  You are logged in to the context #AuthenticatedContext()#.</CFOUTPUT>
<CFCATCH TYPE="Security">
  <CFOUTPUT><P><B>Not logged in:</B> #CFCATCH.Message#<BR>
  <I>#CFCATCH.Detail#</I></CFOUTPUT>
</CFCATCH>
</CFTRY>

<CFOUTPUT><P>IsAuthenticated() returns #IsAuthenticated()#.</CFOUTPUT>
