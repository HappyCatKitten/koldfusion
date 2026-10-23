<!--- requires: java --->
<!--- CFOBJECT TYPE="Java" / CreateObject("Java"): methods, overloads, JavaCast, fields, statics, conversions, exceptions --->
<cfoutput>
<cfset h = CreateObject("Java", "java.util.Hashtable")>
<cfset h.put("name", "Ben")><cfset h.put("age", 42)>
1. hashtable size=#h.size()# name=#h.get("name")# hasAge=#h.containsKey("age")# missing=[#h.get("nope")#]
<cfobject type="Java" action="Create" class="java.lang.StringBuffer" name="sb">
<cfset sb.init("Hello")><cfset sb.append(", ").append("World")>
2. stringbuffer [#sb.toString()#] length=#sb.length()# reverse=#sb.reverse().toString()#
<cfset m = CreateObject("Java", "java.lang.Math")>
3. math max=#m.max(3, 7)# max2=#m.max(2.5, 1)# abs=#m.abs(JavaCast("int", -5))# pow=#m.pow(2, 10)# PI=#m.PI#
<cfset v = CreateObject("Java", "java.util.Vector")>
<cfset v.addElement("a")><cfset v.addElement("b")><cfset v.addElement("c")>
<cfset sub = v.subList(0, 2)>
4. vector size=#v.size()# elementAt=#v.elementAt(1)# subList isArray=#IsArray(sub)# len=#ArrayLen(sub)# list=#ArrayToList(sub)#
<cfset ht = CreateObject("Java", "java.util.Hashtable")><cfset inner = CreateObject("Java", "java.util.Hashtable")>
<cfset inner.put("x", "1")><cfset ht.put("inner", inner)>
<cfset copy = CreateObject("Java", "java.util.Hashtable").init(ht)>
<cfset st = copy.clone()>
5. hashtable clone isStruct=#IsStruct(st)# inner.x=#st.inner.x#
<cfset s = CreateObject("Java", "java.lang.String").init("héllo wörld")>
6. string upper=#s.toUpperCase()# length=#s.length()# indexOf=#s.indexOf("w")# char=#Chr(s.charAt(0))# split=#ArrayToList(s.split(" "), "|")#
<cfset e = CreateObject("Java", "Employee")>
7. static company=#e.company()# headCount=#e.headCount#
<cfset e.init("Ben", "Forta")>
8. init name=#e.getFullName()# first=#e.firstName# headCount=#e.headCount#
<cfset e.salary = 50000><cfset e.lastName = "Forta-Smith">
9. fields salary=#e.salary# raise=#e.raise(10)# name=#e.getFullName()#
10. overloads #e.setJobGrade(JavaCast("int", 3))# / #e.setJobGrade(JavaCast("String", "b"))# / #e.setJobGrade("c")#
<cfset g = JavaCast("int", 4)>
11. javacast variable #e.setJobGrade(g)# grade=#e.getJobGrade()# display=#g# #JavaCast("double", 3.5)# #JavaCast("bool", 1)# #JavaCast("long", "12")#
<cfset e.addSkill("CFML")><cfset e.addSkill("Java")>
12. vector return #ArrayToList(e.getSkills())# array return #ArrayToList(e.getNameParts(), " ")#
<cftry><cfset e.raise(99)>
<cfcatch type="Object">13. exception type=#cfcatch.type# message=#cfcatch.message#
<cfset ex = GetException(e)>    GetException code=#ex.getErrorCode()# message=#ex.getErrorMessage()#</cfcatch></cftry>
<cfset e.getFullName()>
14. after a good call GetException is empty: [#GetException(e)#]
<cfset e2 = CreateObject("Java", "Employee").init()><cfset e2.firstName = "Copy">
<cfset e3 = Duplicate(e2)>
15. duplicate shares the Java object: #e3.getFullName()# simple=#IsSimpleValue(e3)# struct=#IsStruct(e3)# array=#IsArray(e3)#
<cfset c = CreateObject("Java", "java.util.Calendar")>
16. static field via class Calendar.YEAR=#c.YEAR#
<cfset str = CreateObject("Java", "java.lang.String")>
17. varargs #str.format("%05d|%s", JavaCast("int", 42), "x")# valueOf=#str.valueOf(JavaCast("boolean", "yes"))#
<cfset arr = CreateObject("Java", "java.util.Arrays")>
18. CF array in, List out: #ArrayToList(arr.asList(ListToArray("c,b,a")))#
<cfset d = CreateObject("Java", "java.util.Date").init(JavaCast("long", 0))>
19. date getTime=#d.getTime()#
<cfset bool = CreateObject("Java", "java.lang.Boolean")>
20. boolean #bool.parseBoolean("true")# #bool.parseBoolean("nope")#
<cfscript>
map = CreateObject("Java", "java.util.TreeMap");
map.put("zebra", 1); map.put("apple", 2);
keys = map.keySet();
first = map.firstKey();
</cfscript>
21. cfscript first=#first# keys=#ArrayToList(keys.toArray())#
<cftry><cfset x = e.noSuchMethod()><cfcatch type="Object">22. #cfcatch.message#</cfcatch></cftry>
<cftry><cfset x = e.raise("a", "b")><cfcatch type="Object">23. #cfcatch.message#</cfcatch></cftry>
<cftry><cfset x = CreateObject("Java", "com.example.NoSuchClass")><cfcatch type="Object">24. #cfcatch.message#</cfcatch></cftry>
<cftry><cfset x = e.noSuchField><cfcatch type="Object">25. #cfcatch.message#</cfcatch></cftry>
<cftry><cfset r = CreateObject("Java", "java.lang.Runnable")><cfset r.run()><cfcatch type="Object">26. #cfcatch.message#</cfcatch></cftry>
<cftry><cfset i = CreateObject("Java", "java.lang.Integer").parseInt("abc")><cfcatch type="Object">27. #cfcatch.message#</cfcatch></cftry>
<cftry><cfset e.init()><cfcatch type="Object">28. #cfcatch.message#</cfcatch></cftry>
<cftry>#e#<cfcatch type="Expression">29. #cfcatch.message#</cfcatch></cftry>
30. IsDefined field=#IsDefined("e.firstName")# missing=#IsDefined("e.nothing")#
<cfset sbs = ArrayNew(1)><cfloop index="i" from="1" to="3"><cfset sbs[i] = CreateObject("Java", "java.lang.StringBuilder").init("n#i#")></cfloop>
31. array of objects #sbs[1].toString()##sbs[2].toString()##sbs[3].toString()#
<cfset hs = StructNew()><cfset hs.a = 1><cfset hs.b = "two">
<cfset fromStruct = CreateObject("Java", "java.util.Hashtable").init(hs)>
32. struct -> Hashtable size=#fromStruct.size()# b=#fromStruct.get("b")#
</cfoutput>
