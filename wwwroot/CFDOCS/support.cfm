<!--- /CFDOCS/support.cfm - Gibson Technical Support: a tiny Knowledge Base and a support request form
      (requests are stored in the Comments table of cfsnippets with CommtType "Support"). --->
<cfset pageTitle = "Technical Support">
<cfset section = "support.cfm">
<cfparam name="URL.kb" default="">
<cfparam name="URL.article" default="0">
<cfparam name="Form.FromUser" default="">
<cfparam name="Form.Email" default="">
<cfparam name="Form.Subject" default="">
<cfparam name="Form.MessText" default="">

<!--- The Knowledge Base: id | title | answer --->
<cfset KB = ArrayNew(1)>
<cfset ArrayAppend(KB, "Too few parameters. Expected 1.|Usually a misspelled column name, or a text value without single quotes around it. Compare your SQL with the table definition (Administrator > ODBC > the data source's table list) and quote string values: WHERE LastName = '##Form.LastName##'. Better yet, use CFQUERYPARAM.")>
<cfset ArrayAppend(KB, "Data source could not be found|The DATASOURCE attribute must name a data source registered in the Administrator. Names are not case-sensitive, but spelling counts. Use Verify Data Source to test the connection.")>
<cfset ArrayAppend(KB, "Error resolving parameter|You referenced a variable that does not exist. Check the spelling, the scope (Form., URL., Session.), and that the query used by CFOUTPUT has a QUERY attribute. Use CFPARAM to give optional variables a default.")>
<cfset ArrayAppend(KB, "Pound signs (##) appear in my output|Inside CFOUTPUT every ## starts an expression. Write ####FFFFFF for a literal color value, or keep static HTML outside CFOUTPUT.")>
<cfset ArrayAppend(KB, "Session variables are lost|Make sure CFAPPLICATION has SESSIONMANAGEMENT=""Yes"" and the browser accepts cookies (CFID and CFTOKEN). Sessions expire after the timeout set on the Administrator's Variables page (20 minutes by default).")>
<cfset ArrayAppend(KB, "Is KoldFusion Year 2000 compliant?|Yes. See the Year 2000 section of the Release Notes. Check your own templates for two-digit year masks (yy) and for string arithmetic on dates.")>
<cfset ArrayAppend(KB, "I forgot the Administrator password|Stop the server and start it with --reset-admin-password, or set UseAdminPassword to 0 in kfroot/registry/kf.registry. Then choose a new password on the Basic Security page.")>
<cfset ArrayAppend(KB, "CFMAIL messages never arrive|Mail is first written to the spool directory and delivered in the background. Check the mail server on the Administrator's Mail page, then look in mail.log. Undeliverable messages are moved to the undelivr directory.")>
<cfset ArrayAppend(KB, "The page times out|Requests are stopped after the time set on the Server Settings page. Long reports can raise their own limit with RequestTimeout=seconds in the URL. Or add an index to that table.")>
<cfset ArrayAppend(KB, "My page looks different in Netscape and Internet Explorer|Welcome to the Web. Close every TABLE, TR and TD tag, avoid nested FONT tags, and test in both browsers. Navigator 4 will not show a table with a missing </TABLE> at all.")>

<cfset Variables.ticket = 0>
<cfset Variables.formError = "">
<cfif IsDefined("Form.SendRequest")>
	<cfif NOT Len(Trim(Form.FromUser)) OR NOT Find("@", Form.Email) OR NOT Len(Trim(Form.MessText))>
		<cfset Variables.formError = "Please fill in your name, a valid e-mail address and a description of the problem.">
	<cfelse>
		<cfquery name="AddRequest" datasource="cfsnippets">
		INSERT INTO Comments (Email, FromUser, Subject, CommtType, MessText, Posted, Processed)
		VALUES (<cfqueryparam value="#Left(Trim(Form.Email), 60)#" cfsqltype="CF_SQL_VARCHAR">,
		        <cfqueryparam value="#Left(Trim(Form.FromUser), 50)#" cfsqltype="CF_SQL_VARCHAR">,
		        <cfqueryparam value="#Left(Trim(Form.Subject), 100)#" cfsqltype="CF_SQL_VARCHAR">,
		        'Support',
		        <cfqueryparam value="#Left(Form.MessText, 2000)#" cfsqltype="CF_SQL_LONGVARCHAR">,
		        <cfqueryparam value="#Now()#" cfsqltype="CF_SQL_TIMESTAMP">, 0)
		</cfquery>
		<cfquery name="NewTicket" datasource="cfsnippets">SELECT @@IDENTITY AS ID</cfquery>
		<cfset Variables.ticket = NewTicket.ID>
	</cfif>
</cfif>

<cfinclude template="_siteheader.cfm">
<FONT FACE="Arial, Helvetica" SIZE=2>
<cfif Variables.ticket>
	<TABLE BORDER=0 CELLPADDING=8 CELLSPACING=0 BGCOLOR="#FFFFCC" WIDTH="100%"><TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>
	<IMG SRC="/CFIDE/administrator/images/check.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
	<cfoutput><B>Thank you, #HTMLEditFormat(Form.FromUser)#.</B> Your request has been logged as case
	<B>KF-#NumberFormat(Variables.ticket, "00000")#</B>. A support engineer will reply to #HTMLEditFormat(Form.Email)#
	within two business days, or one business day if you mention the word &quot;mousepad&quot;.</cfoutput>
	</FONT></TD></TR></TABLE>
</cfif>

<P>Before you call, try the KoldFusion Knowledge Base: most questions have been asked before, many of them
by us.</P>

<!--- ======================================================== Knowledge Base --->
<H3>Search the Knowledge Base</H3>
<FORM ACTION="support.cfm" METHOD="GET">
<INPUT TYPE="text" NAME="kb" SIZE=30 VALUE="<cfoutput>#HTMLEditFormat(URL.kb)#</cfoutput>">
<INPUT TYPE="submit" VALUE="Search">
<FONT SIZE=1>Try: <A HREF="support.cfm?kb=session">session</A>, <A HREF="support.cfm?kb=password">password</A>,
<A HREF="support.cfm?kb=Y2K">Y2K</A>, <A HREF="support.cfm?kb=">everything</A></FONT>
</FORM>
<cfoutput>
<cfif Val(URL.article) GE 1 AND Val(URL.article) LE ArrayLen(KB)>
	<cfset Variables.a = KB[Val(URL.article)]>
	<TABLE BORDER=0 CELLPADDING=1 CELLSPACING=0 BGCOLOR="##003399" WIDTH="100%"><TR><TD>
	<TABLE BORDER=0 CELLPADDING=8 CELLSPACING=0 BGCOLOR="##FFFFFF" WIDTH="100%"><TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>
	<FONT SIZE=1 COLOR="##666666">Article KB-#NumberFormat(1000 + Val(URL.article), "00000")#</FONT><BR>
	<B>#HTMLEditFormat(ListFirst(Variables.a, "|"))#</B>
	<P>#HTMLEditFormat(ListRest(Variables.a, "|"))#</P>
	</FONT></TD></TR></TABLE></TD></TR></TABLE>
</cfif>
<cfset Variables.hits = 0>
<UL>
<cfloop index="i" from="1" to="#ArrayLen(KB)#">
	<cfif NOT Len(Trim(URL.kb)) OR FindNoCase(Trim(URL.kb), KB[i])>
		<cfset Variables.hits = Variables.hits + 1>
		<LI><A HREF="support.cfm?kb=#URLEncodedFormat(URL.kb)#&article=#i#">#HTMLEditFormat(ListFirst(KB[i], "|"))#</A>
		<FONT SIZE=1 COLOR="##666666">KB-#NumberFormat(1000 + i, "00000")#</FONT>
	</cfif>
</cfloop>
</UL>
<cfif NOT Variables.hits><P>No articles match <B>#HTMLEditFormat(URL.kb)#</B>. Our Knowledge Base is small but proud.</P></cfif>
</cfoutput>

<!--- ======================================================== Support options --->
<H3>Support options</H3>
<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=1 BGCOLOR="#999999" WIDTH="100%">
<TR BGCOLOR="#669966"><TH ALIGN=LEFT><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF">Program</FONT></TH><TH ALIGN=LEFT><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF">What you get</FONT></TH><TH ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF">Price</FONT></TH></TR>
<TR BGCOLOR="#FFFFFF" VALIGN=TOP><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Installation Support</B></FONT></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>30 days of help getting the server installed, for <A HREF="registration.cfm">registered</A> users.</FONT></TD><TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2>Free</FONT></TD></TR>
<TR BGCOLOR="#FFFBF0" VALIGN=TOP><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Per-Incident</B></FONT></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>One problem, solved by phone or e-mail. We define &quot;one problem&quot; generously.</FONT></TD><TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2>$195</FONT></TD></TR>
<TR BGCOLOR="#FFFFFF" VALIGN=TOP><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Gold Support</B></FONT></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>Unlimited incidents for a year, two named contacts, priority phone queue with slightly better hold music.</FONT></TD><TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2>$2,495/yr</FONT></TD></TR>
<TR BGCOLOR="#FFFBF0" VALIGN=TOP><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Y2K Rapid Response</B></FONT></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>An engineer on call from December 31, 1999 18:00 to January 1, 2000 06:00. Champagne not included.</FONT></TD><TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2>$1,999</FONT></TD></TR>
</TABLE>
<P><FONT SIZE=1>Phone support: 1-888-KOLDFUS, Monday to Friday, 8 a.m. to 8 p.m. Central Time.
Fax-back service: 1-218-555-0199 (press 1 for the document index).</FONT></P>

<!--- ======================================================== Request form --->
<H3>Submit a support request</H3>
<cfif Len(Variables.formError)><P><FONT COLOR="#CC0000"><B><cfoutput>#Variables.formError#</cfoutput></B></FONT></P></cfif>
<cfoutput>
<FORM ACTION="support.cfm" METHOD="POST">
<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Your name</B></FONT></TD><TD><INPUT TYPE="text" NAME="FromUser" SIZE=40 MAXLENGTH=50 VALUE="#HTMLEditFormat(Form.FromUser)#"></TD></TR>
<TR><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>E-mail</B></FONT></TD><TD><INPUT TYPE="text" NAME="Email" SIZE=40 MAXLENGTH=60 VALUE="#HTMLEditFormat(Form.Email)#"></TD></TR>
<TR><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Subject</B></FONT></TD><TD><INPUT TYPE="text" NAME="Subject" SIZE=40 MAXLENGTH=100 VALUE="#HTMLEditFormat(Form.Subject)#"></TD></TR>
<TR VALIGN=TOP><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Problem</B></FONT></TD><TD><TEXTAREA NAME="MessText" ROWS=5 COLS=50 WRAP="virtual">#HTMLEditFormat(Form.MessText)#</TEXTAREA><BR>
	<FONT SIZE=1>Please include the exact error message, your operating system, and what you were doing when it happened.</FONT></TD></TR>
<TR><TD></TD><TD><INPUT TYPE="submit" NAME="SendRequest" VALUE="Send Request"></TD></TR>
</TABLE>
</FORM>
</cfoutput>
</FONT>
<cfinclude template="_sitefooter.cfm">
