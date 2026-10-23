<!--- Mail Server Connection Settings --->
<cfset msg = "">
<cfif IsDefined("Form.Apply") OR IsDefined("Form.Verify")>
	<cfmodule template="../_tags/setreg.cfm" key="Mail" entry="Server" value="#Trim(Form.MailServer)#">
	<cfmodule template="../_tags/setreg.cfm" key="Mail" entry="Port" value="#Val(Form.Port)#">
	<cfmodule template="../_tags/setreg.cfm" key="Mail" entry="Timeout" value="#Val(Form.Timeout)#">
	<cfmodule template="../_tags/setreg.cfm" key="Mail" entry="SpoolInterval" value="#Max(1, Val(Form.SpoolInterval))#">
	<cfset msg = "Mail settings have been applied.">
	<cfif IsDefined("Form.Verify")><cfset v = KFUSION_VERIFYMAIL(Trim(Form.MailServer), Val(Form.Port), Val(Form.Timeout))><cfset msg = v.Message></cfif>
</cfif>
<cfif IsDefined("Form.Respool")><cfset n = KFUSION_RESPOOL()><cfset KFUSION_SPOOLNOW()><cfset msg = "#n# undeliverable messages were returned to the spool."></cfif>
<cfif IsDefined("Form.SpoolNow")><cfset KFUSION_SPOOLNOW()><cfset msg = "The mail spool has been processed."></cfif>
<cfmodule template="../_tags/getreg.cfm" key="Mail" variable="M">
<cfset spool = KFUSION_SPOOLLIST("spool")>
<cfset undel = KFUSION_SPOOLLIST("undelivr")>
<cfset pageTitle = "Mail Server Connection Settings">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="mail.cfm" METHOD="POST">
<P>#Request.f#<B>Mail Server</B><BR><INPUT TYPE="text" NAME="MailServer" VALUE="#HTMLEditFormat(M.Server)#" SIZE=40><BR>
Specify the server for sending dynamic SMTP mail messages. This can be an Internet address (e.g., mail.company.com) or the IP address
of the mail server (e.g., 127.0.0.1).</FONT>
<P>#Request.f#<B>Server Port</B><BR><INPUT TYPE="text" NAME="Port" VALUE="#M.Port#" SIZE=4><BR>
Accept the default port number for mail servers or enter a different one. Contact your server administrator if you are not sure which
port the mail server is running on.</FONT>
<P>#Request.f#<B>Connection Timeout</B> <INPUT TYPE="text" NAME="Timeout" VALUE="#M.Timeout#" SIZE=3> <B>seconds</B><BR>
The time KoldFusion should wait for a response from the mail server. This value may be important when optimizing performance with a
less reliable mail server.</FONT>
<P>#Request.f#<B>Spool Interval</B> <INPUT TYPE="text" NAME="SpoolInterval" VALUE="#M.SpoolInterval#" SIZE=3> <B>seconds</B><BR>
How often the mail spooler delivers messages waiting in the spool directory.</FONT>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Apply" VALUE="Apply"> <INPUT TYPE="submit" NAME="Verify" VALUE="Verify"> <INPUT TYPE="reset" VALUE="Cancel">
<P><TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>Mail Spool</B></FONT></TD></TR></TABLE>
<P>#Request.f##spool.RecordCount# message(s) waiting in the spool, #undel.RecordCount# in the undeliverable folder.
<INPUT TYPE="submit" NAME="SpoolNow" VALUE="Deliver Now"> <cfif undel.RecordCount><INPUT TYPE="submit" NAME="Respool" VALUE="Respool Undeliverable"></cfif></FONT>
<cfif undel.RecordCount>
<UL><cfloop query="undel" endrow="10"><LI>#Request.f##undel.Name# (#undel.Size# bytes, #DateFormat(undel.DateLastModified, "mm/dd/yy")# #TimeFormat(undel.DateLastModified, "HH:mm")#)</FONT></cfloop></UL>
</cfif>
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
