<!--- Find the first employee, by seniority, who earns more than $70,000 --->
<CFQUERY NAME="Staff" DATASOURCE="cfsnippets">
SELECT FirstName, LastName, StartDate, Salary FROM Employees ORDER BY StartDate
</CFQUERY>

<CFSET Found = "">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Row</TH><TH>Employee</TH><TH>Salary</TH></TR>
<CFLOOP QUERY="Staff">
  <CFOUTPUT><TR><TD>#CurrentRow#</TD><TD>#FirstName# #LastName#</TD><TD>#DollarFormat(Salary)#</TD></TR></CFOUTPUT>
  <CFIF Salary GT 70000>
    <CFSET Found = FirstName & " " & LastName>
    <CFSET StoppedAt = CurrentRow>
    <CFBREAK>
  </CFIF>
</CFLOOP>
</TABLE>
<CFOUTPUT>
<P>Stopped after #StoppedAt# of #Staff.RecordCount# rows: the answer is <B>#Found#</B>.</P>
</CFOUTPUT>
