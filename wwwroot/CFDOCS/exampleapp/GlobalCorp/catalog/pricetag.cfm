<!---
	pricetag.cfm - custom tag <CF_PRICETAG>
	Formats a catalog price. Items in the featured list get a "sale" badge
	and show the regular price (15% higher) struck through.
	Attributes:
	  Price     (required) the selling price
	  OnSale    (optional) Yes/No, default No
	  Size      (optional) FONT SIZE for the price, default 3
--->
<CFIF NOT IsDefined("Attributes.Price")>
	<CFTHROW MESSAGE="CF_PRICETAG requires a PRICE attribute.">
</CFIF>
<CFPARAM NAME="Attributes.OnSale" DEFAULT="No">
<CFPARAM NAME="Attributes.Size" DEFAULT="3">
<CFIF NOT IsNumeric(Attributes.Price)>
	<CFTHROW MESSAGE="CF_PRICETAG: PRICE must be a number, not '#Attributes.Price#'.">
</CFIF>
<CFOUTPUT>
<CFIF Attributes.OnSale>
	<FONT FACE="Arial, Helvetica" SIZE=1 COLOR="##666666">Regularly <STRIKE>#DollarFormat(Round(Attributes.Price * 115) / 100)#</STRIKE></FONT><BR>
	<FONT FACE="Arial, Helvetica" SIZE="#Attributes.Size#" COLOR="##CC0000"><B>#DollarFormat(Attributes.Price)#</B></FONT>
	<IMG SRC="#Request.Images#/sale.gif" WIDTH=60 HEIGHT=40 ALIGN=ABSMIDDLE ALT="Sale!">
<CFELSE>
	<FONT FACE="Arial, Helvetica" SIZE="#Attributes.Size#" COLOR="##006600"><B>#DollarFormat(Attributes.Price)#</B></FONT>
</CFIF>
</CFOUTPUT>
