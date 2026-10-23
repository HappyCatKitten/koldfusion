<!--- Validate some orders; bad ones are thrown and caught by family --->
<CFSET Orders = "Modem:3,Mouse pad:-2,Zip drive:0,Keyboard:abc,Monitor:1">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Product</TH><TH>Qty</TH><TH>Result</TH></TR>
<CFLOOP INDEX="Order" LIST="#Orders#">
  <CFSET Product = ListFirst(Order, ":")>
  <CFSET Qty = ListLast(Order, ":")>
  <CFOUTPUT><TR><TD>#Product#</TD><TD>#Qty#</TD></CFOUTPUT>
  <CFTRY>
    <CFIF NOT IsNumeric(Qty)>
      <CFTHROW TYPE="Snippets.Order.NotANumber" MESSAGE="Quantity is not a number"
               ERRORCODE="ORD-1" DETAIL="Use digits, please.">
    <CFELSEIF Qty LT 1>
      <CFTHROW TYPE="Snippets.Order.TooFew" MESSAGE="Quantity must be at least 1"
               ERRORCODE="ORD-2" EXTENDEDINFO="Qty=#Qty#">
    </CFIF>
    <TD BGCOLOR="#CCFFCC">Accepted</TD>
  <CFCATCH TYPE="Snippets.Order">
    <CFOUTPUT><TD BGCOLOR="##FFE0E0">#CFCATCH.ErrorCode#: #CFCATCH.Message#
    <FONT SIZE="1">(#CFCATCH.Type#)</FONT></TD></CFOUTPUT>
  </CFCATCH>
  </CFTRY>
  </TR>
</CFLOOP>
</TABLE>
