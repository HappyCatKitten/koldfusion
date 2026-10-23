<!---
	InsertAction.cfm - CFINSERT writes the form fields straight into the table.
	FORMFIELDS lists the fields to save (the hidden validation fields are skipped).
--->
<CFIF NOT IsDefined("Form.LastName")>
	<CFLOCATION URL="InsertForm.cfm" ADDTOKEN="No">
</CFIF>
<CFINSERT DATASOURCE="#Request.DSN#" TABLENAME="Employees"
	FORMFIELDS="FirstName,LastName,Department_ID,StartDate,Salary,Contract">

<CFSET PageTitle = "Employee Added">
<CFINCLUDE TEMPLATE="toolbar.cfm">
<CFOUTPUT>
<P><FONT FACE="#Request.Font#" SIZE=2><B>#HTMLEditFormat(Form.FirstName)# #HTMLEditFormat(Form.LastName)#</B> has been added to the employee database.</FONT></P>
<P><FONT FACE="#Request.Font#" SIZE=2><A HREF="InsertForm.cfm">Add another employee</A> | <A HREF="EmpList.cfm">Employee list</A></FONT></P>
</CFOUTPUT>
<CFINCLUDE TEMPLATE="footer.cfm">
