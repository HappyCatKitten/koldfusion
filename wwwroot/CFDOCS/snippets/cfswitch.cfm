<CFQUERY NAME="Depts" DATASOURCE="cfsnippets">
SELECT Dept_Name, Location FROM Departments ORDER BY Dept_Name
</CFQUERY>

<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Department</TH><TH>Location</TH><TH>Typical lunch</TH></TR>
<CFOUTPUT QUERY="Depts">
<TR><TD>#Dept_Name#</TD><TD>#Location#</TD><TD>
  <CFSWITCH EXPRESSION="#Dept_Name#">
    <CFCASE VALUE="Sales,Marketing">Expense-account steak</CFCASE>
    <CFCASE VALUE="engineering">Cold pizza at the keyboard</CFCASE>
    <CFCASE VALUE="Accounting">A sandwich, itemized</CFCASE>
    <CFDEFAULTCASE><I>Whatever is in the cafeteria</I></CFDEFAULTCASE>
  </CFSWITCH>
</TD></TR>
</CFOUTPUT>
</TABLE>
