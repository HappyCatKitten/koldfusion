<!---
	catalog/cart.cfm - the shopping cart, kept in the Session scope.
	Session.Cart is a structure: key = Product_ID, value = quantity.
	Actions (Form or URL variable "action"):
	  add     Product_ID, Qty      put an item in the cart
	  update  Qty_<Product_ID>     change quantities (0 removes)
	  remove  Product_ID           take an item out
	  empty                        start over
	Every change happens inside an exclusive CFLOCK on the Session scope,
	because a visitor with two browser windows open can make two requests at once.
--->
<CFSET Section = "catalog">
<CFSET PageTitle = "Your Shopping Cart">
<CFIF IsDefined("Form.action")>
	<CFSET CartAction = Form.action>
<CFELSEIF IsDefined("URL.action")>
	<CFSET CartAction = URL.action>
<CFELSE>
	<CFSET CartAction = "view">
</CFIF>

<CFIF CartAction IS "add">
	<CFPARAM NAME="Form.Product_ID" DEFAULT="0">
	<CFPARAM NAME="Form.Qty" DEFAULT="1">
	<CFSET AddQty = Int(Val(Form.Qty))>
	<CFIF AddQty LT 1><CFSET AddQty = 1></CFIF>
	<CFQUERY NAME="CheckProduct" DATASOURCE="#Request.DSN#">
		SELECT Product_ID FROM Products WHERE Product_ID = #Val(Form.Product_ID)#
	</CFQUERY>
	<CFIF CheckProduct.RecordCount>
		<CFLOCK SCOPE="Session" TYPE="Exclusive" TIMEOUT="10">
			<CFIF StructKeyExists(Session.Cart, CheckProduct.Product_ID)>
				<CFSET Session.Cart[CheckProduct.Product_ID] = Session.Cart[CheckProduct.Product_ID] + AddQty>
			<CFELSE>
				<CFSET Session.Cart[CheckProduct.Product_ID] = AddQty>
			</CFIF>
		</CFLOCK>
	</CFIF>
	<!--- redirect so that pressing Reload does not add the item again --->
	<CFLOCATION URL="cart.cfm?added=#Val(Form.Product_ID)#" ADDTOKEN="No">

<CFELSEIF CartAction IS "update">
	<CFLOCK SCOPE="Session" TYPE="Exclusive" TIMEOUT="10">
		<CFLOOP COLLECTION="#Session.Cart#" ITEM="ProdID">
			<CFIF IsDefined("Form.Qty_#ProdID#")>
				<CFSET NewQty = Int(Val(Form["Qty_" & ProdID]))>
				<CFIF NewQty GT 0>
					<CFSET Session.Cart[ProdID] = NewQty>
				<CFELSE>
					<CFSET StructDelete(Session.Cart, ProdID)>
				</CFIF>
			</CFIF>
		</CFLOOP>
	</CFLOCK>

<CFELSEIF CartAction IS "remove" AND IsDefined("URL.Product_ID")>
	<CFLOCK SCOPE="Session" TYPE="Exclusive" TIMEOUT="10">
		<CFSET StructDelete(Session.Cart, URL.Product_ID)>
	</CFLOCK>

<CFELSEIF CartAction IS "empty">
	<CFLOCK SCOPE="Session" TYPE="Exclusive" TIMEOUT="10">
		<CFSET StructClear(Session.Cart)>
	</CFLOCK>
</CFIF>

<!--- read a copy of the cart for display --->
<CFLOCK SCOPE="Session" TYPE="ReadOnly" TIMEOUT="10">
	<CFSET MyCart = Duplicate(Session.Cart)>
</CFLOCK>

<CFIF NOT StructIsEmpty(MyCart)>
	<CFQUERY NAME="GetCartItems" DATASOURCE="#Request.DSN#">
		SELECT Product_ID, SKU, ProductName, Price
		FROM Products
		WHERE Product_ID IN (#StructKeyList(MyCart)#)
		ORDER BY ProductName
	</CFQUERY>
</CFIF>

<CFINCLUDE TEMPLATE="../header.cfm">

<CFIF IsDefined("URL.added")>
	<CFQUERY NAME="JustAdded" DATASOURCE="#Request.DSN#">
		SELECT ProductName FROM Products WHERE Product_ID = #Val(URL.added)#
	</CFQUERY>
	<CFOUTPUT><P><IMG SRC="/CFIDE/administrator/images/check.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE> <B>#JustAdded.ProductName#</B> was added to your cart.</P></CFOUTPUT>
</CFIF>

<CFIF StructIsEmpty(MyCart)>
	<P>Your cart is empty. <A HREF="index.cfm">Visit the Company Store</A> to fill it up.</P>
<CFELSE>
	<FORM ACTION="cart.cfm" METHOD="POST">
	<INPUT TYPE="Hidden" NAME="action" VALUE="update">
	<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%">
	<TR BGCOLOR="#003366">
		<TD><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Item</B></FONT></TD>
		<TD ALIGN=CENTER><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Qty</B></FONT></TD>
		<TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Each</B></FONT></TD>
		<TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Total</B></FONT></TD>
		<TD></TD>
	</TR>
	<CFSET GrandTotal = 0>
	<CFOUTPUT QUERY="GetCartItems">
	<CFSET LineTotal = MyCart[Product_ID] * Price>
	<CFSET GrandTotal = GrandTotal + LineTotal>
	<TR BGCOLOR="###IIf(CurrentRow MOD 2, DE('FFFFFF'), DE('F0F0F0'))#">
		<TD><FONT FACE="#Request.Font#" SIZE=2><A HREF="product.cfm?Product_ID=#Product_ID#">#ProductName#</A> <FONT SIZE=1 COLOR="##666666">#SKU#</FONT></FONT></TD>
		<TD ALIGN=CENTER><INPUT TYPE="Text" NAME="Qty_#Product_ID#" VALUE="#MyCart[Product_ID]#" SIZE=3 MAXLENGTH=3></TD>
		<TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2>#DollarFormat(Price)#</FONT></TD>
		<TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2>#DollarFormat(LineTotal)#</FONT></TD>
		<TD><FONT FACE="#Request.Font#" SIZE=1><A HREF="cart.cfm?action=remove&Product_ID=#Product_ID#">remove</A></FONT></TD>
	</TR>
	</CFOUTPUT>
	<CFOUTPUT>
	<TR><TD COLSPAN=3 ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>Order total:</B></FONT></TD>
		<TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>#DollarFormat(GrandTotal)#</B></FONT></TD><TD></TD></TR>
	<TR><TD COLSPAN=5><FONT FACE="#Request.Font#" SIZE=1>Interoffice delivery is free. Set a quantity to 0 to remove an item.</FONT></TD></TR>
	</CFOUTPUT>
	</TABLE>
	<P>
	<INPUT TYPE="Submit" VALUE="Update Quantities">
	<INPUT TYPE="Button" VALUE="Keep Shopping" onClick="location.href='index.cfm'">
	<INPUT TYPE="Button" VALUE="Empty Cart" onClick="if (confirm('Remove everything from your cart?')) location.href='cart.cfm?action=empty'">
	<INPUT TYPE="Button" VALUE="Check Out &gt;&gt;" onClick="location.href='checkout.cfm'">
	</P>
	</FORM>
</CFIF>

<CFINCLUDE TEMPLATE="../footer.cfm">
