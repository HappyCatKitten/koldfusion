<!--- ch6app/Application.cfm: runs before every page in ch6app/ --->
<CFAPPLICATION NAME="DevGuideSignIn" SESSIONMANAGEMENT="Yes"
    SESSIONTIMEOUT="#CreateTimeSpan(0, 0, 20, 0)#">
<CFSET Request.DSN = "cfsnippets">
<CFSET Request.PageTitle = "Staff Directory">

<!--- Copy the user's nickname out of the session (if any) --->
<CFSET Request.UserName = "">
<CFLOCK SCOPE="Session" TYPE="ReadOnly" TIMEOUT="10">
  <CFIF IsDefined("Session.UserName")>
    <CFSET Request.UserName = Session.UserName>
  </CFIF>
</CFLOCK>

<!--- Everybody must sign in first, except on the sign-in page itself --->
<CFIF Request.UserName IS "" AND ListLast(CGI.SCRIPT_NAME, "/") IS NOT "login.cfm">
  <CFLOCATION URL="login.cfm" ADDTOKEN="No">
</CFIF>
