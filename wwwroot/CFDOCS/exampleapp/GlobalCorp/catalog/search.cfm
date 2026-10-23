<!---
	catalog/search.cfm - full-text search of the catalog with Verity.
	The first search after the server starts (or ?reindex=yes) builds the index:
	  1. CFSEARCH the collection; if that fails the collection doesn't exist,
	     so CFCOLLECTION ACTION="Create" makes it
	  2. CFINDEX ACTION="Refresh" TYPE="Custom" indexes the rows of a query
	Then CFSEARCH finds matching products. KEY is the Product_ID, so each hit
	links straight to the product page.
--->
<CFPARAM NAME="URL.criteria" DEFAULT="">
<CFSET Section = "catalog">
<CFSET PageTitle = "Search the Company Store">
<CFSET CollectionName = "GlobalCorpCatalog">

<CFLOCK SCOPE="Application" TYPE="ReadOnly" TIMEOUT="10">
	<CFSET AlreadyIndexed = Application.CatalogIndexed>
</CFLOCK>

<CFIF NOT AlreadyIndexed OR IsDefined("URL.reindex")>
	<CFLOCK NAME="GlobalCorpCatalogIndexer" TYPE="Exclusive" TIMEOUT="60">
		<CFTRY>
			<CFSEARCH NAME="Probe" COLLECTION="#CollectionName#" CRITERIA="widget" MAXROWS="1">
			<CFCATCH TYPE="Any">
				<!--- On CF for Windows you would add PATH="C:\CFUSION\Verity\Collections\";
				      KoldFusion puts new collections in its own verity directory by default --->
				<CFCOLLECTION ACTION="Create" COLLECTION="#CollectionName#" LANGUAGE="English">
			</CFCATCH>
		</CFTRY>
		<CFQUERY NAME="IndexMe" DATASOURCE="#Request.DSN#">
			SELECT p.Product_ID, p.SKU, p.ProductName, p.ShortDesc, p.LongDesc, p.Price, c.CategoryName
			FROM Products p, Categories c
			WHERE p.Category_ID = c.Category_ID
		</CFQUERY>
		<CFINDEX ACTION="Refresh" COLLECTION="#CollectionName#" TYPE="Custom" QUERY="IndexMe"
			KEY="Product_ID" TITLE="ProductName" BODY="SKU,ProductName,ShortDesc,LongDesc,CategoryName"
			CUSTOM1="Price" CUSTOM2="CategoryName">
	</CFLOCK>
	<CFLOCK SCOPE="Application" TYPE="Exclusive" TIMEOUT="10">
		<CFSET Application.CatalogIndexed = TRUE>
	</CFLOCK>
	<CFSET JustIndexed = IndexMe.RecordCount>
</CFIF>

<CFIF Len(Trim(URL.criteria))>
	<CFSEARCH NAME="Results" COLLECTION="#CollectionName#" CRITERIA="#Trim(URL.criteria)#" MAXROWS="25">
</CFIF>

<CFINCLUDE TEMPLATE="../header.cfm">

<CFOUTPUT>
<FONT FACE="#Request.Font#" SIZE=2><A HREF="index.cfm">Company Store</A> &gt; Search</FONT>
<FORM ACTION="search.cfm" METHOD="GET">
<INPUT TYPE="Text" NAME="criteria" SIZE=30 VALUE="#HTMLEditFormat(URL.criteria)#">
<INPUT TYPE="Submit" VALUE="Search">
<FONT FACE="#Request.Font#" SIZE=1>Try <A HREF="search.cfm?criteria=widget">widget</A>, <A HREF="search.cfm?criteria=keyboard or mouse">keyboard or mouse</A>,
<A HREF="search.cfm?criteria=%22year 2000%22">"year 2000"</A> or <A HREF="search.cfm?criteria=cotton">cotton</A>.</FONT>
</FORM>
<CFIF IsDefined("JustIndexed")><P><FONT SIZE=1 COLOR="##666666">(The Verity collection #CollectionName# was just indexed: #JustIndexed# products.)</FONT></P></CFIF>
</CFOUTPUT>

<CFIF IsDefined("Results")>
	<CFOUTPUT><P><B>#Results.RecordCount#</B> product<CFIF Results.RecordCount NEQ 1>s</CFIF> matched <B>#HTMLEditFormat(URL.criteria)#</B>.</P></CFOUTPUT>
	<CFIF Results.RecordCount>
	<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%">
	<TR BGCOLOR="#003366">
		<TD><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Score</B></FONT></TD>
		<TD><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Product</B></FONT></TD>
		<TD><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Department</B></FONT></TD>
		<TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Price</B></FONT></TD>
	</TR>
	<CFOUTPUT QUERY="Results">
	<TR VALIGN=TOP BGCOLOR="###IIf(CurrentRow MOD 2, DE('FFFFFF'), DE('F0F0F0'))#">
		<TD><FONT FACE="#Request.Font#" SIZE=1>#NumberFormat(Score * 100, "999")#%</FONT></TD>
		<TD><FONT FACE="#Request.Font#" SIZE=2><A HREF="product.cfm?Product_ID=#Key#"><B>#Title#</B></A><BR>
			<FONT SIZE=1>#Left(Summary, 120)#...</FONT></FONT></TD>
		<TD><FONT FACE="#Request.Font#" SIZE=2>#Custom2#</FONT></TD>
		<TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2>#DollarFormat(Custom1)#</FONT></TD>
	</TR>
	</CFOUTPUT>
	</TABLE>
	</CFIF>
</CFIF>
<CFIF Request.IsAdmin><P><FONT SIZE=1><A HREF="search.cfm?reindex=yes">Rebuild the search index</A></FONT></P></CFIF>

<CFINCLUDE TEMPLATE="../footer.cfm">
