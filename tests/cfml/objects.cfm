<!--- COM/CORBA objects, JavaCast() and CFSERVLETPARAM outside CFSERVLET: the same with or without a JVM --->
<cfoutput>
JavaCast: #JavaCast("int", 42.7)# #JavaCast("long", "-12")# #JavaCast("double", "3.14")# #JavaCast("float", 0.5)# #JavaCast("String", 1999)# #JavaCast("bool", 0)# [#JavaCast("null", "x")#]
<cftry>#JavaCast("blob", 1)#<cfcatch type="Expression">#cfcatch.message#</cfcatch></cftry>
<cftry><cfset x = CreateObject("COM", "Word.Application")><cfcatch type="Object">#cfcatch.message#</cfcatch></cftry>
<cftry><cfobject type="COM" action="Create" class="Excel.Application" name="xl"><cfcatch type="Object">#cfcatch.message#</cfcatch></cftry>
<cftry><cfset x = CreateObject("CORBA", "c:\myobject.ior", "IOR")><cfcatch type="Object">#cfcatch.message#</cfcatch></cftry>
<cftry><cfobject type="CORBA" context="NameService" class="Allaire.Department.Doc.empobject" name="emp"><cfcatch type="Object">#cfcatch.message#</cfcatch></cftry>
<cftry><cfset x = CreateObject("ActiveX", "x")><cfcatch type="Expression">#cfcatch.message#</cfcatch></cftry>
<cftry><cfobject type="Java" action="Destroy" class="java.util.Vector" name="v"><cfcatch type="Application">#cfcatch.message#</cfcatch></cftry>
</cfoutput>
<cftry><cfservletparam name="a" value="b"><cfcatch type="Template"><cfoutput>#cfcatch.message#</cfoutput></cfcatch></cftry>
<cfset s = "abc"><cftry><cfset s.foo()><cfcatch type="Object"><cfoutput>#cfcatch.message#</cfoutput></cfcatch></cftry>
