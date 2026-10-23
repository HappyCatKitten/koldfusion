<CFSET Launch = CreateDate(1999, 10, 22)>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Expression</TH><TH>Result</TH></TR>
<TR><TD>CreateDate(1999, 10, 22)</TD><TD>#Launch#</TD></TR>
<TR><TD>DateFormat(...)</TD><TD>#DateFormat(Launch, "dddd, mmmm d, yyyy")#</TD></TR>
<TR><TD>Year / Month / Day</TD><TD>#Year(Launch)# / #Month(Launch)# / #Day(Launch)#</TD></TR>
</TABLE>
</CFOUTPUT>

<!--- Invalid dates throw an error --->
<CFTRY>
  <CFSET Bad = CreateDate(1999, 2, 29)>
<CFCATCH TYPE="Expression">
  <CFOUTPUT><P>CreateDate(1999, 2, 29): <B>#CFCATCH.Message#</B> 1999 was not a leap year.</P></CFOUTPUT>
</CFCATCH>
</CFTRY>
