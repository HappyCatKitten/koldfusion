<CFSET Funcs = GetFunctionList()>
<CFSET Names = ListSort(StructKeyList(Funcs), "textnocase")>
<CFOUTPUT>
<P>This server knows <B>#StructCount(Funcs)#</B> functions.
<P>Has Hash()? #StructKeyExists(Funcs, "Hash")# &nbsp; Has CFDump()? #StructKeyExists(Funcs, "CFDump")#
<P>The ones whose names start with "Get":
</CFOUTPUT>
<UL>
<CFLOOP LIST="#Names#" INDEX="f">
  <CFIF Left(f, 3) IS "Get"><CFOUTPUT><LI>#f#</CFOUTPUT></CFIF>
</CFLOOP>
</UL>
