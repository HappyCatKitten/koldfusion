<cfsetting enablecfoutputonly="yes">
<cfset s = StructNew()><cfset s.b = 2><cfset s["a"] = 1><cfset s.nested = StructNew()><cfset s.nested.deep = "yes">
<cfset t = s><cfset t.c = 3><cfset d = Duplicate(s)><cfset d.nested.deep = "no">
<cfoutput>#StructCount(s)#|#s.nested.deep#|#StructKeyExists(s, "C")#|#ListSort(StructKeyList(s), "text")#|#IsStruct(s)#
</cfoutput>
<cfset a = ArrayNew(1)><cfset a[3] = "three"><cfset b = a><cfset b[1] = "one">
<cfoutput>#ArrayLen(a)#|#IsDefined("a")#|#ArrayLen(b)#|#b[1]#|#ArraySum(ListToArray("1,2,3.5"))#
</cfoutput>
<cfset m = ArrayNew(2)><cfset m[2][2] = "x"><cfoutput>#ArrayLen(m)#|#ArrayLen(m[2])#|#m[2][2]#
</cfoutput>
