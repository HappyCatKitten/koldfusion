<!--- Java (new in 4.5) --->
<cfset fields = "JVMPath:Java Virtual Machine Path:The full path to the JVM library KoldFusion loads for Java CFX tags and CFOBJECT TYPE=Java.~ClassPath:Class Path:Additional directories and JAR files to search for classes.~InitialHeap:Initial Heap Size:Initial heap size in kilobytes.~MaxHeap:Max Heap Size:Maximum heap size in kilobytes.~SystemOptions:System Options:JVM system options in the form OPT1=option1;OPT2=option2.~ImplementationOptions:Implementation Options:Implementation-specific JVM options in the same form.~CFXJarPath:CFX Jar Path:The location of cfx.jar, which Java CFX tags compile against.">
<cfset msg = "">
<cfif IsDefined("Form.Apply")>
	<cfloop list="#fields#" index="row" delimiters="~">
		<cfset f = ListFirst(row, ":")>
		<cfmodule template="../_tags/setreg.cfm" key="Java" entry="#f#" value="#Trim(Form[f])#">
	</cfloop>
	<cfset msg = "Java settings have been applied. Restart the KoldFusion Application Server for them to take effect.">
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="Java" variable="J">
<cfset pageTitle = "Java">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="java.cfm" METHOD="POST">
<cfloop list="#fields#" index="row" delimiters="~">
	<cfset f = ListGetAt(row, 1, ":")>
	<P>#Request.f#<B>#ListGetAt(row, 2, ":")#</B><BR>
	<INPUT TYPE="text" NAME="#f#" VALUE="#HTMLEditFormat(J[f])#" SIZE=60><BR>#ListGetAt(row, 3, ":")#</FONT>
</cfloop>
<P>#Request.f#<I>Status: no Java Virtual Machine is loaded (KoldFusion 4.5 for UNIX supports Java CFX tags only with a
JDK 1.2 VM installed). Java CFX tags and CFOBJECT TYPE="Java" will report an error.</I></FONT>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Apply" VALUE="Apply"> <INPUT TYPE="reset" VALUE="Cancel">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
