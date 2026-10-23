<!--- the obligatory 1999 guestbook --->
<cfset pageTitle = "Guestbook">
<cfif IsDefined("Form.SignIt")>
	<cfquery datasource="cfsnippets">
		INSERT INTO GuestBook (Name, Email, Comments, Posted)
		VALUES (<cfqueryparam value="#Left(Form.Name, 50)#" cfsqltype="CF_SQL_VARCHAR">,
		        <cfqueryparam value="#Left(Form.Email, 80)#" cfsqltype="CF_SQL_VARCHAR">,
		        <cfqueryparam value="#Left(Form.Comments, 1000)#" cfsqltype="CF_SQL_LONGVARCHAR">,
		        <cfqueryparam value="#Now()#" cfsqltype="CF_SQL_TIMESTAMP">)
	</cfquery>
	<cflocation url="guestbook.cfm?thanks=1" addtoken="no">
</cfif>
<cfquery name="entries" datasource="cfsnippets">SELECT * FROM GuestBook ORDER BY Posted DESC</cfquery>
<cfinclude template="_top.cfm">
<cfif IsDefined("URL.thanks")><P><FONT COLOR="#009900"><B>Thanks for signing! Come back soon!</B></FONT></P></cfif>
<TABLE BORDER=0 CELLPADDING=10><TR VALIGN=TOP><TD WIDTH="55%">
<cfoutput query="entries">
<TABLE WIDTH="100%" BORDER=1 CELLPADDING=6 CELLSPACING=0 BGCOLOR="##FFFFEE"><TR><TD>
<FONT FACE="Arial" SIZE=2><B>#HTMLEditFormat(Name)#</B><cfif Len(Email)> &lt;<A HREF="mailto:#HTMLEditFormat(Email)#">#HTMLEditFormat(Email)#</A>&gt;</cfif>
<cfif IsDate(Posted)> wrote on #DateFormat(Posted, "mmmm d, yyyy")# at #TimeFormat(Posted, "h:mm tt")#:</cfif>
<cfif IsDate(Posted) AND DateDiff("d", Posted, Now()) LT 2> <IMG SRC="/images/new.gif" WIDTH=44 HEIGHT=22 ALIGN=ABSMIDDLE></cfif>
<P>#ParagraphFormat(HTMLEditFormat(Comments))#</FONT></TD></TR></TABLE><BR>
</cfoutput>
</TD><TD>
<cfform action="guestbook.cfm" method="POST" name="gb">
<TABLE BORDER=1 CELLPADDING=6 CELLSPACING=0 BGCOLOR="#CCCCFF"><TR><TD>
<FONT FACE="Arial" SIZE=2><B>Sign my guestbook!</B><BR><BR>
Name:<BR><cfinput type="text" name="Name" size="30" required="yes" message="Please tell us your name."><BR>
E-mail:<BR><cfinput type="text" name="Email" size="30"><BR>
Comments:<BR><TEXTAREA NAME="Comments" ROWS=6 COLS=30 WRAP=VIRTUAL></TEXTAREA><BR>
<INPUT TYPE="hidden" NAME="Comments_required" VALUE="Please leave a comment!">
<INPUT TYPE="submit" NAME="SignIt" VALUE="Sign It!"> <INPUT TYPE="reset" VALUE="Start Over">
</FONT></TD></TR></TABLE>
</cfform>
<P><IMG SRC="/images/mailbox.gif" WIDTH=32 HEIGHT=32> <cfoutput>#entries.RecordCount#</cfoutput> people have signed so far.
</TD></TR></TABLE>
<cfinclude template="_bottom.cfm">
