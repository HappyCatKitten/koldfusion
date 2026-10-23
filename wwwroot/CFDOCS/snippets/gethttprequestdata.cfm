<CFSET Request_Data = GetHttpRequestData()>
<CFOUTPUT>
<P>This page was requested with <B>#Request_Data.Method#</B> over #Request_Data.Protocol#.
The request body is #Len(Request_Data.Content)# bytes long.</P>
</CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR BGCOLOR="#CCCCCC"><TH>Header</TH><TH>Value</TH></TR>
<CFLOOP COLLECTION="#Request_Data.Headers#" ITEM="h">
<CFOUTPUT><TR><TD>#h#</TD><TD>#HTMLEditFormat(Request_Data.Headers[h])#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
