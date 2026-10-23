<CFSET Cart = StructNew()>
<CFSET Cart.Modem = 1>
<CFSET Cart.Mousepad = 2>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Call</TH><TH>Returns</TH></TR>
<TR><TD>StructDelete(Cart, "Mousepad")</TD><TD>#StructDelete(Cart, "Mousepad")#</TD></TR>
<TR><TD>StructDelete(Cart, "Mousepad", TRUE)</TD><TD>#StructDelete(Cart, "Mousepad", TRUE)#</TD></TR>
<TR><TD>StructDelete(Cart, "Mousepad")</TD><TD>#StructDelete(Cart, "Mousepad")#</TD></TR>
</TABLE>
<P>Keys left: #StructKeyList(Cart)#</P>
</CFOUTPUT>
