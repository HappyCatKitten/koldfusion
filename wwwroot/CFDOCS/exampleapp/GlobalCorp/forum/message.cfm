<!---
	forum/message.cfm - read one message, with the rest of its thread below
	  ?Msg_ID=n
--->
<CFPARAM NAME="URL.Msg_ID" DEFAULT="0">
<CFPARAM NAME="URL.posted" DEFAULT="">
<CFSET Section = "forum">

<CFQUERY NAME="GetMessage" DATASOURCE="#Request.DSN#">
	SELECT m.*, t.TopicName
	FROM Messages m, Topics t
	WHERE m.Topic_ID = t.Topic_ID
	  AND m.Msg_ID = #Val(URL.Msg_ID)#
</CFQUERY>
<CFIF GetMessage.RecordCount EQ 0>
	<CFLOCATION URL="index.cfm" ADDTOKEN="No">
</CFIF>

<CFQUERY NAME="GetThread" DATASOURCE="#Request.DSN#">
	SELECT Msg_ID, ParentID, Subject, Author, Posted
	FROM Messages
	WHERE ThreadID = #GetMessage.ThreadID#
	ORDER BY Posted
</CFQUERY>

<CFSET PageTitle = GetMessage.Subject>
<CFINCLUDE TEMPLATE="../header.cfm">

<CFOUTPUT QUERY="GetMessage">
<FONT FACE="Arial, Helvetica" SIZE=2><A HREF="index.cfm">Forum</A> &gt; <A HREF="topic.cfm?Topic_ID=#Topic_ID#">#TopicName#</A></FONT>
<CFIF URL.posted IS "yes"><P><FONT COLOR="##006600"><B>Thanks! Your message has been posted.</B></FONT></P></CFIF>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=1 CELLSPACING=0 BGCOLOR="##003366"><TR><TD>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=6 CELLSPACING=0>
<TR BGCOLOR="##DDDDEE"><TD><FONT FACE="Arial, Helvetica" SIZE=2>
	<B>From:</B> <A HREF="mailto:#Email#">#HTMLEditFormat(Author)#</A><BR>
	<B>Posted:</B> #DateFormat(Posted, "dddd, mmmm d, yyyy")# at #TimeFormat(Posted, "h:mm tt")#<BR>
	<B>Subject:</B> #HTMLEditFormat(Subject)#
</FONT></TD></TR>
<TR BGCOLOR="##FFFFFF"><TD><FONT FACE="Arial, Helvetica" SIZE=2>#ParagraphFormat(HTMLEditFormat(Body))#</FONT></TD></TR>
</TABLE>
</TD></TR></TABLE>
<FORM ACTION="post.cfm" METHOD="GET">
<INPUT TYPE="Hidden" NAME="Topic_ID" VALUE="#Topic_ID#">
<INPUT TYPE="Hidden" NAME="ParentID" VALUE="#Msg_ID#">
<INPUT TYPE="Submit" VALUE="Reply to This Message">
</FORM>
</CFOUTPUT>

<P><B>This thread:</B></P>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0>
<CFMODULE TEMPLATE="threadtree.cfm" Messages="#GetThread#" ParentID="0" Current="#GetMessage.Msg_ID#">
</TABLE>

<CFINCLUDE TEMPLATE="../footer.cfm">
