<CFSET Checks = "Application|Payroll|,File|/reports/salaries.txt|Read,DataSource|cfsnippets|Delete">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Type</TH><TH>Resource</TH><TH>Action</TH><TH>IsAuthorized</TH></TR>
<CFLOOP LIST="#Checks#" INDEX="c">
  <CFSET Type = ListGetAt(c, 1, "|")>
  <CFSET Res = ListGetAt(c, 2, "|")>
  <CFSET Act = "">
  <CFIF ListLen(c, "|") GT 2><CFSET Act = ListGetAt(c, 3, "|")></CFIF>
  <CFOUTPUT><TR><TD>#Type#</TD><TD>#Res#</TD><TD>#Act#&nbsp;</TD>
  <TD>#IsAuthorized(Type, Res, Act)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<CFIF NOT IsAuthenticated()>
  <P><I>Nobody is logged in, so every answer is NO.</I></P>
</CFIF>
