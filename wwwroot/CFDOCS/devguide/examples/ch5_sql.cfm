<!--- ch5_sql.cfm: INSERT, UPDATE and DELETE with CFQUERYPARAM.
      The demo product is deleted again at the end. --->
<CFSET NewName = "Millennium Bug Spray (demo)">
<CFSET NewPrice = 19.99>

<CFTRANSACTION>
  <CFQUERY DATASOURCE="cfsnippets">
  INSERT INTO Products (Name, Description, Price, Category, InStock)
  VALUES (
    <CFQUERYPARAM VALUE="#NewName#" CFSQLTYPE="CF_SQL_VARCHAR">,
    <CFQUERYPARAM VALUE="Keeps two-digit years out of your code." CFSQLTYPE="CF_SQL_VARCHAR">,
    <CFQUERYPARAM VALUE="#NewPrice#" CFSQLTYPE="CF_SQL_MONEY">,
    'Software',
    <CFQUERYPARAM VALUE="10" CFSQLTYPE="CF_SQL_INTEGER">)
  </CFQUERY>
  <CFQUERY NAME="GetNew" DATASOURCE="cfsnippets">
  SELECT MAX(ProductID) AS NewID FROM Products
  </CFQUERY>
</CFTRANSACTION>
<CFSET NewID = GetNew.NewID>

<!--- Half price for the new millennium! --->
<CFQUERY DATASOURCE="cfsnippets">
UPDATE Products
SET Price = Price / 2, InStock = InStock - 1
WHERE ProductID = <CFQUERYPARAM VALUE="#NewID#" CFSQLTYPE="CF_SQL_INTEGER">
</CFQUERY>

<CFQUERY NAME="GetSoftware" DATASOURCE="cfsnippets">
SELECT ProductID, Name, Price, InStock
FROM Products
WHERE Category = 'Software'
ORDER BY Price DESC
</CFQUERY>

<H3>Software catalog</H3>
<TABLE BORDER="1" CELLPADDING="3" CELLSPACING="0">
<TR><TH>Product</TH><TH>Price</TH><TH>In stock</TH></TR>
<CFOUTPUT QUERY="GetSoftware">
<TR<CFIF ProductID IS NewID> BGCOLOR="##FFFFCC"</CFIF>>
  <TD>#Name#</TD>
  <TD ALIGN="RIGHT">#DollarFormat(Price)#</TD>
  <TD ALIGN="RIGHT">#InStock#</TD>
</TR>
</CFOUTPUT>
</TABLE>

<!--- Tidy up --->
<CFQUERY DATASOURCE="cfsnippets">
DELETE FROM Products
WHERE ProductID = <CFQUERYPARAM VALUE="#NewID#" CFSQLTYPE="CF_SQL_INTEGER">
</CFQUERY>
<CFOUTPUT><P>The demo product (ID #NewID#) has been deleted again.</P></CFOUTPUT>
