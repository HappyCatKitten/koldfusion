<CFSET Tests = "12/31/1999|January 1, 2000|2000-02-29|February 30, 2000|2000|next Tuesday">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>string</TH><TH>IsDate</TH></TR>
<CFLOOP INDEX="s" LIST="#Tests#" DELIMITERS="|">
<CFOUTPUT><TR><TD>#s#</TD><TD>#IsDate(s)#</TD></TR></CFOUTPUT>
</CFLOOP>
<CFOUTPUT><TR><TD>Now()</TD><TD>#IsDate(Now())#</TD></TR></CFOUTPUT>
</TABLE>
