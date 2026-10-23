<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>string</TH><TH>radix</TH><TH>InputBaseN</TH></TR>
<CFLOOP INDEX="args" LIST="1010:2,777:8,FF:16,cafe:16,ZZ:36">
<CFSET s = ListFirst(args, ":")><CFSET r = ListLast(args, ":")>
<CFOUTPUT><TR><TD><TT>#s#</TT></TD><TD ALIGN="RIGHT">#r#</TD><TD ALIGN="RIGHT">#InputBaseN(s, r)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<CFTRY>
  <CFSET x = InputBaseN("12G", 16)>
  <CFCATCH TYPE="Expression">
    <CFOUTPUT><P><I>"12G" is not hexadecimal:</I> #CFCATCH.Message#</CFOUTPUT>
  </CFCATCH>
</CFTRY>
