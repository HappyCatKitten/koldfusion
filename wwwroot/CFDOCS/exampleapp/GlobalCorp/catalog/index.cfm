<!---
	catalog/index.cfm - the GlobalCorp Company Store front page
	Lists the categories and this week's featured (sale) items.
	Prices are drawn by the CF_PRICETAG custom tag (pricetag.cfm in this directory).
--->
<CFSET PageTitle = "Company Store">
<CFSET Section = "catalog">

<CFQUERY NAME="GetCategories" DATASOURCE="#Request.DSN#">
	SELECT c.Category_ID, c.CategoryName, c.Blurb, COUNT(p.Product_ID) AS Items
	FROM Categories c LEFT JOIN Products p ON p.Category_ID = c.Category_ID
	GROUP BY c.Category_ID, c.CategoryName, c.Blurb, c.SortOrder
	ORDER BY c.SortOrder
</CFQUERY>

<CFQUERY NAME="GetFeatured" DATASOURCE="#Request.DSN#">
	SELECT Product_ID, Category_ID, SKU, ProductName, ShortDesc, Price
	FROM Products
	WHERE Featured = 1
	ORDER BY Price DESC
</CFQUERY>

<CFINCLUDE TEMPLATE="../header.cfm">

<CFOUTPUT>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0><TR VALIGN=TOP>
<TD><FONT FACE="#Request.Font#" SIZE=2>Order desk supplies, computer accessories and GlobalCorp gear for delivery
to your mail stop. Orders are charged to your department's cost center.</FONT></TD>
<TD ALIGN=RIGHT NOWRAP>
	<FORM ACTION="search.cfm" METHOD="GET">
	<FONT FACE="#Request.Font#" SIZE=2><B>Search:</B></FONT>
	<INPUT TYPE="Text" NAME="criteria" SIZE=18> <INPUT TYPE="Submit" VALUE="Find">
	</FORM>
</TD>
</TR></TABLE>
</CFOUTPUT>

<TABLE WIDTH="100%" BORDER=0 CELLPADDING=6 CELLSPACING=0>
<TR VALIGN=TOP>
<TD WIDTH="55%">
	<FONT FACE="Arial, Helvetica" SIZE=3 COLOR="#003366"><B>Departments</B></FONT>
	<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0>
	<CFOUTPUT QUERY="GetCategories">
	<TR VALIGN=TOP>
		<TD><A HREF="category.cfm?Category_ID=#Category_ID#"><IMG SRC="#Request.Images#/cat_#Category_ID#.gif" WIDTH=50 HEIGHT=40 BORDER=0 ALT="#CategoryName#"></A></TD>
		<TD><FONT FACE="#Request.Font#" SIZE=2><A HREF="category.cfm?Category_ID=#Category_ID#"><B>#CategoryName#</B></A>
		<FONT SIZE=1 COLOR="##666666">(#Items# items)</FONT><BR>#Blurb#</FONT></TD>
	</TR>
	</CFOUTPUT>
	</TABLE>
	<CFOUTPUT><P><FONT FACE="#Request.Font#" SIZE=2><A HREF="cart.cfm">View your cart</A> | <A HREF="orders.cfm">Your past orders</A></FONT></CFOUTPUT>
</TD>
<TD BGCOLOR="#FFFFE0">
	<FONT FACE="Arial, Helvetica" SIZE=3 COLOR="#CC0000"><B>This Week's Specials</B></FONT>
	<CFOUTPUT QUERY="GetFeatured">
	<P><FONT FACE="#Request.Font#" SIZE=2><A HREF="product.cfm?Product_ID=#Product_ID#"><B>#ProductName#</B></A><BR>
	#ShortDesc#</FONT><BR>
	<CF_PRICETAG PRICE="#Price#" ONSALE="Yes" SIZE="2">
	</CFOUTPUT>
</TD>
</TR>
</TABLE>

<CFINCLUDE TEMPLATE="../footer.cfm">
