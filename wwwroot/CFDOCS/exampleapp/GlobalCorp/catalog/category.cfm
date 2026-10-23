<!---
	catalog/category.cfm - every product in one category
	  ?Category_ID=n
--->
<CFPARAM NAME="URL.Category_ID" DEFAULT="0">
<CFSET Section = "catalog">

<CFQUERY NAME="GetCategory" DATASOURCE="#Request.DSN#">
	SELECT Category_ID, CategoryName, Blurb FROM Categories WHERE Category_ID = #Val(URL.Category_ID)#
</CFQUERY>
<CFIF GetCategory.RecordCount EQ 0>
	<CFLOCATION URL="index.cfm" ADDTOKEN="No">
</CFIF>

<CFQUERY NAME="GetProducts" DATASOURCE="#Request.DSN#">
	SELECT Product_ID, SKU, ProductName, ShortDesc, Price, InStock, Featured
	FROM Products
	WHERE Category_ID = #GetCategory.Category_ID#
	ORDER BY Price
</CFQUERY>

<CFSET PageTitle = GetCategory.CategoryName>
<CFINCLUDE TEMPLATE="../header.cfm">

<CFOUTPUT>
<FONT FACE="#Request.Font#" SIZE=2><A HREF="index.cfm">Company Store</A> &gt; #GetCategory.CategoryName#</FONT>
<P><IMG SRC="#Request.Images#/cat_#GetCategory.Category_ID#.gif" WIDTH=100 HEIGHT=80 ALIGN=RIGHT ALT="">#GetCategory.Blurb#</P>
</CFOUTPUT>

<TABLE WIDTH="100%" BORDER=0 CELLPADDING=4 CELLSPACING=0>
<TR BGCOLOR="#003366">
	<TD><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Item</B></FONT></TD>
	<TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Price</B></FONT></TD>
	<TD ALIGN=CENTER><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Order</B></FONT></TD>
</TR>
<CFOUTPUT QUERY="GetProducts">
<TR VALIGN=TOP BGCOLOR="###IIf(CurrentRow MOD 2, DE('FFFFFF'), DE('F0F0F0'))#">
	<TD><FONT FACE="#Request.Font#" SIZE=2><A HREF="product.cfm?Product_ID=#Product_ID#"><B>#ProductName#</B></A>
		<FONT SIZE=1 COLOR="##666666">#SKU#</FONT><BR>#ShortDesc#</FONT></TD>
	<TD ALIGN=RIGHT NOWRAP><CF_PRICETAG PRICE="#Price#" ONSALE="#Featured#" SIZE="2"></TD>
	<TD ALIGN=CENTER NOWRAP>
	<CFIF InStock GT 0>
		<FORM ACTION="cart.cfm" METHOD="POST">
		<INPUT TYPE="Hidden" NAME="action" VALUE="add">
		<INPUT TYPE="Hidden" NAME="Product_ID" VALUE="#Product_ID#">
		<INPUT TYPE="Text" NAME="Qty" VALUE="1" SIZE=2 MAXLENGTH=3>
		<INPUT TYPE="Submit" VALUE="Add to Cart">
		</FORM>
	<CFELSE>
		<FONT FACE="#Request.Font#" SIZE=1 COLOR="##CC0000">Back-ordered</FONT>
	</CFIF>
	</TD>
</TR>
</CFOUTPUT>
</TABLE>

<CFINCLUDE TEMPLATE="../footer.cfm">
