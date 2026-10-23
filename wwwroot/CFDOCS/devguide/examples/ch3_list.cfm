<!--- ch3_list.cfm: list the employees of one department --->
<CFQUERY NAME="GetStaff" DATASOURCE="cfsnippets">
SELECT FirstName, LastName, Phone, StartDate
FROM Employees
WHERE Department = 'Engineering'
ORDER BY LastName
</CFQUERY>

<H3>Engineering Department</H3>
<CFOUTPUT><P>#GetStaff.RecordCount# people found.</P></CFOUTPUT>

<TABLE BORDER="0" CELLPADDING="3" CELLSPACING="0">
<TR BGCOLOR="#003399">
  <TH><FONT COLOR="#FFFFFF">#</FONT></TH>
  <TH><FONT COLOR="#FFFFFF">Name</FONT></TH>
  <TH><FONT COLOR="#FFFFFF">Phone</FONT></TH>
  <TH><FONT COLOR="#FFFFFF">Started</FONT></TH>
</TR>
<CFOUTPUT QUERY="GetStaff">
<TR BGCOLOR="###IIf(CurrentRow MOD 2, DE('FFFFFF'), DE('EEEEEE'))#">
  <TD>#CurrentRow#</TD>
  <TD>#LastName#, #FirstName#</TD>
  <TD>#Phone#</TD>
  <TD>#DateFormat(StartDate, "mmm d, yyyy")#</TD>
</TR>
</CFOUTPUT>
</TABLE>
