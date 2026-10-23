<!---
	GlobalCorp Intranet - Application.cfm
	Runs before every page in this directory and its subdirectories.
	  * names the application and turns on session variables
	  * sets up application-wide constants and the hit counter once
	  * handles the login form and keeps strangers out
	  * copies the session user into the Request scope so pages need not lock
--->
<CFAPPLICATION NAME="GlobalCorpIntranet"
	SESSIONMANAGEMENT="Yes"
	SESSIONTIMEOUT="#CreateTimeSpan(0, 0, 30, 0)#"
	APPLICATIONTIMEOUT="#CreateTimeSpan(2, 0, 0, 0)#">

<!--- Per-request constants --->
<CFSET Request.DSN = "cfexamples">
<CFSET Request.Root = "/CFDOCS/exampleapp/GlobalCorp">
<CFSET Request.Images = "/CFDOCS/exampleapp/images">
<CFSET Request.Font = "Arial, Helvetica">

<!--- Application-wide settings, initialized once --->
<CFLOCK SCOPE="Application" TYPE="Exclusive" TIMEOUT="10">
	<CFIF NOT IsDefined("Application.Initialized")>
		<CFSET Application.CompanyName = "GlobalCorp Industries">
		<CFSET Application.HelpDesk = "x4004">
		<CFSET Application.OrdersFrom = "companystore@globalcorp.example">
		<CFSET Application.StartedAt = Now()>
		<!--- The hit counter lives only in memory: it starts over when the server restarts --->
		<CFSET Application.HitCount = 0>
		<CFSET Application.CatalogIndexed = FALSE>
		<CFSET Application.Initialized = TRUE>
	</CFIF>
	<CFSET Request.CompanyName = Application.CompanyName>
	<CFSET Request.HelpDesk = Application.HelpDesk>
	<CFSET Request.OrdersFrom = Application.OrdersFrom>
</CFLOCK>

<!--- Process a login attempt from loginform.cfm --->
<CFSET Request.LoginError = "">
<CFIF IsDefined("Form.Login_UserName") AND IsDefined("Form.Login_Password")>
	<CFQUERY NAME="CheckLogin" DATASOURCE="#Request.DSN#">
		SELECT UserName, FullName, Emp_ID, IsAdmin
		FROM Users
		WHERE UserName = '#Trim(Form.Login_UserName)#'
		  AND Password = '#Form.Login_Password#'
	</CFQUERY>
	<CFIF CheckLogin.RecordCount EQ 1>
		<CFLOCK SCOPE="Session" TYPE="Exclusive" TIMEOUT="10">
			<CFSET Session.UserName = CheckLogin.UserName>
			<CFSET Session.FullName = CheckLogin.FullName>
			<CFSET Session.Emp_ID = Val(CheckLogin.Emp_ID)>
			<CFSET Session.IsAdmin = CheckLogin.IsAdmin>
			<CFSET Session.LoginTime = Now()>
			<CFIF NOT IsDefined("Session.Cart")>
				<CFSET Session.Cart = StructNew()>
			</CFIF>
		</CFLOCK>
	<CFELSE>
		<CFSET Request.LoginError = "That user name and password combination was not found. Please try again.">
	</CFIF>
</CFIF>

<!--- Copy the session user to the Request scope (read-only lock) --->
<CFLOCK SCOPE="Session" TYPE="ReadOnly" TIMEOUT="10">
	<CFIF IsDefined("Session.UserName")>
		<CFSET Request.UserName = Session.UserName>
		<CFSET Request.FullName = Session.FullName>
		<CFSET Request.Emp_ID = Session.Emp_ID>
		<CFSET Request.IsAdmin = Session.IsAdmin>
	<CFELSE>
		<CFSET Request.UserName = "">
	</CFIF>
</CFLOCK>

<!--- Not logged in? Show the login form instead of the requested page --->
<CFIF Request.UserName IS "">
	<CFINCLUDE TEMPLATE="loginform.cfm">
	<CFABORT>
</CFIF>
