<!--- /CFDOCS/newfeatures.cfm - New Features in KoldFusion 4.5 (with a few live demonstrations) --->
<cfset pageTitle = "New Features in KoldFusion 4.5">
<cfset prevURL = "/CFDOCS/releasenotes.cfm">
<cfset nextURL = "/CFDOCS/install.cfm">
<cfinclude template="_docheader.cfm">

<H1>New Features in KoldFusion 4.5</H1>
<P>KoldFusion 4.5 is all about <B>safer, faster and more connected</B> applications. Here is the short tour.
The grey boxes below are not screenshots: this page is a CFML template, and the results are computed by your
server as you read. Each name links to its page in the <A HREF="langref/index.htm">CFML Language Reference</A>.</P>

<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%">
<TR VALIGN=TOP><TD WIDTH="50%">
<B>Language</B>
<UL>
<LI><A HREF="#queryparam">CFQUERYPARAM</A>: typed, safe SQL parameters
<LI><A HREF="#rethrow">CFRETHROW</A> and better exception handling
<LI><A HREF="#silent">CFSILENT</A> and CFPROCESSINGDIRECTIVE
<LI><A HREF="#execute">CFEXECUTE</A>: run programs on the server
<LI><A HREF="#mailparam">CFMAILPARAM</A>: attachments and custom headers
<LI><A HREF="#java">Java and objects</A>: CFSERVLET, CreateObject, JavaCast
<LI><A HREF="#functions">Fourteen new functions</A>, including Hash
</UL>
</TD><TD WIDTH="50%">
<B>Server and Administrator</B>
<UL>
<LI><A HREF="#admin">New Caching, Locking, Java and Source Control pages</A>
<LI><A HREF="#locking">Automatic read locking and single-threaded sessions</A>
<LI><A HREF="#metrics">GetMetricData and server statistics</A>
<LI><A HREF="#tools">The CFML Syntax Checker</A>
</UL>
</TD></TR>
</TABLE>

<!--- ============================================================ CFQUERYPARAM --->
<H2><A NAME="queryparam">CFQUERYPARAM</A></H2>
<P><A HREF="langref/cfqueryparam.htm"><CODE>CFQUERYPARAM</CODE></A> checks the type of each value you put into a
<CODE>CFQUERY</CODE> and passes it as a proper parameter. A URL like <CODE>detail.cfm?id=7;DROP TABLE Employees</CODE>
is rejected with an error instead of being handed to your database. Use it for every value that came from a user.</P>
<PRE>&lt;CFQUERY NAME="GetEmployee" DATASOURCE="cfsnippets"&gt;
SELECT FirstName, LastName FROM Employees
WHERE Emp_ID = &lt;CFQUERYPARAM VALUE="#URL.id#" CFSQLTYPE="CF_SQL_INTEGER"&gt;
&lt;/CFQUERY&gt;</PRE>
<cfset Variables.attack = "7;DROP TABLE Employees">
<cftry>
	<cfquery name="Variables.demo" datasource="cfsnippets">
	SELECT FirstName FROM Employees
	WHERE Emp_ID = <cfqueryparam value="#Variables.attack#" cfsqltype="CF_SQL_INTEGER">
	</cfquery>
	<cfset Variables.result = "Query ran (this should not happen!)">
	<cfcatch type="Any"><cfset Variables.result = "Rejected: " & CFCATCH.Message></cfcatch>
</cftry>
<TABLE BORDER=0 CELLPADDING=6 BGCOLOR="#EEEEEE"><TR><TD><FONT SIZE=1><B>Live:</B> passing
<CODE><cfoutput>#HTMLEditFormat(Variables.attack)#</cfoutput></CODE> as CF_SQL_INTEGER &raquo;
<cfoutput>#HTMLEditFormat(Variables.result)#</cfoutput></FONT></TD></TR></TABLE>

<!--- ============================================================ CFRETHROW --->
<H2><A NAME="rethrow">CFRETHROW and exception handling</A></H2>
<P>Inside a <CODE>CFCATCH</CODE> block, <A HREF="langref/cfrethrow.htm"><CODE>CFRETHROW</CODE></A> passes the current
exception on to the next enclosing <CODE>CFTRY</CODE> (or to the error page), with its type, message and detail
intact. Handle the errors you understand, rethrow the rest:</P>
<PRE>&lt;CFTRY&gt;
    &lt;CFQUERY ...&gt; ... &lt;/CFQUERY&gt;
    &lt;CFCATCH TYPE="Database"&gt;
        &lt;CFIF CFCATCH.SQLState CONTAINS "S0002"&gt;
            The table is missing - please run the setup page first.
        &lt;CFELSE&gt;
            &lt;CFRETHROW&gt;
        &lt;/CFIF&gt;
    &lt;/CFCATCH&gt;
&lt;/CFTRY&gt;</PRE>
<cftry>
	<cftry>
		<cfthrow type="Inventory.OutOfStock" message="Zip disks are sold out." detail="Try the 1.44MB floppies.">
		<cfcatch type="Database"><cfset Variables.where = "inner handler (wrong type)"></cfcatch>
		<cfcatch type="Any"><cfrethrow></cfcatch>
	</cftry>
	<cfcatch type="Inventory">
		<cfset Variables.where = "outer handler caught " & CFCATCH.Type & ": " & CFCATCH.Message>
	</cfcatch>
</cftry>
<TABLE BORDER=0 CELLPADDING=6 BGCOLOR="#EEEEEE"><TR><TD><FONT SIZE=1><B>Live:</B> a custom exception thrown,
rethrown by the inner CFCATCH, and handled by the <CODE>TYPE="Inventory"</CODE> catch outside &raquo;
<cfoutput>#HTMLEditFormat(Variables.where)#</cfoutput></FONT></TD></TR></TABLE>

<!--- ============================================================ CFSILENT --->
<H2><A NAME="silent">CFSILENT and CFPROCESSINGDIRECTIVE</A></H2>
<P><A HREF="langref/cfsilent.htm"><CODE>CFSILENT</CODE></A> throws away all output generated between its tags. Wrap
your page setup code in it and the browser no longer receives forty blank lines before the
<CODE>&lt;HTML&gt;</CODE> tag. <A HREF="langref/cfprocessingdirective.htm"><CODE>CFPROCESSINGDIRECTIVE
SUPPRESSWHITESPACE="Yes"</CODE></A> squeezes the whitespace out of a block of the page instead.</P>
<cfset Variables.chatter = 0>
<cfsilent>
	<cfloop index="i" from="1" to="40">
		This text and these forty lines of whitespace never reach the browser.
		<cfset Variables.chatter = Variables.chatter + 1>
	</cfloop>
</cfsilent>
<TABLE BORDER=0 CELLPADDING=6 BGCOLOR="#EEEEEE"><TR><TD><FONT SIZE=1><B>Live:</B> a CFSILENT block just ran
<cfoutput>#Variables.chatter#</cfoutput> loop iterations. View the source of this page: you will not find their output.</FONT></TD></TR></TABLE>

<!--- ============================================================ CFEXECUTE --->
<H2><A NAME="execute">CFEXECUTE</A></H2>
<P><A HREF="langref/cfexecute.htm"><CODE>CFEXECUTE</CODE></A> runs a program on the server and captures what it prints,
either into the page or into a file. Give it a <CODE>TIMEOUT</CODE> so a stuck program cannot hold a request hostage,
and remember that the program runs with the server's privileges. Administrators can switch the tag off on the
<A HREF="admin/basicsecurity.htm">Basic Security</A> page.</P>
<PRE>&lt;CFEXECUTE NAME="/bin/date" ARGUMENTS="-u" TIMEOUT="5"&gt;&lt;/CFEXECUTE&gt;</PRE>

<!--- ============================================================ CFMAILPARAM --->
<H2><A NAME="mailparam">CFMAILPARAM</A></H2>
<P>Nested inside <CODE>CFMAIL</CODE>, <A HREF="langref/cfmailparam.htm"><CODE>CFMAILPARAM</CODE></A> attaches files
and adds custom mail headers such as <CODE>Reply-To</CODE> or <CODE>X-Mailer</CODE>.</P>
<PRE>&lt;CFMAIL TO="webmaster@localhost" FROM="orders@localhost" SUBJECT="Your invoice"&gt;
    &lt;CFMAILPARAM NAME="Reply-To" VALUE="billing@localhost"&gt;
    &lt;CFMAILPARAM FILE="#GetTempDirectory()#invoice.txt"&gt;
Thank you for your order!
&lt;/CFMAIL&gt;</PRE>

<!--- ============================================================ Java --->
<H2><A NAME="java">Java and objects</A></H2>
<P>4.5 introduces <A HREF="langref/cfservlet.htm"><CODE>CFSERVLET</CODE></A> for calling Java servlets,
<A HREF="langref/createobject.htm"><CODE>CreateObject</CODE></A> as a function-style alternative to
<CODE>CFOBJECT</CODE>, <A HREF="langref/javacast.htm"><CODE>JavaCast</CODE></A> for passing typed values to Java methods,
Java CFX tags, and a <A HREF="admin/java.htm">Java</A> page in the Administrator. On the UNIX edition the
Java Virtual Machine is not loaded; see the <A HREF="releasenotes.cfm#known">Release Notes</A>.</P>

<!--- ============================================================ functions --->
<H2><A NAME="functions">New functions</A></H2>
<cfset Variables.word = "KoldFusion & <Friends>">
<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=1 BGCOLOR="#999999" WIDTH="100%">
<TR BGCOLOR="#669966"><TH ALIGN=LEFT><FONT COLOR="#FFFFFF">Function</FONT></TH><TH ALIGN=LEFT><FONT COLOR="#FFFFFF">What it does</FONT></TH><TH ALIGN=LEFT><FONT COLOR="#FFFFFF">Live result</FONT></TH></TR>
<cfoutput>
<TR BGCOLOR="##FFFFFF" VALIGN=TOP><TD><A HREF="langref/hash.htm">Hash</A></TD><TD>One-way MD5 hash, 32 hex digits. Store password hashes, not passwords.</TD>
	<TD><CODE>Hash("KoldFusion")</CODE><BR>#Hash("KoldFusion")#</TD></TR>
<TR BGCOLOR="##FFFBF0" VALIGN=TOP><TD><A HREF="langref/xmlformat.htm">XMLFormat</A></TD><TD>Escapes text for XML documents.</TD>
	<TD>#HTMLEditFormat(XMLFormat(Variables.word))#</TD></TR>
<TR BGCOLOR="##FFFFFF" VALIGN=TOP><TD><A HREF="langref/jsstringformat.htm">JSStringFormat</A></TD><TD>Escapes text for a JavaScript string literal.</TD>
	<TD>#HTMLEditFormat(JSStringFormat("It's ""quoted"""))#</TD></TR>
<TR BGCOLOR="##FFFBF0" VALIGN=TOP><TD><A HREF="langref/tobase64.htm">ToBase64</A>, <A HREF="langref/tobinary.htm">ToBinary</A>, <A HREF="langref/tostring.htm">ToString</A>, <A HREF="langref/isbinary.htm">IsBinary</A></TD>
	<TD>Convert between strings, binary objects and Base64 text.</TD>
	<TD><CODE>ToBase64("Y2K")</CODE> = #ToBase64("Y2K")#<BR>and back: #ToString(ToBinary(ToBase64("Y2K")))#</TD></TR>
<TR BGCOLOR="##FFFFFF" VALIGN=TOP><TD><A HREF="langref/urldecode.htm">URLDecode</A></TD><TD>The inverse of URLEncodedFormat.</TD>
	<TD>#HTMLEditFormat(URLDecode("Frostbite%20Falls%2C%20MN"))#</TD></TR>
<TR BGCOLOR="##FFFBF0" VALIGN=TOP><TD><A HREF="langref/gethttptimestring.htm">GetHTTPTimeString</A></TD><TD>A date in the format HTTP headers expect (GMT).</TD>
	<TD>#GetHTTPTimeString(CreateDateTime(2000, 1, 1, 12, 0, 0))#</TD></TR>
<TR BGCOLOR="##FFFFFF" VALIGN=TOP><TD><A HREF="langref/duplicate.htm">Duplicate</A></TD><TD>A deep copy of a structure, array or query.</TD>
	<TD>No more surprises from <CODE>StructCopy</CODE> and nested structures.</TD></TR>
<TR BGCOLOR="##FFFBF0" VALIGN=TOP><TD><A HREF="langref/getfunctionlist.htm">GetFunctionList</A></TD><TD>A structure whose keys are all the functions the server knows.</TD>
	<TD>This server knows #StructCount(GetFunctionList())# functions.</TD></TR>
<TR BGCOLOR="##FFFFFF" VALIGN=TOP><TD><A HREF="langref/getmetricdata.htm">GetMetricData</A></TD><TD>Performance counters for monitoring pages.</TD>
	<TD>Pages served since startup: #GetMetricData("perf_monitor").PageHits#</TD></TR>
<TR BGCOLOR="##FFFBF0" VALIGN=TOP><TD><A HREF="langref/createobject.htm">CreateObject</A>, <A HREF="langref/javacast.htm">JavaCast</A></TD><TD>Objects and typed Java arguments.</TD>
	<TD>See <A HREF="##java">Java and objects</A>.</TD></TR>
</cfoutput>
</TABLE>

<!--- ============================================================ admin --->
<H2><A NAME="admin">The Administrator</A></H2>
<UL>
<LI><A HREF="admin/caching.htm"><B>Caching</B></A>: template cache size, trusted cache, and the maximum number of cached queries.
<LI><A HREF="admin/locking.htm"><B>Locking</B></A>: per-scope settings for automatic checking and read locking.
<LI><A HREF="admin/java.htm"><B>Java</B></A>: the JVM, class path and heap settings.
<LI><A HREF="admin/sourcecontrol.htm"><B>Source Control</B></A>: integration with your source code control system for KoldFusion Studio users.
<LI><A HREF="admin/versioninfo.htm"><B>Version Info</B></A> now shows server statistics and active sessions.
</UL>

<H2><A NAME="locking">Locking made easier</A></H2>
<P>Shared scopes (Server, Application and Session) need <A HREF="langref/cflock.htm"><CODE>CFLOCK</CODE></A> around every
read and write. New in 4.5, the <CODE>SCOPE</CODE> attribute locks a whole scope without having to invent a lock name,
and the Administrator can check that you did it (<I>Full checking</I>), or lock reads for you (<I>Automatic read locking</I>).
Session variables can also be made <I>single threaded</I>, so two frames of the same user never run at once.</P>

<H2><A NAME="metrics">Server statistics</A></H2>
<P><A HREF="langref/getmetricdata.htm"><CODE>GetMetricData("perf_monitor")</CODE></A> returns the counters the Windows
NT Performance Monitor shows: page hits, queued and running requests, timeouts and average times. Feed them to your
own status page, or to a pager when <CODE>ReqQueued</CODE> gets scary.</P>

<H2><A NAME="tools">The CFML Syntax Checker</A></H2>
<P>Before you upgrade a production server, run the <A HREF="cfmlsyntaxcheck/cfmlsyntaxcheck.cfm">CFML Syntax Checker</A>
over your templates. It parses each file with the 4.5 parser and lists anything it cannot understand, with the line and
column, without running a single line of your code.</P>

<cfinclude template="_docfooter.cfm">
