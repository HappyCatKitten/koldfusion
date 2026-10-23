<CFQUERY NAME="GetStaff" DATASOURCE="cfsnippets" MAXROWS="6">
SELECT FirstName, LastName, Contract FROM Employees ORDER BY LastName
</CFQUERY>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Employee</TH><TH>Contract (raw)</TH><TH>Contractor?</TH></TR>
<CFOUTPUT QUERY="GetStaff">
<TR><TD>#FirstName# #LastName#</TD><TD>#Contract#</TD><TD>#YesNoFormat(Contract)#</TD></TR>
</CFOUTPUT>
</TABLE>
<CFOUTPUT><P>Is 2000 a leap year? #YesNoFormat(IsLeapYear(2000))#</P></CFOUTPUT>
