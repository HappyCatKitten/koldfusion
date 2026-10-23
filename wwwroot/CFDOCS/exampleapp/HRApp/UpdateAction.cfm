<!---
	UpdateAction.cfm - CFUPDATE finds the row by the primary key field
	(Employee_ID) and updates the other columns from the form.
--->
<CFIF NOT IsDefined("Form.Employee_ID")>
	<CFLOCATION URL="UpdateList.cfm" ADDTOKEN="No">
</CFIF>
<CFUPDATE DATASOURCE="#Request.DSN#" TABLENAME="Employees"
	FORMFIELDS="Employee_ID,FirstName,LastName,Department_ID,StartDate,Salary,Contract">

<CFSET PageTitle = "Employee Updated">
<CFINCLUDE TEMPLATE="toolbar.cfm">
<CFOUTPUT>
<P><FONT FACE="#Request.Font#" SIZE=2>The record for <B>#HTMLEditFormat(Form.FirstName)# #HTMLEditFormat(Form.LastName)#</B> has been updated.</FONT></P>
<P><FONT FACE="#Request.Font#" SIZE=2><A HREF="UpdateList.cfm">Update another employee</A> | <A HREF="EmpList.cfm">Employee list</A></FONT></P>
</CFOUTPUT>
<CFINCLUDE TEMPLATE="footer.cfm">
