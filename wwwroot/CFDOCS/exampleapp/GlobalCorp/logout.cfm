<!--- logout.cfm - forget who the user is, then send them to the home page (and the login form) --->
<CFLOCK SCOPE="Session" TYPE="Exclusive" TIMEOUT="10">
	<CFSET StructDelete(Session, "UserName")>
	<CFSET StructDelete(Session, "FullName")>
	<CFSET StructDelete(Session, "Emp_ID")>
	<CFSET StructDelete(Session, "IsAdmin")>
	<CFSET StructDelete(Session, "Cart")>
</CFLOCK>
<CFLOCATION URL="index.cfm?loggedout=yes" ADDTOKEN="No">
