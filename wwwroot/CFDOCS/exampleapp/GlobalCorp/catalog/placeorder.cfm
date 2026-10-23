<!---
	catalog/placeorder.cfm - writes the order, e-mails a confirmation, empties the cart.
	The order header and its line items are written inside one CFTRANSACTION.
	CFMAIL hands the message to the mail spooler, so the page doesn't wait for the mail server.
--->
<CFSET Section = "catalog">
<CFSET PageTitle = "Thank You for Your Order">
<CFIF NOT IsDefined("Form.ShipName")>
	<CFLOCATION URL="cart.cfm" ADDTOKEN="No">
</CFIF>
<CFPARAM NAME="Form.Notes" DEFAULT="">

<CFLOCK SCOPE="Session" TYPE="ReadOnly" TIMEOUT="10">
	<CFSET MyCart = Duplicate(Session.Cart)>
</CFLOCK>
<CFIF StructIsEmpty(MyCart)>
	<CFLOCATION URL="cart.cfm" ADDTOKEN="No">
</CFIF>

<CFQUERY NAME="GetItems" DATASOURCE="#Request.DSN#">
	SELECT Product_ID, SKU, ProductName, Price
	FROM Products
	WHERE Product_ID IN (#StructKeyList(MyCart)#)
	ORDER BY ProductName
</CFQUERY>
<!--- add a Quantity column to the query so CFMAIL and CFOUTPUT can use it --->
<CFSET QtyList = "">
<CFSET OrderTotal = 0>
<CFLOOP QUERY="GetItems">
	<CFSET QtyList = ListAppend(QtyList, MyCart[Product_ID])>
	<CFSET OrderTotal = OrderTotal + MyCart[Product_ID] * Price>
</CFLOOP>
<CFSET QueryAddColumn(GetItems, "Quantity", ListToArray(QtyList))>

<CFTRANSACTION>
	<CFQUERY DATASOURCE="#Request.DSN#">
		INSERT INTO Orders (UserName, ShipName, Email, MailStop, Notes, OrderTotal, OrderDate)
		VALUES ('#Request.UserName#', '#Left(Trim(Form.ShipName), 60)#', '#Left(Trim(Form.Email), 60)#',
		        '#Left(Trim(Form.MailStop), 20)#', '#Left(Trim(Form.Notes), 255)#', #OrderTotal#,
		        <CFQUERYPARAM CFSQLTYPE="CF_SQL_TIMESTAMP" VALUE="#Now()#">)
	</CFQUERY>
	<CFQUERY NAME="GetOrderID" DATASOURCE="#Request.DSN#">
		SELECT MAX(Order_ID) AS NewID FROM Orders
	</CFQUERY>
	<CFSET OrderID = GetOrderID.NewID>
	<CFLOOP QUERY="GetItems">
		<CFQUERY DATASOURCE="#Request.DSN#">
			INSERT INTO OrderItems (Order_ID, Product_ID, Quantity, UnitPrice)
			VALUES (#OrderID#, #Product_ID#, #Quantity#, #Price#)
		</CFQUERY>
		<CFQUERY DATASOURCE="#Request.DSN#">
			UPDATE Products SET InStock = InStock - #Quantity#
			WHERE Product_ID = #Product_ID# AND InStock >= #Quantity#
		</CFQUERY>
	</CFLOOP>
</CFTRANSACTION>
<!--- every row gets the order number too, so CFMAIL can GROUP on it --->
<CFSET QueryAddColumn(GetItems, "Order_ID", ListToArray(RepeatString("#OrderID#,", GetItems.RecordCount)))>

<!--- the confirmation e-mail. With QUERY alone CFMAIL would send one message
      per row; GROUP makes it one message per order, and the inner CFOUTPUT
      writes one line per item. --->
<CFMAIL TO="#Trim(Form.Email)#"
	FROM="#Request.OrdersFrom#"
	SUBJECT="Company Store order #OrderID# confirmation"
	QUERY="GetItems" GROUP="Order_ID">Hello #Form.ShipName#,

Thank you for shopping at the GlobalCorp Company Store.
Your order number is #OrderID#. It will be delivered to
mail stop #Form.MailStop# within two business days.

<CFOUTPUT>  #LJustify(SKU, 8)# #LJustify(ProductName, 38)# #RJustify(Quantity, 3)# x #RJustify(DollarFormat(Price), 9)#
</CFOUTPUT>
  Order total: #DollarFormat(OrderTotal)# (charged to your cost center)

Questions? Reply to this message or call the Help Desk at #Request.HelpDesk#.

-- 
GlobalCorp Company Store
</CFMAIL>

<!--- all done: empty the cart --->
<CFLOCK SCOPE="Session" TYPE="Exclusive" TIMEOUT="10">
	<CFSET StructClear(Session.Cart)>
</CFLOCK>

<CFINCLUDE TEMPLATE="../header.cfm">

<CFOUTPUT>
<P><IMG SRC="/CFIDE/administrator/images/check.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
Your order number is <FONT SIZE=4 COLOR="##CC0000"><B>#OrderID#</B></FONT>.
A confirmation has been sent to <B>#HTMLEditFormat(Form.Email)#</B>.</P>
<P>Deliver to: <B>#HTMLEditFormat(Form.ShipName)#</B>, mail stop <B>#HTMLEditFormat(Form.MailStop)#</B></P>
</CFOUTPUT>
<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="#CCCCCC"><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Item</B></FONT></TD><TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2><B>Qty</B></FONT></TD><TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2><B>Price</B></FONT></TD></TR>
<CFOUTPUT QUERY="GetItems">
<TR><TD><FONT FACE="#Request.Font#" SIZE=2>#ProductName#</FONT></TD><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2>#Quantity#</FONT></TD><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2>#DollarFormat(Price)#</FONT></TD></TR>
</CFOUTPUT>
<CFOUTPUT>
<TR><TD COLSPAN=2 ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>Total</B></FONT></TD><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>#DollarFormat(OrderTotal)#</B></FONT></TD></TR>
</CFOUTPUT>
</TABLE>
<P><A HREF="index.cfm">Back to the Company Store</A> | <A HREF="orders.cfm">Your orders</A></P>

<CFINCLUDE TEMPLATE="../footer.cfm">
