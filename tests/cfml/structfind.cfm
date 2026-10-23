<cfsetting enablecfoutputonly="yes">
<!--- StructFindKey / StructFindValue / StructSort (4.5.1 SP2) --->
<cfset s = StructNew()>
<cfset s.b = StructNew()><cfset s.b.name = "Bob"><cfset s.b.age = 30>
<cfset s.a = StructNew()><cfset s.a.name = "Ann"><cfset s.a.age = 9>
<cfset s.c = StructNew()><cfset s.c.name = "cy"><cfset s.c.age = 100>
<cfset s.list = ArrayNew(1)><cfset s.list[1] = "x"><cfset s.list[2] = StructNew()><cfset s.list[2].name = "Deep">
<cfset r = StructFindKey(s, "NAME", "all")>
<cfoutput>#ArrayLen(r)#<cfloop from="1" to="#ArrayLen(r)#" index="i"> #r[i].Path#=#r[i].Value#</cfloop>
</cfoutput>
<cfset r = StructFindKey(s, "name")>
<cfoutput>#ArrayLen(r)# #r[1].Path# #r[1].Owner.age#
</cfoutput>
<cfset r = StructFindKey(s, "nope", "all")><cfoutput>#ArrayLen(r)#
</cfoutput>
<cfset r = StructFindValue(s, "DEEP", "all")>
<cfoutput>#ArrayLen(r)# #r[1].Key# #r[1].Path# #StructKeyList(r[1].Owner)#
</cfoutput>
<cfset r = StructFindValue(s, "30")><cfoutput>#r[1].Key# #r[1].Path#
</cfoutput>
<cfset t = StructCopy(s)><cfset StructDelete(t, "list")>
<cfoutput>#ArrayToList(StructSort(t, "numeric", "desc", "age"))#|#ArrayToList(StructSort(t, "numeric", "asc", "age"))#|#ArrayToList(StructSort(t, "text", "asc", "name"))#|#ArrayToList(StructSort(t, "textnocase", "desc", "name"))#
</cfoutput>
<cfset u = StructNew()><cfset u.x = 10><cfset u.y = 2><cfset u.z = 33>
<cfoutput>#ArrayToList(StructSort(u, "numeric"))#|#ArrayToList(StructSort(u))#
</cfoutput>
<cftry><cfset StructSort(u, "bogus")><cfcatch><cfoutput>err1
</cfoutput></cfcatch></cftry>
<cftry><cfset StructSort(t, "numeric", "asc")><cfcatch><cfoutput>err2 #cfcatch.detail#
</cfoutput></cfcatch></cftry>
<cftry><cfset StructFindKey(s, "a", "some")><cfcatch><cfoutput>err3
</cfoutput></cfcatch></cftry>
