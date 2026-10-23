<CFSET Phone = StructNew()>
<CFSET Temp = StructInsert(Phone, "Help Desk", "x4357")>
<CFSET Temp = StructInsert(Phone, "Cafeteria", "x2233")>
<CFTRY>
  <CFSET Temp = StructInsert(Phone, "Help Desk", "x0000")>
<CFCATCH TYPE="Expression">
  <CFOUTPUT><P><I>#CFCATCH.Message#</I></P></CFOUTPUT>
</CFCATCH>
</CFTRY>
<CFSET Temp = StructInsert(Phone, "Cafeteria", "x2234", TRUE)>
<TABLE BORDER=1 CELLPADDING=3>
<CFLOOP COLLECTION="#Phone#" ITEM="Who">
<CFOUTPUT><TR><TD>#Who#</TD><TD>#Phone[Who]#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
