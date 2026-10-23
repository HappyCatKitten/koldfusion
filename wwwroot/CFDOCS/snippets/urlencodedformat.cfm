<CFPARAM NAME="URL.Search" DEFAULT="Tom & Jerry's 100% fun">
<CFOUTPUT>
<P>Received: #URL.Search#</P>
<P>Encoded: <TT>#URLEncodedFormat(URL.Search)#</TT></P>
<P><A HREF="urlencodedformat.cfm?Search=#URLEncodedFormat("Fish & Chips ##1")#">Try another value</A></P>
</CFOUTPUT>
