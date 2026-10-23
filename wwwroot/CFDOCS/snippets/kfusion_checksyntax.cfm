<CFSET Samples = ArrayNew(1)>
<CFSET Samples[1] = '<CFIF Speed GT 28800>Fast!</CFIF>'>
<CFSET Samples[2] = '<CFIF Speed GT 28800>Fast!'>
<CFSET Samples[3] = '<CFSET Total = (Price * 2>'>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Code</TH><TH>OK</TH><TH>Line:Col</TH><TH>Message</TH></TR>
<CFLOOP INDEX="i" FROM="1" TO="#ArrayLen(Samples)#">
  <CFSET Check = KFUSION_CHECKSYNTAX(Samples[i], "sample#i#.cfm")>
  <CFOUTPUT><TR VALIGN="top"><TD><TT>#HTMLEditFormat(Samples[i])#</TT></TD><TD>#Check.OK#</TD>
  <TD>#Check.Line#:#Check.Column#</TD><TD>#Check.Message#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
