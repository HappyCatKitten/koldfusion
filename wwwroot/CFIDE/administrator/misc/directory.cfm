<!--- Gibson Directory Server: the LDAP directory bundled with KoldFusion --->
<cfset msg = "">
<cfmodule template="../_tags/getreg.cfm" key="DirectoryServer" variable="D">
<cfif IsDefined("Form.Apply")>
	<cfset problems = "">
	<cfif NOT IsNumeric(Form.Port) OR Form.Port LT 1 OR Form.Port GT 65535>
		<cfset problems = problems & "The server port must be a number between 1 and 65535. ">
	</cfif>
	<cfif NOT Len(Trim(Form.BaseDN)) OR NOT Find("=", Form.BaseDN)>
		<cfset problems = problems & "The base DN must be a distinguished name such as o=Gibson Mainframe Co, c=US. ">
	</cfif>
	<cfif NOT Len(Trim(Form.AdminDN)) OR NOT Find("=", Form.AdminDN)>
		<cfset problems = problems & "The Directory Manager DN must be a distinguished name such as cn=Directory Manager. ">
	</cfif>
	<cfif Form.AdminPassword NEQ "********" AND Form.AdminPassword NEQ Form.AdminConfirm>
		<cfset problems = problems & "The Directory Manager password and its confirmation do not match. ">
	</cfif>
	<cfif Len(problems)>
		<cfset msg = problems>
	<cfelse>
		<!--- the built-in user directory follows the server to its new port --->
		<cfset udKey = Request.reg & "\Security\UserDirectories\Gibson Directory">
		<cfregistry action="getall" branch="#Request.reg#\Security\UserDirectories" name="udirs" type="key">
		<cfif ListFindNoCase(ValueList(udirs.Entry), "Gibson Directory")>
			<cfregistry action="get" branch="#udKey#" entry="Location" variable="udLoc">
			<cfif udLoc EQ "127.0.0.1:#D.Port#" OR udLoc EQ "localhost:#D.Port#">
				<cfregistry action="set" branch="#udKey#" entry="Location" value="127.0.0.1:#Val(Form.Port)#">
			</cfif>
		</cfif>
		<cfmodule template="../_tags/setreg.cfm" key="DirectoryServer" entry="Enabled" value="#IIf(IsDefined('Form.Enabled'), 1, 0)#">
		<cfmodule template="../_tags/setreg.cfm" key="DirectoryServer" entry="Port" value="#Val(Form.Port)#">
		<cfmodule template="../_tags/setreg.cfm" key="DirectoryServer" entry="BindAddress" value="#Trim(Form.BindAddress)#">
		<cfmodule template="../_tags/setreg.cfm" key="DirectoryServer" entry="BaseDN" value="#Trim(Form.BaseDN)#">
		<cfmodule template="../_tags/setreg.cfm" key="DirectoryServer" entry="AdminDN" value="#Trim(Form.AdminDN)#">
		<cfif Form.AdminPassword NEQ "********">
			<cfmodule template="../_tags/setreg.cfm" key="DirectoryServer" entry="AdminPassword" value="#KFUSION_ENCRYPT(Form.AdminPassword)#">
		</cfif>
		<cfmodule template="../_tags/setreg.cfm" key="DirectoryServer" entry="SizeLimit" value="#Val(Form.SizeLimit)#">
		<cfmodule template="../_tags/setreg.cfm" key="DirectoryServer" entry="AllowAnonymous" value="#IIf(IsDefined('Form.AllowAnonymous'), 1, 0)#">
		<cfmodule template="../_tags/setreg.cfm" key="DirectoryServer" entry="PasswordStorage" value="#Form.PasswordStorage#">
		<cfmodule template="../_tags/setreg.cfm" key="DirectoryServer" entry="LogAccess" value="#IIf(IsDefined('Form.LogAccess'), 1, 0)#">
		<cfmodule template="../_tags/setreg.cfm" key="DirectoryServer" entry="LDIFFile" value="#Trim(Form.LDIFFile)#">
		<cfset st = KFUSION_DIRECTORYSERVER("restart")>
		<cfset msg = "Directory server settings have been applied. " & st.Message>
	</cfif>
</cfif>
<cfif IsDefined("Form.StopServer")><cfset st = KFUSION_DIRECTORYSERVER("stop")><cfset msg = st.Message></cfif>
<cfif IsDefined("Form.StartServer")><cfset st = KFUSION_DIRECTORYSERVER("start")><cfset msg = st.Message></cfif>
<cfif IsDefined("Form.Reload")><cfset st = KFUSION_DIRECTORYSERVER("reload")><cfset msg = st.Message></cfif>
<cfif IsDefined("Form.Reseed")><cfset st = KFUSION_DIRECTORYSERVER("reseed")><cfset msg = st.Message></cfif>
<cfmodule template="../_tags/getreg.cfm" key="DirectoryServer" variable="D">
<cfset st = KFUSION_DIRECTORYSERVER("status")>
<cfset pageTitle = "Gibson Directory Server">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="directory.cfm" METHOD="POST">
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>Server Status</B></FONT></TD></TR></TABLE>
<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR><TD>#Request.f#<B>Status</B></FONT></TD><TD>#Request.f#<cfif st.Running><FONT COLOR="##006600"><B>Running</B></FONT> since #DateFormat(st.StartedAt, "mmm d, yyyy")# #TimeFormat(st.StartedAt, "h:mm tt")#<cfelse><FONT COLOR="##CC0000"><B>Stopped</B></FONT></cfif></FONT></TD></TR>
<TR><TD>#Request.f#<B>LDAP URL</B></FONT></TD><TD><FONT FACE="Courier New, Courier" SIZE=2>ldap://#st.BindAddress#:#st.Port#/#HTMLEditFormat(st.BaseDN)#</FONT></TD></TR>
<TR><TD>#Request.f#<B>Product</B></FONT></TD><TD>#Request.f##st.Product# (LDAP version 3)</FONT></TD></TR>
<TR><TD>#Request.f#<B>Entries</B></FONT></TD><TD>#Request.f##st.Entries# &nbsp; <A HREF="directorybrowse.cfm">Browse Directory...</A></FONT></TD></TR>
<TR><TD>#Request.f#<B>Activity</B></FONT></TD><TD>#Request.f##st.Connections# open connection(s), #st.Operations# operation(s) since the server started</FONT></TD></TR>
<TR><TD>#Request.f#<B>Database</B></FONT></TD><TD><FONT FACE="Courier New, Courier" SIZE=2>#HTMLEditFormat(st.LDIFFile)#</FONT></TD></TR>
</TABLE>
<P><cfif st.Running><INPUT TYPE="submit" NAME="StopServer" VALUE="Stop Server"><cfelse><INPUT TYPE="submit" NAME="StartServer" VALUE="Start Server"></cfif>
<INPUT TYPE="submit" NAME="Reload" VALUE="Reload LDIF">
<INPUT TYPE="submit" NAME="Reseed" VALUE="Restore Sample Directory" onClick="return confirm('Replace every entry in the directory with the sample Gibson Mainframe Co. directory?')">

<P><TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>Server Settings</B></FONT></TD></TR></TABLE>
<P>#Request.f#<INPUT TYPE="checkbox" NAME="Enabled" VALUE="1"<cfif D.Enabled EQ 1> CHECKED</cfif>>
<B>Enable the Gibson Directory Server</B><BR>
Starts the bundled LDAP directory together with the KoldFusion Application Server, so that CFLDAP and LDAP user directories
(Advanced Security) have a directory to talk to. Any LDAPv3 client can use it, too.</FONT>
<P>#Request.f#<B>Server Port</B><BR><INPUT TYPE="text" NAME="Port" VALUE="#D.Port#" SIZE=6><BR>
The TCP port the directory listens on. LDAP servers normally use port 389; the Gibson Directory Server uses 3890 so that it does
not need to run as root. Use this port in the PORT attribute of CFLDAP.</FONT>
<P>#Request.f#<B>Bind Address</B><BR><INPUT TYPE="text" NAME="BindAddress" VALUE="#HTMLEditFormat(D.BindAddress)#" SIZE=16><BR>
The network address to listen on. Leave this at 127.0.0.1: the directory holds password hashes and its access control is as trusting
as everything else in 1999.</FONT>
<P>#Request.f#<B>Base DN (Directory Suffix)</B><BR><INPUT TYPE="text" NAME="BaseDN" VALUE="#HTMLEditFormat(D.BaseDN)#" SIZE=40><BR>
The root of the directory tree, for example <TT>o=Gibson Mainframe Co, c=US</TT> or <TT>dc=gibson, dc=com</TT>. The sample entries
are created below it when the directory is first built.</FONT>
<P>#Request.f#<B>Directory Manager DN</B><BR><INPUT TYPE="text" NAME="AdminDN" VALUE="#HTMLEditFormat(D.AdminDN)#" SIZE=40><BR>
The privileged user that may read and change every entry. Members of the group <TT>cn=Directory Administrators,ou=Groups</TT>
may also change entries, and every user may change his or her own entry.</FONT>
<BLOCKQUOTE><TABLE BORDER=0>
<TR><TD>#Request.f#Directory Manager Password</FONT></TD><TD><INPUT TYPE="password" NAME="AdminPassword" VALUE="********" SIZE=20></TD></TR>
<TR><TD>#Request.f#Confirmation</FONT></TD><TD><INPUT TYPE="password" NAME="AdminConfirm" VALUE="********" SIZE=20></TD></TR>
</TABLE></BLOCKQUOTE>
<P>#Request.f#<B>Size Limit</B> <INPUT TYPE="text" NAME="SizeLimit" VALUE="#D.SizeLimit#" SIZE=5> <B>entries</B><BR>
The most entries a single search returns (the Directory Manager is not limited). 0 means no limit.</FONT>
<P>#Request.f#<INPUT TYPE="checkbox" NAME="AllowAnonymous" VALUE="1"<cfif D.AllowAnonymous EQ 1> CHECKED</cfif>>
<B>Allow anonymous read access</B><BR>
Lets clients that do not bind search the directory, as a company phone book should. Password attributes are never shown to them.</FONT>
<P>#Request.f#<B>Password Storage Scheme</B><BR>
<SELECT NAME="PasswordStorage"><OPTION VALUE="SHA"<cfif D.PasswordStorage EQ "SHA"> SELECTED</cfif>>SHA (Secure Hash Algorithm)<OPTION VALUE="CLEAR"<cfif D.PasswordStorage EQ "CLEAR"> SELECTED</cfif>>Clear text</SELECT><BR>
How new userPassword values are stored. Existing values keep their scheme.</FONT>
<P>#Request.f#<INPUT TYPE="checkbox" NAME="LogAccess" VALUE="1"<cfif D.LogAccess EQ 1> CHECKED</cfif>>
<B>Log directory access</B><BR>
Records every connection and operation in <TT>directory.log</TT> (see Log Files).</FONT>
<P>#Request.f#<B>LDIF Database File</B><BR><INPUT TYPE="text" NAME="LDIFFile" VALUE="#HTMLEditFormat(D.LDIFFile)#" SIZE=60><BR>
The directory is kept in memory and written to this LDIF file after every change. If the file does not exist the sample directory
is created.</FONT>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Apply" VALUE="Apply"> <INPUT TYPE="reset" VALUE="Cancel">
<FONT FACE="Arial, Helvetica" SIZE=1>Applying restarts the directory server.</FONT>
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
