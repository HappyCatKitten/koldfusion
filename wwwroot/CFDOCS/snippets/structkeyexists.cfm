<CFSET Inventory = StructNew()>
<CFSET Inventory.Modems = 12>
<CFSET Inventory["Zip Disks"] = 40>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<CFLOOP LIST="Modems,zip disks,Pagers" INDEX="Item">
<TR><TD>#Item#</TD>
<TD><CFIF StructKeyExists(Inventory, Item)>#Inventory[Item]# in stock<CFELSE>not carried</CFIF></TD></TR>
</CFLOOP>
</TABLE>
</CFOUTPUT>
