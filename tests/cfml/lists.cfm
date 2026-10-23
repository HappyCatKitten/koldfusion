<cfsetting enablecfoutputonly="yes">
<cfset l = "apple,banana,,cherry">
<cfoutput>#ListLen(l)#|#ListGetAt(l, 3)#|#ListFind(l, "banana")#|#ListAppend(l, "date")#|#ListPrepend("b", "a")#|#ListSort("10,9,100", "numeric")#|#ListSort("b,A,c", "textnocase", "desc")#|#ListDeleteAt("a,b,c", 1)#|#ListToArray("x;y", ";")[2]#|#ArrayToList(ListToArray("1,2,3"), "-")#|#ListQualify("1,b", """", ",", "CHAR")#
</cfoutput>
