<!--- Java Settings (new in 4.5): the embedded Java Virtual Machine used by CFOBJECT TYPE="Java", CreateObject("Java"),
      Java CFX tags and CFSERVLET --->
<cfset fields = "JVMPath|Java Virtual Machine Path|The Java Virtual Machine library (libjvm.so) or the JDK/JRE directory that contains it. Leave it empty and KoldFusion looks in JAVA_HOME, for java on the PATH, in /usr/lib/jvm and in ~/.local/jdk.^ClassPath|Class Path|Directories and JAR files where Java classes used by KoldFusion are found, separated by semicolons. cfx.jar and the classes directory of the KoldFusion installation are always included.^InitialHeap|Initial Heap Size|The initial size of the Java heap, in kilobytes.^MaxHeap|Max Heap Size|The largest the Java heap may grow, in kilobytes.^SystemOptions|System Options|Standard JVM initialization options as name=value pairs separated by semicolons, for example OPT1=option1;OPT2=option2. Each becomes a Java system property.^ImplementationOptions|Implementation Options|Implementation-specific JVM initialization options, separated by semicolons or spaces, for example -Xss512k;-XX:+UseSerialGC.^CFXJarPath|CFX Jar Path|The location of cfx.jar, which contains the interfaces Java CFX tags are compiled against (com.allaire.cfx and com.gibson.cfx) and the servlet API used by CFSERVLET.">
<cfset msg = "">
<cfif IsDefined("Form.Apply")>
	<cfloop list="#fields#" index="row" delimiters="^">
		<cfset f = ListFirst(row, "|")>
		<cfmodule template="../_tags/setreg.cfm" key="Java" entry="#f#" value="#Trim(Form[f])#">
	</cfloop>
	<cfset J = KFUSION_JAVA("status")>
	<cfif J.Loaded>
		<cfset msg = "The Java settings have been saved. Restart the KoldFusion Application Server for them to take effect: the Java Virtual Machine is already running, and a process can only start it once.">
	<cfelse>
		<cfset msg = "The Java settings have been saved. They are used when the Java Virtual Machine is loaded.">
	</cfif>
</cfif>
<cfif IsDefined("Form.LoadJVM")>
	<cfset J = KFUSION_JAVA("load")>
	<cfif J.Loaded>
		<cfset msg = "The Java Virtual Machine is loaded.">
	<cfelse>
		<cfset msg = "The Java Virtual Machine could not be loaded.">
	</cfif>
</cfif>
<cfset J = KFUSION_JAVA("status")>
<cfmodule template="../_tags/getreg.cfm" key="Java" variable="R">
<cfset pageTitle = "Java Settings">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="java.cfm" METHOD="POST">
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=4 CELLSPACING=0>
<TR BGCOLOR="##669966"><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Java Virtual Machine status</B></FONT></TD></TR>
<TR BGCOLOR="##FFFBF0"><TD>#Request.f#
<cfif J.Loaded>
	<IMG SRC="../images/check.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE ALT="">
	<B>Loaded.</B> Java #HTMLEditFormat(J.Version)#, started #TimeFormat(J.LoadedAt, "h:mm:ss tt")# on #DateFormat(J.LoadedAt, "mmmm d, yyyy")#.<BR>
	Library: <TT>#HTMLEditFormat(J.Path)#</TT> (found via #HTMLEditFormat(J.Source)#)<BR>
	Heap: #NumberFormat(J.HeapUsedKB)# KB used of #NumberFormat(J.HeapTotalKB)# KB (maximum #NumberFormat(J.HeapMaxKB)# KB).
	#J.Threads# thread<cfif J.Threads NEQ 1>s</cfif> attached, #J.Objects# Java object<cfif J.Objects NEQ 1>s</cfif> referenced by CFML variables.<BR>
	Class path: <TT>#HTMLEditFormat(J.ClassPath)#</TT><BR>
	Options: <TT>#HTMLEditFormat(J.Options)#</TT>
<cfelseif J.Failed>
	<IMG SRC="../images/x.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE ALT="">
	<FONT COLOR="##CC0000"><B>Failed.</B> #HTMLEditFormat(J.Error)#</FONT>
<cfelseif J.Found>
	<IMG SRC="../images/warn.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE ALT="">
	<B>Not loaded.</B> KoldFusion will load <TT>#HTMLEditFormat(J.Path)#</TT> (found via #HTMLEditFormat(J.Source)#)
	the first time a page uses Java, or now: <INPUT TYPE="submit" NAME="LoadJVM" VALUE="Load JVM">
<cfelse>
	<IMG SRC="../images/x.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE ALT="">
	<FONT COLOR="##CC0000"><B>No Java Virtual Machine found.</B></FONT> KoldFusion #HTMLEditFormat(J.Source)#.
	Install a JDK or JRE, or enter the path of libjvm.so below. Pages that use Java report an error; everything else works.
	<cfif Len(J.Error)><BR><I>#HTMLEditFormat(J.Error)#</I></cfif>
</cfif>
<BR><cfif J.CFXJarExists><IMG SRC="../images/check.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE ALT=""><cfelse><IMG SRC="../images/warn.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE ALT=""></cfif>
cfx.jar: <TT>#HTMLEditFormat(J.CFXJar)#</TT>
<cfif J.CFXJarExists>(present)<cfelse><B>(missing: run <TT>make</TT> with a JDK installed; Java CFX tags and CFSERVLET need it, CFOBJECT does not)</B></cfif>
</FONT></TD></TR>
</TABLE>
<cfloop list="#fields#" index="row" delimiters="^">
	<cfset f = ListGetAt(row, 1, "|")>
	<cfparam name="R.#f#" default="">
	<P>#Request.f#<B>#ListGetAt(row, 2, "|")#</B><BR>
	<INPUT TYPE="text" NAME="#f#" VALUE="#HTMLEditFormat(R[f])#" SIZE=<cfif f CONTAINS "Heap">10<cfelse>60</cfif><cfif f EQ "JVMPath" OR f EQ "CFXJarPath" OR f EQ "ClassPath"> STYLE="font-family:Courier New,monospace"</cfif>><cfif f EQ "JVMPath" OR f EQ "CFXJarPath"> <INPUT TYPE="button" VALUE="Browse Server..." onClick="browseServer('#f#')"></cfif><BR>
	#ListGetAt(row, 3, "|")#</FONT>
</cfloop>
<P>#Request.f#<I>Java classes, Java CFX tags and servlets can also be dropped into <TT>#HTMLEditFormat(J.ClassesDir)#</TT>;
CFX tags and servlets there are reloaded when their class file changes. Changes to these settings take effect when the
server is restarted.</I></FONT>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Apply" VALUE="Apply"> <INPUT TYPE="reset" VALUE="Cancel">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
