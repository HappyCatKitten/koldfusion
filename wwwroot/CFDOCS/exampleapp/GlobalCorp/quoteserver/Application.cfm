<!---
	quoteserver/Application.cfm
	The quote server is called by machines (CFHTTP), not people, so it
	gets its own Application.cfm: no login screen and no session.
	ColdFusion runs only the Application.cfm closest to the requested page.
--->
<CFAPPLICATION NAME="GlobalCorpQuoteServer" SESSIONMANAGEMENT="No">
<CFSET Request.DSN = "cfexamples">
