<CFSET Tests = "1234.5| 42 |-0.001|1,999,999">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>String</TH><TH>Number</TH><TH>Times two</TH></TR>
<CFLOOP INDEX="S" LIST="#Tests#" DELIMITERS="|">
<CFSET N = LSParseNumber(Replace(S, ",", "", "ALL"))>
<CFOUTPUT>
<TR><TD>[#S#]</TD><TD>#N#</TD><TD>#N * 2#</TD></TR>
</CFOUTPUT>
</CFLOOP>
</TABLE>
