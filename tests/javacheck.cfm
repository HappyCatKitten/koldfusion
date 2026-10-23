<!--- used by tests/run_tests.sh: prints JAVA=YES when a JVM and cfx.jar are available --->
<cftry><cfset b = CreateObject("Java", "com.gibson.kf.Bridge")><cfoutput>JAVA=YES</cfoutput><cfcatch type="Any"><cfoutput>JAVA=NO</cfoutput></cfcatch></cftry>
