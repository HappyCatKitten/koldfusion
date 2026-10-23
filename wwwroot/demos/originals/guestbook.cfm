<!---
  guestbook.cfm - a 1999-style guestbook. Entries are stored in the Guestbook
  table of DSN "demos" (see kfroot/seed/demos.sql). Uses CFQUERY + CFQUERYPARAM,
  KoldFusion's hidden-field form validation (name_required), and paging with
  CFOUTPUT STARTROW/MAXROWS. KoldFusion Demo Gallery original - MIT licence.
--->
<cfparam name="URL.start" default="1">
<cfif NOT IsNumeric(URL.start) OR URL.start LT 1><cfset URL.start = 1></cfif>
<cfset perPage = 5>
<cfset thanks = false>

<cfif IsDefined("Form.signIt")>
	<cfparam name="Form.Email" default="">
	<cfparam name="Form.Homepage" default="">
	<cfparam name="Form.Location" default="">
	<cfparam name="Form.HeardFrom" default="">
	<cfset homepage = Trim(Form.Homepage)>
	<cfif homepage IS "http://"><cfset homepage = ""></cfif>
	<cfif Len(homepage) AND Left(homepage, 7) IS NOT "http://"><cfset homepage = "http://" & homepage></cfif>
	<cfquery datasource="demos">
		INSERT INTO Guestbook (Name, Email, Homepage, Location, HeardFrom, Comments, Posted)
		VALUES (
			<cfqueryparam value="#Left(Trim(Form.Name), 40)#" cfsqltype="CF_SQL_VARCHAR">,
			<cfqueryparam value="#Left(Trim(Form.Email), 60)#" cfsqltype="CF_SQL_VARCHAR">,
			<cfqueryparam value="#Left(homepage, 100)#" cfsqltype="CF_SQL_VARCHAR">,
			<cfqueryparam value="#Left(Trim(Form.Location), 40)#" cfsqltype="CF_SQL_VARCHAR">,
			<cfqueryparam value="#Left(Form.HeardFrom, 30)#" cfsqltype="CF_SQL_VARCHAR">,
			<cfqueryparam value="#Left(Trim(Form.Comments), 255)#" cfsqltype="CF_SQL_VARCHAR">,
			<cfqueryparam value="#Now()#" cfsqltype="CF_SQL_TIMESTAMP">
		)
	</cfquery>
	<cfset thanks = true>
	<cfset URL.start = 1>
</cfif>

<cfquery name="Entries" datasource="demos">
	SELECT EntryID, Name, Email, Homepage, Location, HeardFrom, Comments, Posted
	FROM Guestbook
	ORDER BY Posted DESC, EntryID DESC
</cfquery>

<html>
<head>
<title>Sign My Guestbook!</title>
</head>
<body background="/images/stars_bg.gif" bgcolor="#000033" text="#FFFFFF" link="#FFFF00" vlink="#FF99FF" alink="#FF0000">
<center>
<img src="/images/mailbox.gif" width="32" height="32" alt="">
<font face="Comic Sans MS, Arial" size="6" color="#FF66FF"><b>Sign My Guestbook!</b></font>
<img src="/images/mailbox.gif" width="32" height="32" alt=""><br>
<font face="Arial, Helvetica" size="2" color="#CCCCFF">Please sign my guestbook before you leave! I read every single entry. :-)</font>
<p>
<img src="/images/rainbow_hr.gif" width="500" height="6" alt="------">
<p>

<cfif thanks>
	<cfoutput>
	<table border="2" cellpadding="8" bordercolor="##FFFF00"><tr><td align="center">
	<font face="Arial, Helvetica" size="3" color="##FFFF00"><b>Thanks for signing, #HTMLEditFormat(Form.Name)#!</b></font><br>
	<font face="Arial, Helvetica" size="2">You are visitor ###Entries.RecordCount# to sign this guestbook.</font>
	</td></tr></table>
	</cfoutput>
	<p>
</cfif>

<!--- the entries --->
<font face="Arial, Helvetica" size="2" color="#CCCCFF">
<cfoutput>Showing entries #URL.start# - #Min(URL.start + perPage - 1, Entries.RecordCount)# of #Entries.RecordCount#</cfoutput>
</font>
<p>
<cfoutput query="Entries" startrow="#URL.start#" maxrows="#perPage#">
<table width="560" border="1" cellpadding="6" cellspacing="0" bordercolor="##6666CC" bgcolor="##000066">
<tr>
	<td bgcolor="##333399">
		<font face="Arial, Helvetica" size="2"><b>#HTMLEditFormat(Name)#</b>
		<cfif Len(Location)> from #HTMLEditFormat(Location)#</cfif></font>
	</td>
	<td bgcolor="##333399" align="right">
		<font face="Arial, Helvetica" size="1">#DateFormat(Posted, "mmmm d, yyyy")# at #TimeFormat(Posted, "h:mm tt")#</font>
	</td>
</tr>
<tr>
	<td colspan="2">
		<font face="Arial, Helvetica" size="2">#ParagraphFormat(HTMLEditFormat(Comments))#</font>
		<font face="Arial, Helvetica" size="1">
		<cfif Len(Email)><img src="/images/email.gif" width="40" height="30" align="absmiddle" alt="e-mail"> <a href="mailto:#HTMLEditFormat(Email)#">#HTMLEditFormat(Email)#</a> &nbsp;</cfif>
		<cfif Len(Homepage)><img src="/images/globe.gif" width="32" height="32" align="absmiddle" alt="homepage"> <a href="#HTMLEditFormat(Homepage)#">#HTMLEditFormat(Homepage)#</a> &nbsp;</cfif>
		<cfif Len(HeardFrom)><br>Found this site via: #HTMLEditFormat(HeardFrom)#</cfif>
		</font>
	</td>
</tr>
</table>
<br>
</cfoutput>

<font face="Arial, Helvetica" size="2">
<cfoutput>
<cfif URL.start GT 1><a href="guestbook.cfm?start=#Max(1, URL.start - perPage)#">&lt;&lt; Newer entries</a> &nbsp;</cfif>
<cfif URL.start + perPage LTE Entries.RecordCount><a href="guestbook.cfm?start=#URL.start + perPage#">Older entries &gt;&gt;</a></cfif>
</cfoutput>
</font>

<p>
<img src="/images/rainbow_hr.gif" width="500" height="6" alt="------">
<p>

<!--- the sign-in form, validated by KoldFusion's hidden _required fields --->
<form action="guestbook.cfm" method="post">
<input type="hidden" name="Name_required" value="Please tell me your name!">
<input type="hidden" name="Comments_required" value="You forgot to write a comment!">
<table border="0" cellpadding="3" bgcolor="#000066">
<tr><td colspan="2" align="center" bgcolor="#333399"><font face="Arial, Helvetica" size="3"><b>Sign the Guestbook</b></font></td></tr>
<tr><td align="right"><font face="Arial, Helvetica" size="2">Name:</font></td><td><input type="text" name="Name" size="30" maxlength="40"></td></tr>
<tr><td align="right"><font face="Arial, Helvetica" size="2">E-mail:</font></td><td><input type="text" name="Email" size="30" maxlength="60"></td></tr>
<tr><td align="right"><font face="Arial, Helvetica" size="2">Homepage:</font></td><td><input type="text" name="Homepage" size="40" maxlength="100" value="http://"></td></tr>
<tr><td align="right"><font face="Arial, Helvetica" size="2">Location:</font></td><td><input type="text" name="Location" size="30" maxlength="40"></td></tr>
<tr><td align="right"><font face="Arial, Helvetica" size="2">How did you find me?</font></td><td>
	<select name="HeardFrom">
		<option value="">-- pick one --
		<option>Webring
		<option>Search engine
		<option>Usenet
		<option>Friend
		<option>Just surfing
	</select></td></tr>
<tr><td align="right" valign="top"><font face="Arial, Helvetica" size="2">Comments:</font></td><td><textarea name="Comments" rows="5" cols="40" wrap="virtual"></textarea></td></tr>
<tr><td colspan="2" align="center"><input type="submit" name="signIt" value="Sign it!"> <input type="reset" value="Clear"></td></tr>
</table>
</form>
</center>
<cfinclude template="_footer.cfm">
</body>
</html>
