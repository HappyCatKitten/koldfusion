<!--- used by tests/run_tests.sh: JAVA=YES (a JVM and cfx.jar), JAVA=NOJAR (a JVM only) or JAVA=NO --->
<cftry><cfset o = CreateObject("Java", "java.lang.Object")><cfset jvm = "YES"><cfcatch type="Any"><cfset jvm = "NO"></cfcatch></cftry>
<cfif jvm EQ "YES"><cftry><cfset b = CreateObject("Java", "com.gibson.kf.Bridge")><cfcatch type="Any"><cfset jvm = "NOJAR"></cfcatch></cftry></cfif>
<cfoutput>JAVA=#jvm#</cfoutput>
