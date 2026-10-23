<CFSET Cutoff = CreateDate(1998, 1, 1)>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Input</TH><TH>CreateODBCDate</TH></TR>
<TR><TD>CreateDate(1998, 1, 1)</TD><TD>#CreateODBCDate(Cutoff)#</TD></TR>
<TR><TD>"10/22/1999 9:42 PM"</TD><TD>#CreateODBCDate("10/22/1999 9:42 PM")#</TD></TR>
<TR><TD>Now()</TD><TD>#CreateODBCDate(Now())#</TD></TR>
</TABLE>
<P>In a query you would write:</P>
<PRE>
SELECT FirstName, LastName FROM Employees
WHERE StartDate &gt;= #CreateODBCDate(Cutoff)#
</PRE>
</CFOUTPUT>
