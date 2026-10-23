<!--- Neither Request.Shop nor Request.Shop.Cart exists yet --->
<CFSET Cart = StructGet("Request.Shop.Cart")>
<CFSET Cart.Modems = 2>
<CFSET Cart.Cables = 5>

<!--- Asking again returns the same structure --->
<CFSET Again = StructGet("Request.Shop.Cart")>
<CFOUTPUT>
<P>IsStruct(Request.Shop) = #IsStruct(Request.Shop)#</P>
<P>Request.Shop.Cart.Modems = #Request.Shop.Cart.Modems#</P>
<P>Keys seen through the second call: #StructKeyList(Again)#</P>
</CFOUTPUT>
