<CFSET Visitor = StructNew()>
<CFSET Visitor.Name = "Pat">
<CFSET Visitor.Browser = "Netscape 4.7">
<CFSET Visitor["Favorite Site"] = "www.gibson.example">
<CFOUTPUT>
<P>IsStruct(Visitor) = #IsStruct(Visitor)#, #StructCount(Visitor)# keys.</P>
<UL>
<CFLOOP COLLECTION="#Visitor#" ITEM="Key">
  <LI><B>#Key#</B>: #Visitor[Key]#
</CFLOOP>
</UL>
</CFOUTPUT>
