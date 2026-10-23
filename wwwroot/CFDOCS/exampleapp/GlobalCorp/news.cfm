<!---
	news.cfm - company headlines
	  news.cfm              all headlines
	  news.cfm?ID=n         one story
	  news.cfm?action=new   form to post a headline (admins only)
	  POST action=add       saves the headline
--->
<CFPARAM NAME="URL.action" DEFAULT="list">
<CFPARAM NAME="URL.ID" DEFAULT="0">
<CFSET PageTitle = "Company Headlines">
<CFSET Section = "home">
<CFSET Message = "">

<!--- Save a new headline --->
<CFIF IsDefined("Form.Headline") AND Request.IsAdmin>
	<CFQUERY DATASOURCE="#Request.DSN#">
		INSERT INTO Headlines (Headline, Story, Posted)
		VALUES ('#Trim(Form.Headline)#', '#Trim(Form.Story)#',
		        <CFQUERYPARAM CFSQLTYPE="CF_SQL_TIMESTAMP" VALUE="#Now()#">)
	</CFQUERY>
	<CFSET Message = "Your headline has been posted.">
</CFIF>

<CFIF Val(URL.ID)>
	<CFQUERY NAME="GetStory" DATASOURCE="#Request.DSN#">
		SELECT Headline, Story, Posted FROM Headlines WHERE Headline_ID = #Val(URL.ID)#
	</CFQUERY>
	<CFIF GetStory.RecordCount>
		<CFSET PageTitle = GetStory.Headline>
	</CFIF>
<CFELSE>
	<CFQUERY NAME="GetHeadlines" DATASOURCE="#Request.DSN#">
		SELECT Headline_ID, Headline, Story, Posted FROM Headlines ORDER BY Posted DESC
	</CFQUERY>
</CFIF>

<CFINCLUDE TEMPLATE="header.cfm">

<CFOUTPUT>
<CFIF Len(Message)><P><FONT COLOR="##006600"><B>#Message#</B></FONT></P></CFIF>

<CFIF Val(URL.ID)>
	<CFIF GetStory.RecordCount EQ 0>
		<P>Sorry, that headline could not be found. It may have been removed.</P>
	<CFELSE>
		<FONT SIZE=1 COLOR="##666666">Posted #DateFormat(GetStory.Posted, "dddd, mmmm d, yyyy")# at #TimeFormat(GetStory.Posted, "h:mm tt")#</FONT>
		<P>#ParagraphFormat(HTMLEditFormat(GetStory.Story))#</P>
	</CFIF>
	<P><A HREF="news.cfm">&lt;&lt; All headlines</A></P>

<CFELSEIF URL.action IS "new" AND Request.IsAdmin>
	<P>Headlines appear on the What's New page for everyone in the company.</P>
	<CFFORM ACTION="news.cfm" METHOD="POST" NAME="NewsForm">
	<!--- server-side validation, in case JavaScript is turned off --->
	<INPUT TYPE="Hidden" NAME="Headline_required" VALUE="Please enter a headline.">
	<INPUT TYPE="Hidden" NAME="Story_required" VALUE="Please enter the story.">
	<TABLE BORDER=0 CELLPADDING=3>
	<TR><TD><FONT FACE="#Request.Font#" SIZE=2><B>Headline:</B></FONT></TD>
		<TD><CFINPUT TYPE="Text" NAME="Headline" SIZE="60" MAXLENGTH="120" REQUIRED="Yes" MESSAGE="Please enter a headline."></TD></TR>
	<TR VALIGN=TOP><TD><FONT FACE="#Request.Font#" SIZE=2><B>Story:</B></FONT></TD>
		<TD><TEXTAREA NAME="Story" ROWS=6 COLS=55 WRAP="VIRTUAL"></TEXTAREA></TD></TR>
	<TR><TD></TD><TD><INPUT TYPE="Submit" VALUE="Post Headline"></TD></TR>
	</TABLE>
	</CFFORM>

<CFELSE>
	<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0>
	<CFLOOP QUERY="GetHeadlines">
	<TR VALIGN=TOP>
		<TD NOWRAP><FONT FACE="#Request.Font#" SIZE=1 COLOR="##666666">#DateFormat(Posted, "mm/dd/yyyy")#</FONT></TD>
		<TD><FONT FACE="#Request.Font#" SIZE=2><A HREF="news.cfm?ID=#Headline_ID#"><B>#HTMLEditFormat(Headline)#</B></A>
		<CFIF DateDiff("d", Posted, Now()) LT 7><IMG SRC="/images/new.gif" WIDTH=44 HEIGHT=22 ALIGN=ABSMIDDLE ALT="New!"></CFIF>
		</FONT></TD>
	</TR>
	</CFLOOP>
	</TABLE>
	<CFIF Request.IsAdmin><P><A HREF="news.cfm?action=new">Post a new headline</A></P></CFIF>
</CFIF>
</CFOUTPUT>

<CFINCLUDE TEMPLATE="footer.cfm">
