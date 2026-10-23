<CFQUERY NAME="Hires" DATASOURCE="cfsnippets">
SELECT FirstName, LastName, StartDate FROM Employees ORDER BY StartDate
</CFQUERY>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Employee</TH><TH>Started</TH><TH>Quarter</TH></TR>
<CFOUTPUT QUERY="Hires" MAXROWS="8">
<TR><TD>#FirstName# #LastName#</TD><TD>#DateFormat(StartDate, "mmm d, yyyy")#</TD>
    <TD>Q#Quarter(StartDate)# #Year(StartDate)#</TD></TR>
</CFOUTPUT>
</TABLE>
