<CFQUERY NAME="Staff" DATASOURCE="cfsnippets" MAXROWS="6">
SELECT FirstName, LastName, Contract FROM Employees ORDER BY LastName
</CFQUERY>
<TABLE CELLPADDING=3 CELLSPACING=0 BORDER=0>
<TR BGCOLOR="#000066"><TH><FONT COLOR="white">Name</FONT></TH><TH><FONT COLOR="white">Status</FONT></TH></TR>
<CFOUTPUT QUERY="Staff">
<TR BGCOLOR="###IIf(CurrentRow MOD 2, DE("FFFFFF"), DE("FFFFCC"))#">
  <TD>#FirstName# #LastName#</TD>
  <TD>#IIf(Contract, DE("Contractor"), DE("Employee"))#</TD>
</TR>
</CFOUTPUT>
</TABLE>
