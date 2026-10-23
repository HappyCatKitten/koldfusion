<!---
	forum/topic.cfm - every thread in one topic, drawn as a tree
	  ?Topic_ID=n
--->
<CFPARAM NAME="URL.Topic_ID" DEFAULT="0">
<CFSET Section = "forum">

<CFQUERY NAME="GetTopic" DATASOURCE="#Request.DSN#">
	SELECT Topic_ID, TopicName, Description FROM Topics WHERE Topic_ID = #Val(URL.Topic_ID)#
</CFQUERY>
<CFIF GetTopic.RecordCount EQ 0>
	<CFLOCATION URL="index.cfm" ADDTOKEN="No">
</CFIF>

<CFQUERY NAME="GetMessages" DATASOURCE="#Request.DSN#">
	SELECT Msg_ID, ParentID, ThreadID, Subject, Author, Posted
	FROM Messages
	WHERE Topic_ID = #GetTopic.Topic_ID#
	ORDER BY Posted
</CFQUERY>

<CFSET PageTitle = GetTopic.TopicName>
<CFINCLUDE TEMPLATE="../header.cfm">

<CFOUTPUT>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0><TR>
<TD><FONT FACE="Arial, Helvetica" SIZE=2><A HREF="index.cfm">Forum</A> &gt; #GetTopic.TopicName#<BR><I>#GetTopic.Description#</I></FONT></TD>
<TD ALIGN=RIGHT><FORM ACTION="post.cfm" METHOD="GET"><INPUT TYPE="Hidden" NAME="Topic_ID" VALUE="#GetTopic.Topic_ID#"><INPUT TYPE="Submit" VALUE="Start a New Thread"></FORM></TD>
</TR></TABLE>
</CFOUTPUT>

<CFIF GetMessages.RecordCount EQ 0>
	<P>Nobody has posted here yet. Be the first!</P>
<CFELSE>
	<TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0>
	<TR BGCOLOR="#CCCCCC">
		<TD><FONT FACE="Arial, Helvetica" SIZE=1><B>Subject</B></FONT></TD>
		<TD><FONT FACE="Arial, Helvetica" SIZE=1><B>Posted by</B></FONT></TD>
		<TD><FONT FACE="Arial, Helvetica" SIZE=1><B>Date</B></FONT></TD>
	</TR>
	<CFMODULE TEMPLATE="threadtree.cfm" Messages="#GetMessages#" ParentID="0" NewestFirst="Yes">
	</TABLE>
</CFIF>

<CFINCLUDE TEMPLATE="../footer.cfm">
