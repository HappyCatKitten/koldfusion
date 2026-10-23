<!--- /CFDOCS/forums.cfm - Gibson Support Forums: a small threaded discussion on the Messages table of cfsnippets --->
<cfset pageTitle = "Support Forums">
<cfset section = "forums.cfm">
<cfparam name="URL.thread" default="0">
<cfparam name="Form.Author" default="">
<cfparam name="Form.Subject" default="">
<cfparam name="Form.Body" default="">
<cfparam name="Form.ParentID" default="0">
<cfset Variables.thread = Val(URL.thread)>
<cfset Variables.postError = "">

<!--- ============================================================ posting --->
<cfif IsDefined("Form.Post")>
	<cfset Form.ParentID = Val(Form.ParentID)>
	<cfif NOT Len(Trim(Form.Author)) OR NOT Len(Trim(Form.Body)) OR (Form.ParentID EQ 0 AND NOT Len(Trim(Form.Subject)))>
		<cfset Variables.postError = "Please enter your name, a subject and a message.">
		<cfset Variables.thread = Form.ParentID>
	<cfelse>
		<cfif Form.ParentID>
			<cfquery name="Parent" datasource="cfsnippets">
			SELECT Subject FROM Messages WHERE MsgID = <cfqueryparam value="#Form.ParentID#" cfsqltype="CF_SQL_INTEGER">
			</cfquery>
			<cfset Form.Subject = "RE: " & ReplaceNoCase(Parent.Subject, "RE: ", "", "ALL")>
		</cfif>
		<cfquery name="AddPost" datasource="cfsnippets">
		INSERT INTO Messages (ParentID, Subject, Author, Body, Posted)
		VALUES (<cfqueryparam value="#Form.ParentID#" cfsqltype="CF_SQL_INTEGER">,
		        <cfqueryparam value="#Left(Trim(Form.Subject), 100)#" cfsqltype="CF_SQL_VARCHAR">,
		        <cfqueryparam value="#Left(Trim(Form.Author), 50)#" cfsqltype="CF_SQL_VARCHAR">,
		        <cfqueryparam value="#Left(Form.Body, 4000)#" cfsqltype="CF_SQL_LONGVARCHAR">,
		        <cfqueryparam value="#Now()#" cfsqltype="CF_SQL_TIMESTAMP">)
		</cfquery>
		<cfif Form.ParentID>
			<cflocation url="forums.cfm?thread=#Form.ParentID#" addtoken="No">
		<cfelse>
			<cfquery name="NewID" datasource="cfsnippets">SELECT @@IDENTITY AS ID</cfquery>
			<cflocation url="forums.cfm?thread=#NewID.ID#" addtoken="No">
		</cfif>
	</cfif>
</cfif>

<cfinclude template="_siteheader.cfm">
<FONT FACE="Arial, Helvetica" SIZE=2>

<cfif Variables.thread>
	<!--- ======================================================== one thread --->
	<cfquery name="ThreadMsgs" datasource="cfsnippets">
	SELECT MsgID, ParentID, Subject, Author, Body, Posted
	FROM Messages
	WHERE MsgID = <cfqueryparam value="#Variables.thread#" cfsqltype="CF_SQL_INTEGER">
	   OR ParentID = <cfqueryparam value="#Variables.thread#" cfsqltype="CF_SQL_INTEGER">
	ORDER BY Posted, MsgID
	</cfquery>
	<P><A HREF="forums.cfm">&laquo; All topics</A> &nbsp;|&nbsp; Forum: <B>KoldFusion Server - General</B></P>
	<cfif NOT ThreadMsgs.RecordCount>
		<P>That topic has vanished. Perhaps it was never there; perhaps it was a Y2K bug.</P>
	</cfif>
	<cfoutput query="ThreadMsgs">
		<TABLE BORDER=0 CELLPADDING=1 CELLSPACING=0 WIDTH="100%" BGCOLOR="##669966"><TR><TD>
		<TABLE BORDER=0 CELLPADDING=5 CELLSPACING=0 WIDTH="100%">
		<TR BGCOLOR="##669966"><TD><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>#HTMLEditFormat(Subject)#</B></FONT></TD>
			<TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=1 COLOR="##FFFFFF">#HTMLEditFormat(Author)# &middot; #DateFormat(Posted, "mmm d, yyyy")# #TimeFormat(Posted, "h:mm tt")#</FONT></TD></TR>
		<TR BGCOLOR="<cfif CurrentRow EQ 1>##FFFFF0<cfelse>##FFFFFF</cfif>"><TD COLSPAN=2><FONT FACE="Arial, Helvetica" SIZE=2>#ParagraphFormat(HTMLEditFormat(Body))#</FONT></TD></TR>
		</TABLE></TD></TR></TABLE><BR>
	</cfoutput>
	<cfset Variables.replyTo = Variables.thread>
<cfelse>
	<!--- ======================================================== topic list --->
	<cfquery name="Topics" datasource="cfsnippets">
	SELECT MsgID, Subject, Author, Posted FROM Messages WHERE ParentID = 0 ORDER BY Posted DESC
	</cfquery>
	<cfquery name="Replies" datasource="cfsnippets">
	SELECT ParentID, COUNT(*) AS N, MAX(Posted) AS LastPost FROM Messages WHERE ParentID <> 0 GROUP BY ParentID
	</cfquery>
	<P>Welcome to the Gibson Support Forums, where KoldFusion developers help each other out. Be nice, search
	before you post, and please do not type your whole message IN CAPITALS. Gibson engineers drop by when the
	coffee machine is broken.</P>
	<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=1 BGCOLOR="#999999" WIDTH="100%">
	<TR BGCOLOR="#669966">
		<TH ALIGN=LEFT><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF">Topic</FONT></TH>
		<TH ALIGN=LEFT><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF">Started by</FONT></TH>
		<TH><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF">Replies</FONT></TH>
		<TH ALIGN=LEFT><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF">Last post</FONT></TH>
	</TR>
	<cfoutput query="Topics">
		<cfset Variables.n = 0>
		<cfset Variables.last = Topics.Posted>
		<cfloop query="Replies">
			<cfif Replies.ParentID EQ Topics.MsgID><cfset Variables.n = Replies.N><cfset Variables.last = Replies.LastPost></cfif>
		</cfloop>
		<cfif Topics.CurrentRow MOD 2><cfset Variables.bg = "FFFFFF"><cfelse><cfset Variables.bg = "FFFBF0"></cfif>
		<TR BGCOLOR="###Variables.bg#">
		<TD><FONT FACE="Arial, Helvetica" SIZE=2><IMG SRC="/CFIDE/administrator/images/file.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
			<A HREF="forums.cfm?thread=#Topics.MsgID#"><B>#HTMLEditFormat(Topics.Subject)#</B></A></FONT></TD>
		<TD><FONT FACE="Arial, Helvetica" SIZE=2>#HTMLEditFormat(Topics.Author)#</FONT></TD>
		<TD ALIGN=CENTER><FONT FACE="Arial, Helvetica" SIZE=2>#Variables.n#</FONT></TD>
		<TD><FONT FACE="Arial, Helvetica" SIZE=1>#DateFormat(Variables.last, "mmm d, yyyy")#</FONT></TD>
		</TR>
	</cfoutput>
	</TABLE>
	<cfset Variables.replyTo = 0>
</cfif>

<!--- ============================================================ post form --->
<H3><cfif Variables.replyTo>Post a reply<cfelse>Start a new topic</cfif></H3>
<cfif Len(Variables.postError)><P><FONT COLOR="#CC0000"><B><cfoutput>#Variables.postError#</cfoutput></B></FONT></P></cfif>
<cfoutput>
<FORM ACTION="forums.cfm" METHOD="POST">
<INPUT TYPE="hidden" NAME="ParentID" VALUE="#Variables.replyTo#">
<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Your name</B></FONT></TD><TD><INPUT TYPE="text" NAME="Author" SIZE=30 MAXLENGTH=50 VALUE="#HTMLEditFormat(Form.Author)#"></TD></TR>
<cfif NOT Variables.replyTo>
<TR><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Subject</B></FONT></TD><TD><INPUT TYPE="text" NAME="Subject" SIZE=50 MAXLENGTH=100 VALUE="#HTMLEditFormat(Form.Subject)#"></TD></TR>
</cfif>
<TR VALIGN=TOP><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Message</B></FONT></TD><TD><TEXTAREA NAME="Body" ROWS=6 COLS=55 WRAP="virtual">#HTMLEditFormat(Form.Body)#</TEXTAREA></TD></TR>
<TR><TD></TD><TD><INPUT TYPE="submit" NAME="Post" VALUE="Post Message"></TD></TR>
</TABLE>
</FORM>
</cfoutput>
<P><FONT SIZE=1>Prefer Usenet? These forums are also gatewayed to <CODE>comp.lang.cfml</CODE>, in our dreams.</FONT></P>
</FONT>
<cfinclude template="_sitefooter.cfm">
