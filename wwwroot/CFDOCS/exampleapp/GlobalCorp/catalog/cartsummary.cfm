<!---
	cartsummary.cfm - custom tag <CF_CARTSUMMARY> (also called with CFMODULE)
	Shows a small "your cart" box with the item count and running total.
	Attributes:
	  TextColor  (optional) font color, default white for the dark nav bar
	  Link       (optional) Yes/No - link to the cart page, default Yes
--->
<CFPARAM NAME="Attributes.TextColor" DEFAULT="##FFFFFF">
<CFPARAM NAME="Attributes.Link" DEFAULT="Yes">

<!--- Take a private copy of the cart while holding a read lock --->
<CFLOCK SCOPE="Session" TYPE="ReadOnly" TIMEOUT="10">
	<CFIF IsDefined("Session.Cart")>
		<CFSET MyCart = Duplicate(Session.Cart)>
	<CFELSE>
		<CFSET MyCart = StructNew()>
	</CFIF>
</CFLOCK>

<CFSET ItemCount = 0>
<CFSET CartTotal = 0>
<CFIF NOT StructIsEmpty(MyCart)>
	<CFQUERY NAME="CartPrices" DATASOURCE="#Request.DSN#">
		SELECT Product_ID, Price
		FROM Products
		WHERE Product_ID IN (#StructKeyList(MyCart)#)
	</CFQUERY>
	<CFLOOP QUERY="CartPrices">
		<CFSET ItemCount = ItemCount + MyCart[Product_ID]>
		<CFSET CartTotal = CartTotal + (MyCart[Product_ID] * Price)>
	</CFLOOP>
</CFIF>

<CFOUTPUT>
<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0><TR VALIGN=MIDDLE>
<TD><IMG SRC="#Request.Images#/ic_cart.gif" WIDTH=32 HEIGHT=32 ALT="Shopping cart"></TD>
<TD><FONT FACE="Arial, Helvetica" SIZE=1 COLOR="#Attributes.TextColor#">&nbsp;
<CFIF Attributes.Link><A HREF="#Request.Root#/catalog/cart.cfm"><FONT COLOR="#Attributes.TextColor#"></CFIF><B>Your Cart</B><CFIF Attributes.Link></FONT></A></CFIF><BR>
<CFIF ItemCount EQ 0>
	&nbsp;(empty)
<CFELSE>
	&nbsp;#ItemCount# item<CFIF ItemCount NEQ 1>s</CFIF>, #DollarFormat(CartTotal)#
</CFIF>
</FONT></TD>
</TR></TABLE>
</CFOUTPUT>
