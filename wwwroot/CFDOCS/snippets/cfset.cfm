<!--- Simple values, a dynamic name, a structure and an array --->
<CFSET Product = "US Robotics 56K Modem">
<CFSET Price = 129.95>
<CFSET Qty = 3>
<CFSET Total = Price * Qty>
<CFSET Ordered = CreateDate(1999, 11, 30)>
<CFLOOP INDEX="i" FROM="1" TO="3">
  <CFSET "Box#i#" = "Carton " & i & " of 3">
</CFLOOP>
<CFSET Customer = StructNew()>
<CFSET Customer.Name = "Carol Reardon">
<CFSET Customer.Ship.City = "Boston">
<CFSET Extras = ArrayNew(1)>
<CFSET Extras[1] = "Phone cable">
<CFSET ArrayAppend(Extras, "Mouse pad")>

<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH ALIGN="LEFT">Variable</TH><TH ALIGN="LEFT">Value</TH></TR>
<TR><TD>Product</TD><TD>#Product#</TD></TR>
<TR><TD>Total (Price * Qty)</TD><TD>#DollarFormat(Total)#</TD></TR>
<TR><TD>Ordered</TD><TD>#DateFormat(Ordered, "mmmm d, yyyy")#</TD></TR>
<TR><TD>Box1 .. Box3</TD><TD>#Box1#; #Box2#; #Box3#</TD></TR>
<TR><TD>Customer.Name</TD><TD>#Customer.Name#</TD></TR>
<TR><TD>Customer.Ship.City</TD><TD>#Customer.Ship.City#</TD></TR>
<TR><TD>Extras</TD><TD>#ArrayToList(Extras, ", ")#</TD></TR>
</TABLE>
</CFOUTPUT>
