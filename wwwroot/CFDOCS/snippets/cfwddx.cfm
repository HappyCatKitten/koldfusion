<CFSET Order = StructNew()>
<CFSET Order.Customer = "Pat Kowal">
<CFSET Order.Placed = CreateDateTime(1999, 12, 31, 23, 59, 0)>
<CFSET Order.Items = ListToArray("Modem,Mouse pad,Y2K patch disk")>

<CFWDDX ACTION="CFML2WDDX" INPUT="#Order#" OUTPUT="Packet">
<CFWDDX ACTION="WDDX2CFML" INPUT="#Packet#" OUTPUT="Copy">
<CFWDDX ACTION="CFML2JS" INPUT="#Order#" TOPLEVELVARIABLE="order" OUTPUT="Script">

<CFOUTPUT>
<P><B>The WDDX packet</B> (#Len(Packet)# characters, IsWDDX: #IsWDDX(Packet)#):</P>
<PRE>#HTMLEditFormat(Replace(Packet, "><", ">#Chr(10)#<", "ALL"))#</PRE>
<P><B>Back in CFML:</B></P>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>Customer</TD><TD>#Copy.Customer#</TD></TR>
<TR><TD>Placed</TD><TD>#DateFormat(Copy.Placed, "mmmm d, yyyy")# #TimeFormat(Copy.Placed, "h:mm tt")#</TD></TR>
<TR><TD>Items</TD><TD>#ArrayToList(Copy.Items, ", ")#</TD></TR>
</TABLE>
<P><B>As JavaScript:</B></P>
<PRE>#HTMLEditFormat(Script)#</PRE>
</CFOUTPUT>
