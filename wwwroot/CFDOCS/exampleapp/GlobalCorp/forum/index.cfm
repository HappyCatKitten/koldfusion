<!---
	forum/index.cfm - list of discussion topics with post counts
--->
<CFSET PageTitle = "Discussion Forum">
<CFSET Section = "forum">

<CFQUERY NAME="GetTopics" DATASOURCE="#Request.DSN#">
	SELECT t.Topic_ID, t.TopicName, t.Description,
	       COUNT(m.Msg_ID) AS Posts, MAX(m.Posted) AS LastPost
	FROM Topics t LEFT JOIN Messages m ON m.Topic_ID = t.Topic_ID
	GROUP BY t.Topic_ID, t.TopicName, t.Description, t.SortOrder
	ORDER BY t.SortOrder
</CFQUERY>

<CFQUERY NAME="ThreadCounts" DATASOURCE="#Request.DSN#">
	SELECT Topic_ID, COUNT(*) AS Threads
	FROM Messages
	WHERE ParentID = 0
	GROUP BY Topic_ID
</CFQUERY>
<!--- turn the thread counts into a structure keyed by topic --->
<CFSET Threads = StructNew()>
<CFLOOP QUERY="ThreadCounts">
	<CFSET Threads[Topic_ID] = ThreadCounts.Threads>
</CFLOOP>

<CFINCLUDE TEMPLATE="../header.cfm">

<P>Talk with your coworkers about anything GlobalCorp. Please keep it friendly: everyone can read what you post.
Topics with posts in the last three days are marked <IMG SRC="/images/new.gif" WIDTH=44 HEIGHT=22 ALIGN=ABSMIDDLE ALT="New!">.</P>

<TABLE WIDTH="100%" BORDER=0 CELLPADDING=4 CELLSPACING=1>
<TR BGCOLOR="#003366">
	<TD><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Topic</B></FONT></TD>
	<TD ALIGN=CENTER><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Threads</B></FONT></TD>
	<TD ALIGN=CENTER><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Posts</B></FONT></TD>
	<TD><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>Last Post</B></FONT></TD>
</TR>
<CFOUTPUT QUERY="GetTopics">
<TR BGCOLOR="###IIf(CurrentRow MOD 2, DE('FFFFFF'), DE('EEEEF8'))#" VALIGN=TOP>
	<TD><IMG SRC="#Request.Images#/ic_forum.gif" WIDTH=32 HEIGHT=32 ALIGN=LEFT HSPACE=4>
		<FONT FACE="Arial, Helvetica" SIZE=2><A HREF="topic.cfm?Topic_ID=#Topic_ID#"><B>#TopicName#</B></A>
		<CFIF IsDate(LastPost)><CFIF DateDiff("h", LastPost, Now()) LT 72><IMG SRC="/images/new.gif" WIDTH=44 HEIGHT=22 ALIGN=ABSMIDDLE ALT="New!"></CFIF></CFIF><BR>
		<FONT SIZE=1>#Description#</FONT></FONT></TD>
	<TD ALIGN=CENTER><FONT FACE="Arial, Helvetica" SIZE=2><CFIF StructKeyExists(Threads, Topic_ID)>#Threads[Topic_ID]#<CFELSE>0</CFIF></FONT></TD>
	<TD ALIGN=CENTER><FONT FACE="Arial, Helvetica" SIZE=2>#Posts#</FONT></TD>
	<TD NOWRAP><FONT FACE="Arial, Helvetica" SIZE=1><CFIF IsDate(LastPost)>#DateFormat(LastPost, "mmm d, yyyy")#<BR>#TimeFormat(LastPost, "h:mm tt")#<CFELSE>never</CFIF></FONT></TD>
</TR>
</CFOUTPUT>
</TABLE>

<CFINCLUDE TEMPLATE="../footer.cfm">
