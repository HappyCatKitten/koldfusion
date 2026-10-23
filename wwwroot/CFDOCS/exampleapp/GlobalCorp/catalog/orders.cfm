<!---
	catalog/orders.cfm - the logged-in user's order history (CFOUTPUT GROUP by order)
--->
<CFSET Section = "catalog">
<CFSET PageTitle = "Your Orders">

<CFQUERY NAME="GetOrders" DATASOURCE="#Request.DSN#">
	SELECT o.Order_ID, o.OrderDate, o.OrderTotal, o.ShipName, o.MailStop,
	       i.Quantity, i.UnitPrice, p.ProductName, p.Product_ID
	FROM Orders o, OrderItems i, Products p
	WHERE o.Order_ID = i.Order_ID
	  AND i.Product_ID = p.Product_ID
	  AND o.UserName = '#Request.UserName#'
	ORDER BY o.Order_ID DESC, p.ProductName
</CFQUERY>

<CFINCLUDE TEMPLATE="../header.cfm">

<CFIF GetOrders.RecordCount EQ 0>
	<P>You have not placed any orders yet. <A HREF="index.cfm">Start shopping</A>.</P>
<CFELSE>
	<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0 WIDTH="100%">
	<CFOUTPUT QUERY="GetOrders" GROUP="Order_ID">
	<TR BGCOLOR="##003366"><TD COLSPAN=3><FONT FACE="#Request.Font#" SIZE=2 COLOR="##FFFFFF"><B>Order #Order_ID#</B>
		&nbsp; #DateFormat(OrderDate, "mmm d, yyyy")# #TimeFormat(OrderDate, "h:mm tt")# &nbsp; to #HTMLEditFormat(ShipName)# (#MailStop#)</FONT></TD></TR>
	<CFOUTPUT>
	<TR><TD><FONT FACE="#Request.Font#" SIZE=2>&nbsp;&nbsp;<A HREF="product.cfm?Product_ID=#Product_ID#">#ProductName#</A></FONT></TD>
		<TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2>#Quantity# @ #DollarFormat(UnitPrice)#</FONT></TD>
		<TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2>#DollarFormat(Quantity * UnitPrice)#</FONT></TD></TR>
	</CFOUTPUT>
	<TR><TD COLSPAN=2 ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>Total</B></FONT></TD>
		<TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>#DollarFormat(OrderTotal)#</B></FONT></TD></TR>
	</CFOUTPUT>
	</TABLE>
</CFIF>

<CFINCLUDE TEMPLATE="../footer.cfm">
