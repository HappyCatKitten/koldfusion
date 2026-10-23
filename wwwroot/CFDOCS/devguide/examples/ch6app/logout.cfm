<!--- ch6app/logout.cfm: forget the nickname and go back to the sign-in page --->
<CFLOCK SCOPE="Session" TYPE="Exclusive" TIMEOUT="10">
  <CFSET StructDelete(Session, "UserName")>
  <CFSET StructDelete(Session, "Views")>
</CFLOCK>
<CFLOCATION URL="login.cfm" ADDTOKEN="No">
