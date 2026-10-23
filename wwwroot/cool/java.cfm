<!--- Java in your CFML! - the embedded Java Virtual Machine, CFX tags written in Java and servlets --->
<cfset pageTitle = "Java in your CFML!">
<cfparam name="Form.name" default="Webmaster">
<cfparam name="Form.n" default="52">
<cfparam name="Form.raise" default="10">
<cfif NOT IsNumeric(Form.n) OR Form.n LT 1 OR Form.n GT 500><cfset Form.n = 52></cfif>
<cfif NOT IsNumeric(Form.raise)><cfset Form.raise = 10></cfif>
<cfinclude template="_top.cfm">
<P><IMG SRC="/images/new.gif" WIDTH=44 HEIGHT=22 ALIGN=ABSMIDDLE> <B>New in KoldFusion 4.5:</B> a real Java Virtual Machine
lives inside the server. Load any Java class with <TT>CreateObject("Java", ...)</TT> or <TT>&lt;CFOBJECT TYPE="Java"&gt;</TT>,
write CFX tags in Java, and run servlets without a separate servlet engine. Write once, run anywhere (that has a JVM).</P>
<cftry>
	<cfset sys = CreateObject("Java", "java.lang.System")>
	<cfset javaOK = true>
	<cfcatch type="Object">
		<cfset javaOK = false>
		<cfset javaWhy = CFCATCH.Message & " " & CFCATCH.Detail>
	</cfcatch>
</cftry>
<cfif NOT javaOK>
	<cfoutput>
	<TABLE BORDER=1 CELLPADDING=8 CELLSPACING=0 BGCOLOR="##FFEECC"><TR><TD><FONT FACE="Arial" SIZE=2>
	<B>No Java on this server, so no coffee for you.</B><BR>#javaWhy#<BR>
	Install a JDK (or point the <A HREF="/CFIDE/administrator/index.cfm?page=server/java.cfm">Java page</A> of the
	Administrator at one), run <TT>make</TT> to build <TT>cfx.jar</TT>, and reload this page.</FONT></TD></TR></TABLE>
	</cfoutput>
	<cfinclude template="_bottom.cfm">
	<cfabort>
</cfif>

<!--- 1. who are we talking to? --->
<H3><IMG SRC="/images/bullet_red.gif" WIDTH=13 HEIGHT=13> 1. Say hello to the JVM</H3>
<cfset rt = CreateObject("Java", "java.lang.Runtime").getRuntime()>
<cfoutput>
<TABLE BORDER=1 CELLPADDING=4 CELLSPACING=0 BGCOLOR="##FFFFEE">
<TR><TD><TT>System.getProperty("java.version")</TT></TD><TD>#sys.getProperty("java.version")#</TD></TR>
<TR><TD><TT>System.getProperty("java.vendor")</TT></TD><TD>#sys.getProperty("java.vendor")#</TD></TR>
<TR><TD><TT>System.getProperty("os.name")</TT></TD><TD>#sys.getProperty("os.name")# #sys.getProperty("os.arch")#</TD></TR>
<TR><TD><TT>Runtime.availableProcessors()</TT></TD><TD>#rt.availableProcessors()#</TD></TR>
<TR><TD><TT>Runtime.totalMemory()</TT></TD><TD>#NumberFormat(rt.totalMemory() / 1024)# KB (#NumberFormat(rt.freeMemory() / 1024)# KB free)</TD></TR>
</TABLE>
<P>In 1999, Java 1.2 needed 32 MB of RAM just to say hello. This one is #sys.getProperty("java.specification.version")#.</P>
</cfoutput>

<!--- 2. java.util from CFML --->
<H3><IMG SRC="/images/bullet_red.gif" WIDTH=13 HEIGHT=13> 2. java.util, straight from CFML: the Dot-Com Business Plan Generator</H3>
<cfset words = CreateObject("Java", "java.util.StringTokenizer")>
<cfset words.init("e-commerce,B2B,portal,push,synergy,eyeballs,clicks-and-mortar,one-to-one,viral,mindshare,first-mover,WAP", ",")>
<cfset buzz = CreateObject("Java", "java.util.Vector")>
<cfloop condition="words.hasMoreTokens()"><cfset buzz.addElement(words.nextToken())></cfloop>
<cfset rnd = CreateObject("Java", "java.util.Random")>
<cfset CreateObject("Java", "java.util.Collections").shuffle(buzz, rnd)>
<cfset plan = buzz.subList(0, 3)>
<cfoutput>
<P>A <TT>StringTokenizer</TT> chopped up the buzzwords, a <TT>Vector</TT> held them and <TT>Collections.shuffle()</TT>
mixed them with a <TT>java.util.Random</TT>. Your plan:</P>
<P ALIGN=CENTER><FONT SIZE=4 COLOR="##CC0000"><B>"We are the #plan[1]# #plan[2]# company for #plan[3]#."</B></FONT><BR>
Valuation: <B>#DollarFormat(rnd.nextInt(900) * 1000000 + 100000000)#</B>. Revenue: <B>$0</B>.
<A HREF="java.cfm">IPO again</A></P>
</cfoutput>

<!--- 3. arbitrary precision --->
<H3><IMG SRC="/images/bullet_red.gif" WIDTH=13 HEIGHT=13> 3. Numbers too big for CFML</H3>
<cfset big = CreateObject("Java", "java.math.BigInteger").init("1")>
<cfloop index="i" from="2" to="#Form.n#"><cfset big = big.multiply(CreateObject("Java", "java.math.BigInteger").valueOf(JavaCast("long", i)))></cfloop>
<cfoutput>
<FORM ACTION="java.cfm" METHOD="POST">
CFML numbers give up after 15 digits; <TT>java.math.BigInteger</TT> never does. Factorial of
<INPUT TYPE="text" NAME="n" VALUE="#HTMLEditFormat(Form.n)#" SIZE=4> <INPUT TYPE="submit" VALUE="Compute">
<INPUT TYPE="hidden" NAME="name" VALUE="#HTMLEditFormat(Form.name)#">
</FORM>
<P>#Form.n#! has #Len(big.toString())# digits:<BR>
<TT>#Wrap(big.toString(), 70)#</TT></P>
<cfif Form.n EQ 52><P>(That is how many ways there are to shuffle a deck of cards. Your Solitaire game will never repeat.)</P></cfif>
</cfoutput>

<!--- 4. a class of our own, with exceptions --->
<H3><IMG SRC="/images/bullet_red.gif" WIDTH=13 HEIGHT=13> 4. Call your own Java class</H3>
<P><TT>Employee.class</TT> (source in <TT>java/samples</TT>) lives in <TT>kfroot/java/classes</TT>. It has public fields,
an overloaded method, a static method and its own exception class.</P>
<cfobject type="Java" action="Create" class="Employee" name="emp">
<cfset emp.init("Ben", "Forta")>
<cfset emp.salary = 52000>
<cfset emp.addSkill("CFML")><cfset emp.addSkill("Java")><cfset emp.addSkill("HomeSite")>
<cfoutput>
<FORM ACTION="java.cfm" METHOD="POST">
<INPUT TYPE="hidden" NAME="n" VALUE="#HTMLEditFormat(Form.n)#"><INPUT TYPE="hidden" NAME="name" VALUE="#HTMLEditFormat(Form.name)#">
Give #emp.getFullName()# of #emp.company()# a raise of <INPUT TYPE="text" NAME="raise" VALUE="#HTMLEditFormat(Form.raise)#" SIZE=4>%
<INPUT TYPE="submit" VALUE="Raise!"> (more than 50% throws an <TT>EmployeeException</TT>)
</FORM>
<cftry>
	<cfset newSalary = emp.raise(Form.raise)>
	<P>New salary: <B>#DollarFormat(newSalary)#</B>. Skills (a <TT>Vector</TT>, now a CFML array):
	<B>#ArrayToList(emp.getSkills(), ", ")#</B>.
	Job grade: #emp.setJobGrade(JavaCast("String", "B"))#, or #emp.setJobGrade(JavaCast("int", 4))#
	(<TT>JavaCast()</TT> picks the overload).</P>
	<cfcatch type="Object">
		<cfset ex = GetException(emp)>
		<P><FONT COLOR="##CC0000"><B>CFCATCH.Message: #CFCATCH.Message#</B></FONT><BR>
		<TT>GetException(emp).getErrorMessage()</TT> says: <I>#ex.getErrorMessage()#</I></P>
	</cfcatch>
</cftry>
</cfoutput>

<!--- 5. a CFX tag written in Java --->
<H3><IMG SRC="/images/bullet_red.gif" WIDTH=13 HEIGHT=13> 5. A CFX tag written in Java</H3>
<cfoutput>
<FORM ACTION="java.cfm" METHOD="POST">
<INPUT TYPE="hidden" NAME="n" VALUE="#HTMLEditFormat(Form.n)#"><INPUT TYPE="hidden" NAME="raise" VALUE="#HTMLEditFormat(Form.raise)#">
<TT>&lt;CFX_JAVAHELLO NAME="<INPUT TYPE="text" NAME="name" VALUE="#HTMLEditFormat(Form.name)#" SIZE=15>"&gt;</TT>
<INPUT TYPE="submit" VALUE="Run it">
</FORM>
</cfoutput>
<cftry>
	<P><CFX_JAVAHELLO NAME="#Form.name#"></P>
	<P>The tag is a 20-line Java class written against the ColdFusion 4.5 API (<TT>com.allaire.cfx.CustomTag</TT>),
	registered on the <A HREF="/CFIDE/administrator/index.cfm?page=extensions/cfx.cfm">CFX Tags</A> page of the Administrator.</P>
	<cfcatch type="Any"><cfoutput><P><I>#CFCATCH.Message#</I></P></cfoutput></cfcatch>
</cftry>

<!--- 6. a servlet --->
<H3><IMG SRC="/images/bullet_red.gif" WIDTH=13 HEIGHT=13> 6. Servlets without a servlet engine</H3>
<cflock scope="session" type="exclusive" timeout="10">
	<cfparam name="Session.servletVisits" default="0">
	<cfset visits = Session.servletVisits>
</cflock>
<cftry>
	<TABLE BORDER=1 CELLPADDING=8 CELLSPACING=0 BGCOLOR="#EEFFEE"><TR><TD>
	<CFSERVLET CODE="HelloServlet" TIMEOUT="10">
		<CFSERVLETPARAM NAME="name" VALUE="#Form.name#">
		<CFSERVLETPARAM NAME="visits" VARIABLE="visits" TYPE="INT">
	</CFSERVLET>
	</TD></TR></TABLE>
	<cflock scope="session" type="exclusive" timeout="10"><cfset Session.servletVisits = visits></cflock>
	<cfoutput>
	<P><TT>CFSERVLET</TT> ran <TT>HelloServlet</TT> (a 1999-style <TT>HttpServlet</TT>) inside KoldFusion's own JVM. It got
	the name as a request parameter, and the visit counter <I>by reference</I> as a request attribute; it incremented the
	counter with <TT>setAttribute()</TT>, and KoldFusion copied it back: it is now <B>#visits#</B>.
	The servlet's response header <TT>X-Servlet</TT> came back as <TT>CFSERVLET["X-Servlet"]</TT> =
	<B>#CFSERVLET["X-Servlet"]#</B>.</P>
	</cfoutput>
	<cfcatch type="Any"><cfoutput></TD></TR></TABLE><P><I>#CFCATCH.Message#</I></P></cfoutput></cfcatch>
</cftry>
<P>Want to see everything a servlet gets? <A HREF="java.cfm?snoop=yes#snoop">Run SnoopServlet</A>.</P>
<cfif IsDefined("URL.snoop")>
	<A NAME="snoop"></A>
	<cftry>
		<CFSERVLET CODE="SnoopServlet"><CFSERVLETPARAM NAME="from" VALUE="Cool Stuff"></CFSERVLET>
		<cfcatch type="Any"><cfoutput><P><I>#CFCATCH.Message#</I></P></cfoutput></cfcatch>
	</cftry>
</cfif>
<cfinclude template="_bottom.cfm">
