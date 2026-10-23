<CFSET Orders = StructNew()>
<CFSET Orders.Morning = StructNew()>
<CFSET Orders.Morning.Status = "Shipped">
<CFSET Orders.Morning.Item = "Y2K survival kit">
<CFSET Orders.Evening = StructNew()>
<CFSET Orders.Evening.Status = "Backordered">
<CFSET Orders.Evening.Item = "56K modem">
<CFSET Late = StructFindValue(Orders, "backordered", "all")>
<CFOUTPUT>
<CFLOOP FROM="1" TO="#ArrayLen(Late)#" INDEX="i">
  <P>#Late[i].Path#: the #Late[i].Owner.Item# is #Late[i].Owner[Late[i].Key]#.</P>
</CFLOOP>
</CFOUTPUT>
