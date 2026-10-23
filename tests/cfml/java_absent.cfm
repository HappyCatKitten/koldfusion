<!--- requires: nojava --->
<!--- without a Java Virtual Machine every Java feature fails politely (CFCATCH TYPE="Object") --->
<cftry><cfset v = CreateObject("Java", "java.util.Vector")><cfcatch type="Object"><cfoutput>CreateObject: #cfcatch.message#</cfoutput></cfcatch></cftry>
<cftry><cfobject type="Java" action="Create" class="java.util.Vector" name="v"><cfcatch type="Object"><cfoutput>CFOBJECT: #cfcatch.message#</cfoutput></cfcatch></cftry>
<cftry><CFX_JAVAHELLO NAME="x"><cfcatch type="Any"><cfoutput>CFX: #cfcatch.type# #cfcatch.message#</cfoutput></cfcatch></cftry>
<cftry><CFSERVLET CODE="HelloServlet"></CFSERVLET><cfcatch type="Any"><cfoutput>CFSERVLET: #cfcatch.type# #cfcatch.message#</cfoutput></cfcatch></cftry>
<cfoutput>JavaCast still works: #JavaCast("int", 7)#</cfoutput>
