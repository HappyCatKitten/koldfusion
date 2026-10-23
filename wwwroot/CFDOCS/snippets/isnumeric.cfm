<CFSET Tests = ListToArray("42|-3.5|.5|1E3| 12 |$12|1,000|Y2K", "|")>
<CFSET ArrayAppend(Tests, "")>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>string</TH><TH>IsNumeric</TH><TH>Val</TH></TR>
<CFLOOP INDEX="i" FROM="1" TO="#ArrayLen(Tests)#">
<CFSET s = Tests[i]>
<CFOUTPUT><TR><TD><TT>"#s#"</TT></TD><TD>#IsNumeric(s)#</TD><TD>#Val(s)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
