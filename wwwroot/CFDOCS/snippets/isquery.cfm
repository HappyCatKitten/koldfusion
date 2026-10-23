<CFQUERY NAME="GetDepts" DATASOURCE="cfsnippets">
SELECT Dept_Name FROM Departments
</CFQUERY>
<CFSET Made = QueryNew("Name, Price")>
<CFSET List = ValueList(GetDepts.Dept_Name)>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Variable</TH><TH>IsQuery</TH></TR>
<CFOUTPUT>
<TR><TD>GetDepts (CFQUERY)</TD><TD>#IsQuery(GetDepts)#</TD></TR>
<TR><TD>Made (QueryNew)</TD><TD>#IsQuery(Made)#</TD></TR>
<TR><TD>List: #List#</TD><TD>#IsQuery(List)#</TD></TR>
</CFOUTPUT>
</TABLE>
