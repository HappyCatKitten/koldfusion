<!---
	index.cfm - GlobalCorp Intranet "What's New" home page
	Shows: company headlines, a hit counter kept in the Application scope,
	a stock ticker fetched with CFHTTP from our own quote server,
	today's meetings and the latest discussion forum posts.
--->
<CFSET PageTitle = "">
<CFSET Section = "home">

<!--- Count this visit. Application variables are shared by everyone, so lock. --->
<CFLOCK SCOPE="Application" TYPE="Exclusive" TIMEOUT="10">
	<CFSET Application.HitCount = Application.HitCount + 1>
	<CFSET Hits = Application.HitCount>
	<CFSET CountingSince = Application.StartedAt>
</CFLOCK>

<CFQUERY NAME="GetHeadlines" DATASOURCE="#Request.DSN#" MAXROWS="5">
	SELECT Headline_ID, Headline, Story, Posted
	FROM Headlines
	ORDER BY Posted DESC
</CFQUERY>

<CFQUERY NAME="TodaysMeetings" DATASOURCE="#Request.DSN#">
	SELECT b.StartTime, b.EndTime, b.Purpose, r.RoomName
	FROM Bookings b, Rooms r
	WHERE b.Room_ID = r.Room_ID
	  AND b.MeetingDate = <CFQUERYPARAM CFSQLTYPE="CF_SQL_DATE" VALUE="#Now()#">
	ORDER BY b.StartTime
</CFQUERY>

<CFQUERY NAME="LatestPosts" DATASOURCE="#Request.DSN#" MAXROWS="5">
	SELECT m.Msg_ID, m.Subject, m.Author, m.Posted, t.TopicName
	FROM Messages m, Topics t
	WHERE m.Topic_ID = t.Topic_ID
	ORDER BY m.Posted DESC
</CFQUERY>

<!---
	The stock ticker. Our "quote server" is just another KoldFusion page on
	this same web server, so we build its URL from the CGI variables.
	If it cannot be reached we say so instead of throwing an error.
--->
<CFSET QuoteURL = "http://#CGI.SERVER_NAME#:#CGI.SERVER_PORT##Request.Root#/quoteserver/quotes.cfm">
<CFSET TickerOK = FALSE>
<CFTRY>
	<CFHTTP URL="#QuoteURL#?symbols=GLBC,WDGT,CPLR,NETZ" METHOD="GET" TIMEOUT="5" THROWONERROR="Yes">
	</CFHTTP>
	<CFIF Find("200", CFHTTP.StatusCode) AND Len(Trim(CFHTTP.FileContent))>
		<CFSET TickerOK = TRUE>
		<CFSET TickerData = Trim(CFHTTP.FileContent)>
	</CFIF>
	<CFCATCH TYPE="Any">
		<CFSET TickerOK = FALSE>
	</CFCATCH>
</CFTRY>

<CFINCLUDE TEMPLATE="header.cfm">

<CFOUTPUT>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR VALIGN=TOP>
<TD>
	<BR>
	<FONT FACE="#Request.Font#" SIZE=4 COLOR="##003366"><B>Good <CFIF Hour(Now()) LT 12>morning<CFELSEIF Hour(Now()) LT 17>afternoon<CFELSE>evening</CFIF>, #HTMLEditFormat(ListFirst(Request.FullName, " "))#!</B></FONT><BR>
	<FONT FACE="#Request.Font#" SIZE=2>Here is what's new at #Request.CompanyName# today.</FONT>
	<HR SIZE=1 NOSHADE>

	<!--- Stock ticker --->
	<TABLE WIDTH="100%" BORDER=0 CELLPADDING=1 CELLSPACING=0 BGCOLOR="##000000"><TR><TD>
	<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0 BGCOLOR="##000033">
	<TR>
	<TD><FONT FACE="Courier New, Courier" SIZE=2 COLOR="##FFCC00"><B>MARKET</B></FONT></TD>
	<CFIF TickerOK>
		<CFLOOP LIST="#TickerData#" INDEX="QuoteLine" DELIMITERS="#Chr(13)##Chr(10)#">
			<CFIF ListLen(QuoteLine, "|") EQ 4>
				<CFSET Sym = ListGetAt(QuoteLine, 1, "|")>
				<CFSET Price = ListGetAt(QuoteLine, 3, "|")>
				<CFSET Change = Val(Trim(ListGetAt(QuoteLine, 4, "|")))>
				<TD NOWRAP><FONT FACE="Courier New, Courier" SIZE=2 COLOR="##FFFFFF"><B>#Sym#</B> #NumberFormat(Price, "999.999")#</FONT>
				<CFIF Change GT 0><IMG SRC="#Request.Images#/up.gif" WIDTH=9 HEIGHT=9 ALT="up"><FONT FACE="Courier New, Courier" SIZE=2 COLOR="##33FF33">+#NumberFormat(Change, "9.999")#</FONT>
				<CFELSEIF Change LT 0><IMG SRC="#Request.Images#/down.gif" WIDTH=9 HEIGHT=9 ALT="down"><FONT FACE="Courier New, Courier" SIZE=2 COLOR="##FF3333">#NumberFormat(Change, "9.999")#</FONT>
				<CFELSE><FONT FACE="Courier New, Courier" SIZE=2 COLOR="##CCCCCC">unch</FONT></CFIF>
				</TD>
			</CFIF>
		</CFLOOP>
	<CFELSE>
		<TD><FONT FACE="Courier New, Courier" SIZE=2 COLOR="##CCCCCC">Quote server not responding - try again later.</FONT></TD>
	</CFIF>
	</TR>
	</TABLE>
	</TD></TR></TABLE>
	<FONT FACE="#Request.Font#" SIZE=1 COLOR="##666666">Quotes delayed at least 20 minutes. Fetched with CFHTTP from <A HREF="#Request.Root#/quoteserver/quotes.cfm?symbols=GLBC,WDGT,CPLR,NETZ">our quote server</A>.</FONT>

	<!--- Headlines --->
	<P><FONT FACE="#Request.Font#" SIZE=3 COLOR="##003366"><B>Company Headlines</B></FONT>
	<CFIF Request.IsAdmin>&nbsp;<FONT FACE="#Request.Font#" SIZE=1>[<A HREF="news.cfm?action=new">post a headline</A>]</FONT></CFIF>
	<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0 WIDTH="100%">
	<CFLOOP QUERY="GetHeadlines">
	<TR VALIGN=TOP>
		<TD WIDTH=16><IMG SRC="/images/bullet_blue.gif" WIDTH=13 HEIGHT=13 VSPACE=2></TD>
		<TD><FONT FACE="#Request.Font#" SIZE=2>
		<A HREF="news.cfm?ID=#Headline_ID#"><B>#Headline#</B></A>
		<CFIF DateDiff("d", Posted, Now()) LT 7><IMG SRC="/images/new.gif" WIDTH=44 HEIGHT=22 ALIGN=ABSMIDDLE ALT="New!"></CFIF><BR>
		<FONT SIZE=1 COLOR="##666666">#DateFormat(Posted, "mmmm d, yyyy")#</FONT> -
		<CFIF Len(Story) GT 90>#Left(Story, 90)#...<CFELSE>#Story#</CFIF>
		</FONT></TD>
	</TR>
	</CFLOOP>
	</TABLE>
	<FONT FACE="#Request.Font#" SIZE=1><A HREF="news.cfm">All headlines...</A></FONT>
	</P>
</TD>
<TD WIDTH=16>&nbsp;</TD>
<TD WIDTH=210>
	<BR>
	<!--- Today's meetings --->
	<TABLE WIDTH=210 BORDER=0 CELLPADDING=4 CELLSPACING=0>
	<TR><TD BGCOLOR="##003366"><FONT FACE="#Request.Font#" SIZE=2 COLOR="##FFFFFF"><B>Today's Meetings</B></FONT></TD></TR>
	<TR><TD BGCOLOR="##EEEEEE"><FONT FACE="#Request.Font#" SIZE=1>
	<CFIF TodaysMeetings.RecordCount EQ 0>
		No rooms are booked today.<BR>
	<CFELSE>
		<CFLOOP QUERY="TodaysMeetings">
			<B>#TimeFormat(CreateTime(Int(StartTime / 100), StartTime MOD 100, 0), "h:mm tt")#</B>
			#RoomName#: #HTMLEditFormat(Purpose)#<BR>
		</CFLOOP>
	</CFIF>
	<A HREF="scheduler/index.cfm">Book a room...</A>
	</FONT></TD></TR>
	</TABLE>
	<BR>
	<!--- Latest forum posts --->
	<TABLE WIDTH=210 BORDER=0 CELLPADDING=4 CELLSPACING=0>
	<TR><TD BGCOLOR="##003366"><FONT FACE="#Request.Font#" SIZE=2 COLOR="##FFFFFF"><B>Latest in the Forum</B></FONT></TD></TR>
	<TR><TD BGCOLOR="##EEEEEE"><FONT FACE="#Request.Font#" SIZE=1>
	<CFLOOP QUERY="LatestPosts">
		<A HREF="forum/message.cfm?Msg_ID=#Msg_ID#">#HTMLEditFormat(Subject)#</A><BR>
		<FONT COLOR="##666666">#HTMLEditFormat(Author)#, #DateFormat(Posted, "mmm d")# in #TopicName#</FONT><BR>
	</CFLOOP>
	</FONT></TD></TR>
	</TABLE>
	<BR>
	<!--- Hit counter --->
	<TABLE WIDTH=210 BORDER=0 CELLPADDING=4 CELLSPACING=0>
	<TR><TD ALIGN=CENTER BGCOLOR="##EEEEEE"><FONT FACE="#Request.Font#" SIZE=1>You are visitor number<BR>
	<CFSET HitString = NumberFormat(Hits, "000000")>
	<CFLOOP INDEX="d" FROM="1" TO="#Len(HitString)#"><IMG SRC="/images/digit_#Mid(HitString, d, 1)#.gif" WIDTH=15 HEIGHT=20 ALT="#Mid(HitString, d, 1)#"></CFLOOP><BR>
	since #DateFormat(CountingSince, "mm/dd/yy")# #TimeFormat(CountingSince, "h:mm tt")#
	</FONT></TD></TR>
	</TABLE>
</TD>
</TR>
</TABLE>
</CFOUTPUT>

<CFINCLUDE TEMPLATE="footer.cfm">
