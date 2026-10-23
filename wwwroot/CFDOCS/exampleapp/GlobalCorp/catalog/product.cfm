<!---
	catalog/product.cfm - one product, with an add-to-cart form
	  ?Product_ID=n
--->
<CFPARAM NAME="URL.Product_ID" DEFAULT="0">
<CFSET Section = "catalog">

<CFQUERY NAME="GetProduct" DATASOURCE="#Request.DSN#">
	SELECT p.*, c.CategoryName
	FROM Products p, Categories c
	WHERE p.Category_ID = c.Category_ID
	  AND p.Product_ID = #Val(URL.Product_ID)#
</CFQUERY>
<CFIF GetProduct.RecordCount EQ 0>
	<CFLOCATION URL="index.cfm" ADDTOKEN="No">
</CFIF>

<!--- other items from the same category --->
<CFQUERY NAME="Related" DATASOURCE="#Request.DSN#" MAXROWS="3">
	SELECT Product_ID, ProductName, Price
	FROM Products
	WHERE Category_ID = #GetProduct.Category_ID# AND Product_ID <> #GetProduct.Product_ID#
	ORDER BY Featured DESC, Price
</CFQUERY>

<CFSET PageTitle = GetProduct.ProductName>
<CFINCLUDE TEMPLATE="../header.cfm">

<CFOUTPUT QUERY="GetProduct">
<FONT FACE="#Request.Font#" SIZE=2><A HREF="index.cfm">Company Store</A> &gt; <A HREF="category.cfm?Category_ID=#Category_ID#">#CategoryName#</A> &gt; #ProductName#</FONT>
<TABLE BORDER=0 CELLPADDING=8 CELLSPACING=0>
<TR VALIGN=TOP>
	<TD><IMG SRC="#Request.Images#/cat_#Category_ID#.gif" WIDTH=100 HEIGHT=80 BORDER=1 ALT="#ProductName#"></TD>
	<TD><FONT FACE="#Request.Font#" SIZE=2>
		<B>#ShortDesc#</B>
		<P>#LongDesc#</P>
		<FONT SIZE=1>Item number: #SKU#<BR>
		<CFIF InStock GT 20>In stock<CFELSEIF InStock GT 0><FONT COLOR="##CC6600">Only #InStock# left!</FONT><CFELSE><FONT COLOR="##CC0000">Back-ordered</FONT></CFIF>
		</FONT></FONT>
		<P><CF_PRICETAG PRICE="#Price#" ONSALE="#Featured#">
		<CFIF InStock GT 0>
		<FORM ACTION="cart.cfm" METHOD="POST">
		<INPUT TYPE="Hidden" NAME="action" VALUE="add">
		<INPUT TYPE="Hidden" NAME="Product_ID" VALUE="#Product_ID#">
		<INPUT TYPE="Hidden" NAME="Qty_integer" VALUE="Quantity must be a whole number.">
		<FONT FACE="#Request.Font#" SIZE=2>Quantity:</FONT> <INPUT TYPE="Text" NAME="Qty" VALUE="1" SIZE=3 MAXLENGTH=3>
		<INPUT TYPE="Submit" VALUE="Add to Cart">
		</FORM>
		</CFIF>
	</TD>
</TR>
</TABLE>
</CFOUTPUT>

<CFIF Related.RecordCount>
	<P><B>You might also like:</B><BR>
	<CFOUTPUT QUERY="Related"><A HREF="product.cfm?Product_ID=#Product_ID#">#ProductName#</A> (#DollarFormat(Price)#)<BR></CFOUTPUT>
	</P>
</CFIF>

<CFINCLUDE TEMPLATE="../footer.cfm">
