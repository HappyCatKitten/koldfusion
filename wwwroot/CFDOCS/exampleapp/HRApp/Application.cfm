<!---
	HRApp/Application.cfm - Human Resources Employee Manager
	No login here: this example is about CFINSERT, CFUPDATE and form validation.
--->
<CFAPPLICATION NAME="HREmployeeManager" SESSIONMANAGEMENT="No">
<CFSET Request.DSN = "CompanyInfo">
<CFSET Request.Font = "Arial, Helvetica">
