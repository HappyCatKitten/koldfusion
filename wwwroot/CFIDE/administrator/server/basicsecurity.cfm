<!--- Basic Server Security --->
<cfset tags = "CFCONTENT,CFDIRECTORY,CFFILE,CFOBJECT,CFREGISTRY,CFADMINSECURITY,CFEXECUTE">
<cfset msg = "">
<cfif IsDefined("Form.Apply")>
	<cfset problems = "">
	<cfif Len(Form.AdminPassword) AND Form.AdminPassword NEQ "********">
		<cfif Form.AdminPassword NEQ Form.AdminConfirm>
			<cfset problems = problems & "The Administrator password and its confirmation do not match. ">
		<cfelse>
			<cfset KFUSION_SETPASSWORD("Admin", Form.AdminPassword)>
		</cfif>
	</cfif>
	<cfif Len(Form.StudioPassword) AND Form.StudioPassword NEQ "********">
		<cfif Form.StudioPassword NEQ Form.StudioConfirm>
			<cfset problems = problems & "The Studio password and its confirmation do not match. ">
		<cfelse>
			<cfset KFUSION_SETPASSWORD("Studio", Form.StudioPassword)>
		</cfif>
	</cfif>
	<cfmodule template="../_tags/setreg.cfm" key="Server" entry="UseAdminPassword" value="#IIf(IsDefined('Form.UseAdminPassword'), 1, 0)#">
	<cfmodule template="../_tags/setreg.cfm" key="Server" entry="UseStudioPassword" value="#IIf(IsDefined('Form.UseStudioPassword'), 1, 0)#">
	<cfloop list="#tags#" index="tg">
		<cfmodule template="../_tags/setreg.cfm" key="Server\TagRestrictions" entry="#tg#" value="#IIf(IsDefined('Form.Tag_' & tg), 1, 0)#">
	</cfloop>
	<cfmodule template="../_tags/setreg.cfm" key="Server" entry="UnsecuredTagsDirectory" value="#Trim(Form.UnsecuredTagsDirectory)#">
	<cfif Len(problems)><cfset msg = problems><cfelse><cfset msg = "Basic security settings have been applied."></cfif>
	<!--- a new password invalidates the login cookie: issue a fresh one --->
	<cfregistry action="get" branch="#Request.reg#\Server" entry="AdminPassword" variable="newPw">
	<cfcookie name="CFADMIN_AUTH" value="#Hash(KFUSION_DECRYPT(newPw) & Request.reg)#">
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="Server" variable="S">
<cfmodule template="../_tags/getreg.cfm" key="Server\TagRestrictions" variable="T">
<cfset pageTitle = "Basic Server Security">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="basicsecurity.cfm" METHOD="POST">
<P>#Request.f#<INPUT TYPE="checkbox" NAME="UseAdminPassword" VALUE="1"<cfif S.UseAdminPassword EQ 1> CHECKED</cfif>>
<B>Use a KoldFusion Administration Password</B><BR>
The KoldFusion administrator should be restricted exclusively to trusted users. By default, an administrative password is required to
access these pages. If you configure your web server to restrict access to these pages you may opt to disable this administrative
password and rely on your web server's security instead. To change the KoldFusion administrator password, enter a new password and
confirm it below:</FONT>
<BLOCKQUOTE><TABLE BORDER=0>
<TR><TD>#Request.f#New Password</FONT></TD><TD><INPUT TYPE="password" NAME="AdminPassword" VALUE="********" SIZE=20></TD></TR>
<TR><TD>#Request.f#Confirmation</FONT></TD><TD><INPUT TYPE="password" NAME="AdminConfirm" VALUE="********" SIZE=20></TD></TR>
</TABLE></BLOCKQUOTE>

<P>#Request.f#<INPUT TYPE="checkbox" NAME="UseStudioPassword" VALUE="1"<cfif S.UseStudioPassword EQ 1> CHECKED</cfif>>
<B>Use a KoldFusion Studio Password</B><BR>
Access to KoldFusion servers via KoldFusion Studio should be restricted exclusively to trusted users. By default, a KoldFusion Studio
password is required to access a KoldFusion server. To change the KoldFusion Studio password, enter a new password and confirm it below:</FONT>
<BLOCKQUOTE><TABLE BORDER=0>
<TR><TD>#Request.f#New Password</FONT></TD><TD><INPUT TYPE="password" NAME="StudioPassword" VALUE="********" SIZE=20></TD></TR>
<TR><TD>#Request.f#Confirmation</FONT></TD><TD><INPUT TYPE="password" NAME="StudioConfirm" VALUE="********" SIZE=20></TD></TR>
</TABLE></BLOCKQUOTE>

<TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>Tag Restrictions</B></FONT></TD></TR></TABLE>
<P>#Request.f#Checked tags may be used by any template. Unchecked tags are disabled everywhere except in templates located in the
unsecured tags directory.</FONT>
<BLOCKQUOTE><TABLE BORDER=0 CELLPADDING=1>
<cfloop list="#tags#" index="tg">
<TR><TD><INPUT TYPE="checkbox" NAME="Tag_#tg#" VALUE="1"<cfif NOT StructKeyExists(T, tg) OR T[tg] EQ 1> CHECKED</cfif>></TD><TD>#Request.f#<TT>#tg#</TT></FONT></TD></TR>
</cfloop>
</TABLE></BLOCKQUOTE>
<P>#Request.f#<B>Unsecured Tags Directory</B><BR>
<INPUT TYPE="text" NAME="UnsecuredTagsDirectory" VALUE="#HTMLEditFormat(S.UnsecuredTagsDirectory)#" SIZE=50> <INPUT TYPE="button" VALUE="Browse Server..." onClick="browseServer('UnsecuredTagsDirectory')"><BR>
The only directory from which templates may use disabled tags. Enter a fully qualified path.</FONT>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Apply" VALUE="Apply"> <INPUT TYPE="reset" VALUE="Cancel">
</FORM>
<P>#Request.f#<I>Note: in true 1999 fashion these passwords are stored in the registry using the reversible CFMX_COMPAT
cipher with a fixed key. They are about as secret as a post-it note.</I></FONT>
</cfoutput>
<cfinclude template="../_footer.cfm">
