<!---
	forum/post.cfm - form for a new thread or a reply
	  ?Topic_ID=n              new thread
	  ?Topic_ID=n&ParentID=m   reply to message m
--->
<CFPARAM NAME="URL.Topic_ID" DEFAULT="0">
<CFPARAM NAME="URL.ParentID" DEFAULT="0">
<CFSET Section = "forum">

<CFQUERY NAME="GetTopic" DATASOURCE="#Request.DSN#">
	SELECT Topic_ID, TopicName FROM Topics WHERE Topic_ID = #Val(URL.Topic_ID)#
</CFQUERY>
<CFIF GetTopic.RecordCount EQ 0>
	<CFLOCATION URL="index.cfm" ADDTOKEN="No">
</CFIF>

<CFSET DefaultSubject = "">
<CFSET Quoted = "">
<CFIF Val(URL.ParentID)>
	<CFQUERY NAME="GetParent" DATASOURCE="#Request.DSN#">
		SELECT Subject, Body, Author FROM Messages WHERE Msg_ID = #Val(URL.ParentID)#
	</CFQUERY>
	<CFIF GetParent.RecordCount>
		<CFSET DefaultSubject = "Re: " & GetParent.Subject>
		<CFSET Quoted = GetParent.Body>
		<CFSET PageTitle = "Reply to " & GetParent.Author>
	<CFELSE>
		<CFSET URL.ParentID = 0>
	</CFIF>
</CFIF>
<CFIF NOT Val(URL.ParentID)>
	<CFSET PageTitle = "Start a New Thread">
</CFIF>

<!--- who is posting? look up the e-mail address in the directory --->
<CFQUERY NAME="GetMe" DATASOURCE="#Request.DSN#">
	SELECT Email FROM Employees WHERE Emp_ID = #Val(Request.Emp_ID)#
</CFQUERY>

<CFINCLUDE TEMPLATE="../header.cfm">

<CFOUTPUT>
<FONT FACE="Arial, Helvetica" SIZE=2><A HREF="index.cfm">Forum</A> &gt; <A HREF="topic.cfm?Topic_ID=#GetTopic.Topic_ID#">#GetTopic.TopicName#</A></FONT>
<CFIF Len(Quoted)>
	<P><TABLE BORDER=0 CELLPADDING=6 WIDTH="90%"><TR><TD BGCOLOR="##EEEEEE"><FONT FACE="Arial, Helvetica" SIZE=1>
	<B>#HTMLEditFormat(GetParent.Author)# wrote:</B><BR>#HTMLEditFormat(Quoted)#</FONT></TD></TR></TABLE>
</CFIF>
</CFOUTPUT>

<CFFORM ACTION="post_action.cfm" METHOD="POST" NAME="PostForm">
<CFOUTPUT>
<INPUT TYPE="Hidden" NAME="Topic_ID" VALUE="#GetTopic.Topic_ID#">
<INPUT TYPE="Hidden" NAME="ParentID" VALUE="#Val(URL.ParentID)#">
<INPUT TYPE="Hidden" NAME="Subject_required" VALUE="Please give your message a subject.">
<INPUT TYPE="Hidden" NAME="Body_required" VALUE="Your message is empty.">
<INPUT TYPE="Hidden" NAME="Author_required" VALUE="Please enter your name.">
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2><B>Your name:</B></FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="Author" VALUE="#Request.FullName#" SIZE="30" MAXLENGTH="50" REQUIRED="Yes" MESSAGE="Please enter your name."></TD></TR>
<TR><TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2><B>E-mail:</B></FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="Email" VALUE="#GetMe.Email#" SIZE="30" MAXLENGTH="60"></TD></TR>
<TR><TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2><B>Subject:</B></FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="Subject" VALUE="#DefaultSubject#" SIZE="50" MAXLENGTH="100" REQUIRED="Yes" MESSAGE="Please give your message a subject."></TD></TR>
<TR VALIGN=TOP><TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2><B>Message:</B></FONT></TD>
	<TD><TEXTAREA NAME="Body" ROWS=8 COLS=50 WRAP="VIRTUAL"></TEXTAREA></TD></TR>
<TR><TD></TD><TD><INPUT TYPE="Submit" VALUE="Post Message"> <INPUT TYPE="Button" VALUE="Cancel" onClick="history.back()"></TD></TR>
</TABLE>
</CFOUTPUT>
</CFFORM>

<CFINCLUDE TEMPLATE="../footer.cfm">
