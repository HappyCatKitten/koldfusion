<cfsetting enablecfoutputonly="yes">
<cfset s = StructNew()><cfset s.n = 42><cfset s.l = ListToArray("a,b")><cfset s.q = QueryNew("c")><cfset QueryAddRow(s.q)><cfset QuerySetCell(s.q, "c", "v")>
<cfwddx action="cfml2wddx" input="#s#" output="p"><cfwddx action="wddx2cfml" input="#p#" output="r">
<cfoutput>#r.n#|#r.l[2]#|#r.q.c#|#IsWDDX(p)#|#Len(p)#
</cfoutput>
