<!---
	SearchAction.cfm - builds the WHERE clause from whichever fields were filled in.
	"WHERE 1 = 1" lets every condition start with AND.
--->
<CFPARAM NAME="Form.LastName" DEFAULT="">
<CFPARAM NAME="Form.Department_ID" DEFAULT="">
<CFPARAM NAME="Form.MinSalary" DEFAULT="">
<CFPARAM NAME="Form.MaxSalary" DEFAULT="">
<CFPARAM NAME="Form.StartedAfter" DEFAULT="">
<CFPARAM NAME="Form.Contract" DEFAULT="">
<CFSET PageTitle = "Search Results">

<CFQUERY NAME="SearchResults" DATASOURCE="#Request.DSN#">
	SELECT e.Employee_ID, e.FirstName, e.LastName, e.StartDate, e.Salary, e.Contract, d.Department_Name
	FROM Employees e, Departments d
	WHERE e.Department_ID = d.Department_ID
	<CFIF Len(Trim(Form.LastName))>
		AND e.LastName LIKE '#Trim(Form.LastName)#%'
	</CFIF>
	<CFIF Len(Form.Department_ID)>
		AND e.Department_ID = #Val(Form.Department_ID)#
	</CFIF>
	<CFIF Len(Trim(Form.MinSalary))>
		AND e.Salary >= #Val(Form.MinSalary)#
	</CFIF>
	<CFIF Len(Trim(Form.MaxSalary))>
		AND e.Salary <= #Val(Form.MaxSalary)#
	</CFIF>
	<CFIF IsDate(Form.StartedAfter)>
		AND e.StartDate > <CFQUERYPARAM CFSQLTYPE="CF_SQL_DATE" VALUE="#Form.StartedAfter#">
	</CFIF>
	<CFIF Form.Contract IS "Yes">
		AND e.Contract = 1
	<CFELSEIF Form.Contract IS "No">
		AND e.Contract = 0
	</CFIF>
	ORDER BY e.LastName, e.FirstName
</CFQUERY>

<CFINCLUDE TEMPLATE="toolbar.cfm">

<CFOUTPUT><P><FONT FACE="#Request.Font#" SIZE=2><B>#SearchResults.RecordCount#</B> employee<CFIF SearchResults.RecordCount NEQ 1>s</CFIF> found.
<A HREF="SearchForm.cfm">New search</A></FONT></P></CFOUTPUT>

<CFIF SearchResults.RecordCount>
<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="#CCCCCC">
	<TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Name</B></FONT></TD>
	<TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Department</B></FONT></TD>
	<TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Start Date</B></FONT></TD>
	<TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2><B>Salary</B></FONT></TD>
	<TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Contract</B></FONT></TD>
</TR>
<CFOUTPUT QUERY="SearchResults">
<TR BGCOLOR="###IIf(CurrentRow MOD 2, DE('FFFFFF'), DE('EEEEEE'))#">
	<TD><FONT FACE="#Request.Font#" SIZE=2><A HREF="UpdateForm.cfm?Employee_ID=#Employee_ID#">#LastName#, #FirstName#</A></FONT></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2>#Department_Name#</FONT></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2>#DateFormat(StartDate, "mm/dd/yyyy")#</FONT></TD>
	<TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2>#DollarFormat(Salary)#</FONT></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2>#YesNoFormat(Contract)#</FONT></TD>
</TR>
</CFOUTPUT>
</TABLE>
</CFIF>

<CFINCLUDE TEMPLATE="footer.cfm">
