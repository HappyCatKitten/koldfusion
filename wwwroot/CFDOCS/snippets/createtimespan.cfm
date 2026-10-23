<CFSET Span = CreateTimeSpan(0, 6, 0, 0)>
<CFSET Start = CreateDateTime(1999, 12, 31, 20, 0, 0)>
<CFSET Finish = Start + Span>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>CreateTimeSpan(0, 6, 0, 0)</TD><TD>#Span# days</TD></TR>
<TR><TD>CreateTimeSpan(1, 12, 0, 0)</TD><TD>#CreateTimeSpan(1, 12, 0, 0)# days</TD></TR>
<TR><TD>Party starts</TD><TD>#DateFormat(Start, "mmm d, yyyy")# #TimeFormat(Start, "h:mm tt")#</TD></TR>
<TR><TD>Plus six hours</TD><TD>#DateFormat(Finish, "mmm d, yyyy")# #TimeFormat(Finish, "h:mm tt")#</TD></TR>
</TABLE>
</CFOUTPUT>
<!--- Cache this query for 15 minutes --->
<CFQUERY NAME="Depts" DATASOURCE="cfsnippets" CACHEDWITHIN="#CreateTimeSpan(0, 0, 15, 0)#">
SELECT Dept_Name FROM Departments
</CFQUERY>
<CFOUTPUT><P>#Depts.RecordCount# departments, cached for 15 minutes.</P></CFOUTPUT>
