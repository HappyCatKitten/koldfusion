<!--- /CFDOCS/registration.cfm - the KoldFusion product registration card.
      Registrations really are stored, in the Registrations table of the cfsnippets data source. --->
<cfset pageTitle = "Register KoldFusion 4.5">
<cfset section = "registration.cfm">
<cfparam name="Form.FirstName" default="">
<cfparam name="Form.LastName" default="">
<cfparam name="Form.Company" default="">
<cfparam name="Form.Email" default="">
<cfparam name="Form.Platform" default="">
<cfparam name="Form.WebServer" default="">
<cfparam name="Form.Modem" default="56K">
<cfparam name="Form.HeardFrom" default="">
<cfparam name="Form.Comments" default="">
<cfset Variables.platforms = "Windows NT 4.0,Windows 98,Windows 95 (bravely),Solaris 7,Red Hat Linux 6.1,HP-UX 11,BeOS (we admire your spirit),Other">
<cfset Variables.webServers = "Microsoft IIS 4.0,Netscape Enterprise Server 3.6,Apache 1.3,O'Reilly WebSite Pro,KoldFusion built-in server,Other">
<cfset Variables.modems = "14.4K,28.8K,56K,ISDN,T1,Cable modem (lucky you)">
<cfset Variables.sources = "Trade magazine,A friend,Usenet (comp.lang.cfml),Banner ad,Trade show,An AltaVista search,The box it came in">
<cfset Variables.errors = "">

<cfif IsDefined("Form.Register")>
	<!--- server-side checks (the browser's JavaScript may be switched off) --->
	<cfif NOT Len(Trim(Form.FirstName)) OR NOT Len(Trim(Form.LastName))>
		<cfset Variables.errors = ListAppend(Variables.errors, "Please tell us your first and last name.", "|")>
	</cfif>
	<cfif NOT REFind("^[^@ ]+@[^@ ]+$", Trim(Form.Email))>
		<cfset Variables.errors = ListAppend(Variables.errors, "Please enter an e-mail address that looks like one (name@host).", "|")>
	</cfif>
	<cfif NOT ListFind(Variables.platforms, Form.Platform)>
		<cfset Variables.errors = ListAppend(Variables.errors, "Please choose your operating system.", "|")>
	</cfif>
	<cfif NOT Len(Variables.errors)>
		<cfquery name="AddRegistration" datasource="cfsnippets">
		INSERT INTO Registrations (FirstName, LastName, Company, Email, Platform, WebServer, Modem, HeardFrom,
		                           Y2KReady, Newsletter, Comments, Registered)
		VALUES (
			<cfqueryparam value="#Left(Trim(Form.FirstName), 30)#" cfsqltype="CF_SQL_VARCHAR">,
			<cfqueryparam value="#Left(Trim(Form.LastName), 30)#" cfsqltype="CF_SQL_VARCHAR">,
			<cfqueryparam value="#Left(Trim(Form.Company), 60)#" cfsqltype="CF_SQL_VARCHAR">,
			<cfqueryparam value="#Left(Trim(Form.Email), 60)#" cfsqltype="CF_SQL_VARCHAR">,
			<cfqueryparam value="#Left(Form.Platform, 40)#" cfsqltype="CF_SQL_VARCHAR">,
			<cfqueryparam value="#Left(Form.WebServer, 40)#" cfsqltype="CF_SQL_VARCHAR">,
			<cfqueryparam value="#Left(Form.Modem, 30)#" cfsqltype="CF_SQL_VARCHAR">,
			<cfqueryparam value="#Left(Form.HeardFrom, 40)#" cfsqltype="CF_SQL_VARCHAR">,
			<cfqueryparam value="#IsDefined('Form.Y2KReady')#" cfsqltype="CF_SQL_BIT">,
			<cfqueryparam value="#IsDefined('Form.Newsletter')#" cfsqltype="CF_SQL_BIT">,
			<cfqueryparam value="#Left(Form.Comments, 2000)#" cfsqltype="CF_SQL_LONGVARCHAR">,
			<cfqueryparam value="#Now()#" cfsqltype="CF_SQL_TIMESTAMP">
		)
		</cfquery>
		<cfquery name="NewID" datasource="cfsnippets">SELECT @@IDENTITY AS RegID</cfquery>
		<cfquery name="Stats" datasource="cfsnippets">SELECT COUNT(*) AS Total FROM Registrations</cfquery>
		<cfquery name="SamePlatform" datasource="cfsnippets">
		SELECT COUNT(*) AS N FROM Registrations
		WHERE Platform = <cfqueryparam value="#Form.Platform#" cfsqltype="CF_SQL_VARCHAR">
		</cfquery>
		<!--- a serial number that looks important --->
		<cfset Variables.serial = "KFE-" & NumberFormat(NewID.RegID, "000000") & "-" & UCase(Left(Hash(Form.Email & NewID.RegID), 6))>

		<cfinclude template="_siteheader.cfm">
		<cfoutput>
		<FONT FACE="Arial, Helvetica" SIZE=3><B>Thank you, #HTMLEditFormat(Form.FirstName)#!</B></FONT>
		<P><FONT FACE="Arial, Helvetica" SIZE=2>Your copy of KoldFusion Server 4.5 is now registered. You are registered
		user number <B>#NewID.RegID#</B>, one of #Stats.Total# fine people who have filled in this form
		(#SamePlatform.N# of them on #HTMLEditFormat(Form.Platform)#).</FONT></P>
		<TABLE BORDER=0 CELLPADDING=1 CELLSPACING=0 BGCOLOR="##000066"><TR><TD>
		<TABLE BORDER=0 CELLPADDING=8 CELLSPACING=0 BGCOLOR="##FFFFF0"><TR><TD>
		<FONT FACE="Arial, Helvetica" SIZE=1>REGISTRATION CERTIFICATE</FONT><BR>
		<FONT FACE="Courier New, Courier" SIZE=3><B>#Variables.serial#</B></FONT><BR>
		<FONT FACE="Arial, Helvetica" SIZE=1>Issued #DateFormat(Now(), "mmmm d, yyyy")# to #HTMLEditFormat(Form.FirstName)# #HTMLEditFormat(Form.LastName)#<cfif Len(Trim(Form.Company))>, #HTMLEditFormat(Form.Company)#</cfif></FONT>
		</TD></TR></TABLE>
		</TD></TR></TABLE>
		<FONT FACE="Arial, Helvetica" SIZE=2>
		<P>As a registered user you are entitled to:</P>
		<UL>
		<LI>30 days of free installation support (the clock started when you clicked the button)
		<LI>Discounts on <A HREF="training.cfm">Gibson training courses</A>
		<LI>One genuine KoldFusion mousepad, which will ship in 6 to 8 weeks
		<cfif IsDefined("Form.Newsletter")><LI>The <I>KoldFusion Developer Newsletter</I>, sent to #HTMLEditFormat(Form.Email)# whenever we remember</cfif>
		</UL>
		<cfif NOT IsDefined("Form.Y2KReady")>
			<P><IMG SRC="/CFIDE/administrator/images/warn.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
			You told us your systems are not yet Year 2000 ready. Our <A HREF="training.cfm">Y2K100</A> course
			still has seats, but at this point we would hurry.</P>
		</cfif>
		<P>Please print this page for your records, or at least squint at it meaningfully.</P>
		<P><A HREF="/CFDOCS/index.cfm">Back to the welcome page</A> &middot; <A HREF="dochome.cfm">Read the documentation</A></P>
		</FONT>
		</cfoutput>
		<cfinclude template="_sitefooter.cfm">
		<cfabort>
	</cfif>
</cfif>

<cfquery name="Stats" datasource="cfsnippets">SELECT COUNT(*) AS Total FROM Registrations</cfquery>
<cfinclude template="_siteheader.cfm">
<FONT FACE="Arial, Helvetica" SIZE=2>
<P>Register your copy of KoldFusion Server 4.5 today and join a thriving community of
<cfoutput><B>#Stats.Total#</B></cfoutput> registered developers. Registration takes about a minute on a
28.8K modem. Fields marked <FONT COLOR="#CC0000">*</FONT> are required.</P>

<cfif Len(Variables.errors)>
	<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0 BGCOLOR="#FFFFCC"><TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>
	<IMG SRC="/CFIDE/administrator/images/warn.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE> <B>Almost there.</B>
	<UL><cfloop list="#Variables.errors#" delimiters="|" index="e"><LI><cfoutput>#e#</cfoutput></cfloop></UL>
	</FONT></TD></TR></TABLE>
</cfif>

<SCRIPT LANGUAGE="JavaScript">
<!--
function checkCard(f) {
	if (f.FirstName.value == "" || f.LastName.value == "") { alert("Please tell us your first and last name."); return false; }
	if (f.Email.value.indexOf("@") < 1) { alert("Please enter your e-mail address."); f.Email.focus(); return false; }
	if (f.Platform.selectedIndex == 0) { alert("Please choose your operating system."); return false; }
	return true;
}
//-->
</SCRIPT>
<cfoutput>
<FORM ACTION="registration.cfm" METHOD="POST" onSubmit="return checkCard(this)">
<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>First name</B><FONT COLOR="##CC0000">*</FONT></FONT></TD>
	<TD><INPUT TYPE="text" NAME="FirstName" SIZE=20 MAXLENGTH=30 VALUE="#HTMLEditFormat(Form.FirstName)#">
	<FONT FACE="Arial, Helvetica" SIZE=2><B>Last name</B><FONT COLOR="##CC0000">*</FONT></FONT>
	<INPUT TYPE="text" NAME="LastName" SIZE=20 MAXLENGTH=30 VALUE="#HTMLEditFormat(Form.LastName)#"></TD></TR>
<TR><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Company</B></FONT></TD>
	<TD><INPUT TYPE="text" NAME="Company" SIZE=50 MAXLENGTH=60 VALUE="#HTMLEditFormat(Form.Company)#"></TD></TR>
<TR><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>E-mail</B><FONT COLOR="##CC0000">*</FONT></FONT></TD>
	<TD><INPUT TYPE="text" NAME="Email" SIZE=50 MAXLENGTH=60 VALUE="#HTMLEditFormat(Form.Email)#"></TD></TR>
<TR><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Operating system</B><FONT COLOR="##CC0000">*</FONT></FONT></TD>
	<TD><SELECT NAME="Platform"><OPTION VALUE="">-- please choose --
	<cfloop list="#Variables.platforms#" index="p"><OPTION<cfif p EQ Form.Platform> SELECTED</cfif>>#HTMLEditFormat(p)#</cfloop>
	</SELECT></TD></TR>
<TR><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Web server</B></FONT></TD>
	<TD><SELECT NAME="WebServer">
	<cfloop list="#Variables.webServers#" index="p"><OPTION<cfif p EQ Form.WebServer> SELECTED</cfif>>#HTMLEditFormat(p)#</cfloop>
	</SELECT></TD></TR>
<TR VALIGN=TOP><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Connection</B></FONT></TD>
	<TD><FONT FACE="Arial, Helvetica" SIZE=2>
	<cfloop list="#Variables.modems#" index="p"><INPUT TYPE="radio" NAME="Modem" VALUE="#HTMLEditFormat(p)#"<cfif p EQ Form.Modem> CHECKED</cfif>>#HTMLEditFormat(p)# </cfloop>
	</FONT></TD></TR>
<TR><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>How did you<BR>hear about us?</B></FONT></TD>
	<TD><SELECT NAME="HeardFrom">
	<cfloop list="#Variables.sources#" index="p"><OPTION<cfif p EQ Form.HeardFrom> SELECTED</cfif>>#HTMLEditFormat(p)#</cfloop>
	</SELECT></TD></TR>
<TR><TD></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>
	<INPUT TYPE="checkbox" NAME="Y2KReady" VALUE="1"<cfif IsDefined("Form.Y2KReady") OR NOT IsDefined("Form.Register")> CHECKED</cfif>> My systems are Year 2000 ready<BR>
	<INPUT TYPE="checkbox" NAME="Newsletter" VALUE="1"<cfif IsDefined("Form.Newsletter")> CHECKED</cfif>> Send me the <I>KoldFusion Developer Newsletter</I> (plain text, no animated GIFs)
	</FONT></TD></TR>
<TR VALIGN=TOP><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Comments</B></FONT></TD>
	<TD><TEXTAREA NAME="Comments" ROWS=4 COLS=50 WRAP="virtual">#HTMLEditFormat(Form.Comments)#</TEXTAREA></TD></TR>
<TR><TD></TD><TD><INPUT TYPE="submit" NAME="Register" VALUE="Register Now"> <INPUT TYPE="reset" VALUE="Start Over"></TD></TR>
</TABLE>
</FORM>
</cfoutput>
<P><FONT FACE="Arial, Helvetica" SIZE=1><B>Privacy:</B> Gibson will never sell, rent or trade your personal
information. It stays right here, in a flat file on your own server, which is honestly the safest place on the Internet.</FONT></P>
</FONT>
<cfinclude template="_sitefooter.cfm">
