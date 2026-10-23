<CFQUERY NAME="Depts" DATASOURCE="cfsnippets">
SELECT Department, Count(*) AS Heads FROM Employees GROUP BY Department
</CFQUERY>
<!--- create one variable per department: Heads_Sales, Heads_Marketing ... --->
<CFLOOP QUERY="Depts">
  <CFSET Dummy = SetVariable("Heads_" & Department, Heads)>
</CFLOOP>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Variable</TH><TH>Value</TH></TR>
<CFLOOP QUERY="Depts">
<TR><TD>Heads_#Department#</TD><TD>#Evaluate("Heads_" & Department)#</TD></TR>
</CFLOOP>
</TABLE>
</CFOUTPUT>
