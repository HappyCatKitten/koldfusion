<!--- There is probably no POP3 server on this machine; CFTRY keeps the page polite --->
<CFTRY>
  <CFPOP SERVER="127.0.0.1" USERNAME="someone" PASSWORD="secret"
         ACTION="GetHeaderOnly" NAME="Inbox" MAXROWS="10" TIMEOUT="10">
  <CFOUTPUT><P>#Inbox.RecordCount# message(s) waiting.</P></CFOUTPUT>
  <TABLE BORDER=1 CELLPADDING=3>
  <TR><TH>##</TH><TH>From</TH><TH>Subject</TH><TH>Date</TH></TR>
  <CFOUTPUT QUERY="Inbox">
  <TR><TD>#MessageNumber#</TD><TD>#HTMLEditFormat(From)#</TD>
      <TD>#HTMLEditFormat(Subject)#</TD><TD>#Date#</TD></TR>
  </CFOUTPUT>
  </TABLE>
  <CFCATCH TYPE="Application">
    <CFOUTPUT>
    <P><B>No mail today.</B> #CFCATCH.Message#:<BR>
    <I>#CFCATCH.Detail#</I></P>
    </CFOUTPUT>
  </CFCATCH>
</CFTRY>
