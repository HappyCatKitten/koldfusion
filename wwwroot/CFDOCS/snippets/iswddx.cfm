<CFSET Order = StructNew()>
<CFSET Order.Item = "56K modem">
<CFSET Order.Qty = 2>
<CFWDDX ACTION="CFML2WDDX" INPUT="#Order#" OUTPUT="Packet">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Value</TH><TH>IsWDDX</TH></TR>
<CFOUTPUT>
<TR><TD><TT>#HTMLEditFormat(Packet)#</TT></TD><TD>#IsWDDX(Packet)#</TD></TR>
<TR><TD><TT>Hello, world</TT></TD><TD>#IsWDDX("Hello, world")#</TD></TR>
</CFOUTPUT>
</TABLE>
<CFIF IsWDDX(Packet)>
  <CFWDDX ACTION="WDDX2CFML" INPUT="#Packet#" OUTPUT="Back">
  <CFOUTPUT><P>Unpacked: #Back.Qty# x #Back.Item#</CFOUTPUT>
</CFIF>
