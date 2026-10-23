<CFSET Basket = StructNew()>
<CFSET Basket.Apples = 3>
<CFSET Basket.Pears = 2>
<CFSET SameBasket = Basket>
<CFOUTPUT>
<P>Before: #StructCount(Basket)# keys</P>
<CFSET Temp = StructClear(Basket)>
<P>After StructClear: #StructCount(Basket)# keys.
StructIsEmpty(SameBasket) = #StructIsEmpty(SameBasket)#
(it is the same structure).</P>
</CFOUTPUT>
