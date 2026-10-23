<!--- Employee Phone Directory: CFLDAP against the Gibson Directory Server.
      Anyone may search; Directory Administrators (Advanced Security context GibsonIntranet,
      LDAP group "Directory Administrators") may add, edit, rename and delete. --->
<cfset pageTitle = "Employee Phone Directory">
<cfset LDAP = StructNew()>
<cfset LDAP.server = Server.Directory.Host>
<cfset LDAP.port = Server.Directory.Port>
<cfset LDAP.base = Server.Directory.BaseDN>
<cfset LDAP.people = "ou=People, " & LDAP.base>
<cfset LDAP.groups = "ou=Groups, " & LDAP.base>
<cfparam name="URL.action" default="search">
<cfparam name="URL.q" default="">
<cfparam name="URL.dept" default="">
<cfparam name="URL.start" default="1">
<cfset msg = "">
<cfset err = "">

<!--- log in / out with CFAUTHENTICATE: the user directory is the LDAP directory itself --->
<cfif IsDefined("Form.Login")>
	<cfauthenticate securitycontext="GibsonIntranet" username="#Form.uid#" password="#Form.pw#" throwonfailure="no">
	<cfif CFAUTHENTICATE.AuthenticationStatus EQ "Success">
		<!--- writes bind as the user, so keep the password in the session (authentically 1999) --->
		<cfset Session.phoneUser = Form.uid>
		<cfset Session.phonePw = Form.pw>
		<cfset msg = "Welcome, #HTMLEditFormat(Form.uid)#.">
	<cfelse>
		<cfset err = "Login failed: unknown user or wrong password.">
	</cfif>
</cfif>
<cfif URL.action EQ "logout">
	<cfcookie name="CFAUTHORIZATION_GibsonIntranet" value="" expires="now">
	<cfset StructDelete(Session, "phoneUser")>
	<cfset StructDelete(Session, "phonePw")>
	<cfset msg = "You have been logged out.">
	<cfset URL.action = "search">
</cfif>
<cfset canEdit = IsDefined("Session.phoneUser") AND IsAuthenticated("GibsonIntranet") AND IsAuthorized("Application", "PhoneDirectory", "Edit")>
<cfif canEdit>
	<cfset LDAP.user = "uid=" & Session.phoneUser & "," & LDAP.people>
	<cfset LDAP.pw = Session.phonePw>
</cfif>

<!--- departments are the groups whose description says so --->
<cfldap action="query" name="depts" server="#LDAP.server#" port="#LDAP.port#" start="#LDAP.groups#" scope="onelevel"
        filter="(&(objectclass=groupOfUniqueNames)(description=The * department*))" attributes="cn" sort="cn">

<!--- changes --->
<cfif canEdit AND (IsDefined("Form.SaveEntry") OR IsDefined("Form.AddEntry"))>
	<cftry>
		<cfset uid = LCase(Trim(Form.uid))>
		<cfif NOT REFind("^[a-z][a-z0-9]*$", uid)><cfthrow message="The user ID must be letters and digits, starting with a letter."></cfif>
		<cfif NOT Len(Trim(Form.givenName)) OR NOT Len(Trim(Form.sn))><cfthrow message="First and last name are required."></cfif>
		<cfset dn = "uid=" & uid & "," & LDAP.people>
		<!--- values may contain commas ("Boston, MA"), so pairs are separated by ^ and values by | --->
		<cfset attrs = "cn=#Trim(Form.givenName)# #Trim(Form.sn)#^sn=#Trim(Form.sn)#^givenName=#Trim(Form.givenName)#^title=#Trim(Form.title)#^ou=#Form.ou#^telephoneNumber=#Trim(Form.telephoneNumber)#^mail=#Trim(Form.mail)#^l=#Trim(Form.l)#">
		<cfif IsDefined("Form.AddEntry")>
			<cfldap action="add" server="#LDAP.server#" port="#LDAP.port#" username="#LDAP.user#" password="#LDAP.pw#"
			        dn="#dn#" attributes="objectclass=top|person|organizationalPerson|inetOrgPerson^uid=#uid#^userPassword=#uid#^employeeType=Employee^#attrs#"
			        delimiter="^" separator="|">
			<cfldap action="modify" modifytype="add" server="#LDAP.server#" port="#LDAP.port#" username="#LDAP.user#" password="#LDAP.pw#"
			        dn="cn=#Form.ou#,#LDAP.groups#" attributes="uniqueMember=#dn#" separator="|">
			<cfset msg = "#HTMLEditFormat(Form.givenName)# #HTMLEditFormat(Form.sn)# has been added to the directory (password: #uid#).">
		<cfelse>
			<cfset olddn = "uid=" & Form.olduid & "," & LDAP.people>
			<!--- a new user ID renames the entry (ModifyDN) --->
			<cfif CompareNoCase(uid, Form.olduid)>
				<cfldap action="modifydn" server="#LDAP.server#" port="#LDAP.port#" username="#LDAP.user#" password="#LDAP.pw#"
				        dn="#olddn#" attributes="uid=#uid#">
			</cfif>
			<!--- empty fields delete the attribute: MODIFYTYPE="replace" with no value --->
			<cfldap action="modify" modifytype="replace" server="#LDAP.server#" port="#LDAP.port#" username="#LDAP.user#" password="#LDAP.pw#"
			        dn="#dn#" attributes="#attrs#" delimiter="^" separator="|">
			<!--- keep the department groups in step (there is no referential integrity plug-in in 1999) --->
			<cfldap action="query" name="mine" server="#LDAP.server#" port="#LDAP.port#" start="#LDAP.groups#"
			        filter="(uniqueMember=#olddn#)" attributes="cn">
			<cfloop query="mine">
				<cfif CompareNoCase(uid, Form.olduid) OR (ListFindNoCase(ValueList(depts.cn), mine.cn) AND mine.cn NEQ Form.ou)>
					<cfldap action="modify" modifytype="delete" server="#LDAP.server#" port="#LDAP.port#" username="#LDAP.user#" password="#LDAP.pw#"
					        dn="cn=#mine.cn#,#LDAP.groups#" attributes="uniqueMember=#olddn#" separator="|">
					<cfif CompareNoCase(uid, Form.olduid) AND (mine.cn EQ Form.ou OR NOT ListFindNoCase(ValueList(depts.cn), mine.cn))>
						<cfldap action="modify" modifytype="add" server="#LDAP.server#" port="#LDAP.port#" username="#LDAP.user#" password="#LDAP.pw#"
						        dn="cn=#mine.cn#,#LDAP.groups#" attributes="uniqueMember=#dn#" separator="|">
					</cfif>
				</cfif>
			</cfloop>
			<cfldap action="query" name="inDept" server="#LDAP.server#" port="#LDAP.port#" start="cn=#Form.ou#,#LDAP.groups#" scope="base"
			        filter="(uniqueMember=#dn#)" attributes="cn">
			<cfif NOT inDept.RecordCount>
				<cfldap action="modify" modifytype="add" server="#LDAP.server#" port="#LDAP.port#" username="#LDAP.user#" password="#LDAP.pw#"
				        dn="cn=#Form.ou#,#LDAP.groups#" attributes="uniqueMember=#dn#" separator="|">
			</cfif>
			<cfset msg = "The entry for #HTMLEditFormat(Form.givenName)# #HTMLEditFormat(Form.sn)# has been updated.">
		</cfif>
		<cfset URL.action = "search">
		<cfset URL.q = Trim(Form.sn)>
	<cfcatch type="Any">
		<cfset err = cfcatch.Message>
		<cfset URL.action = IIf(IsDefined("Form.AddEntry"), DE("add"), DE("edit"))>
		<cfset URL.uid = Form.olduid>
	</cfcatch>
	</cftry>
</cfif>
<cfif canEdit AND URL.action EQ "delete" AND IsDefined("URL.uid")>
	<cftry>
		<cfset dn = "uid=" & URL.uid & "," & LDAP.people>
		<cfldap action="query" name="mine" server="#LDAP.server#" port="#LDAP.port#" start="#LDAP.groups#" filter="(uniqueMember=#dn#)" attributes="cn">
		<cfloop query="mine">
			<cfldap action="modify" modifytype="delete" server="#LDAP.server#" port="#LDAP.port#" username="#LDAP.user#" password="#LDAP.pw#"
			        dn="cn=#mine.cn#,#LDAP.groups#" attributes="uniqueMember=#dn#" separator="|">
		</cfloop>
		<cfldap action="delete" server="#LDAP.server#" port="#LDAP.port#" username="#LDAP.user#" password="#LDAP.pw#" dn="#dn#">
		<cfset msg = "#HTMLEditFormat(URL.uid)# has been deleted from the directory.">
	<cfcatch type="Any"><cfset err = cfcatch.Message></cfcatch>
	</cftry>
	<cfset URL.action = "search">
</cfif>

<cfinclude template="_top.cfm">
<cfoutput>
<P>This phone book lives in the <B>Gibson Directory Server</B>, the LDAP directory that comes with KoldFusion
(<TT>ldap://#LDAP.server#:#LDAP.port#/#HTMLEditFormat(LDAP.base)#</TT>). The page reads and writes it with
<TT>CFLDAP</TT>, and logs you in with <TT>CFAUTHENTICATE</TT> against the same directory.</P>
<cfif Len(msg)><P><FONT COLOR="##006600"><B>#msg#</B></FONT></P></cfif>
<cfif Len(err)><P><FONT COLOR="##CC0000"><B>#HTMLEditFormat(err)#</B></FONT></P></cfif>

<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0><TR VALIGN=TOP><TD>
<FORM ACTION="phonebook.cfm" METHOD="GET">
<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 BGCOLOR="##FFFFCC"><TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>
<B>Name</B> <INPUT TYPE="text" NAME="q" VALUE="#HTMLEditFormat(URL.q)#" SIZE=16>
<B>Department</B> <SELECT NAME="dept"><OPTION VALUE="">(any)<cfloop query="depts"><OPTION<cfif depts.cn EQ URL.dept> SELECTED</cfif>>#depts.cn#</cfloop></SELECT>
<INPUT TYPE="submit" VALUE="Search">
</FONT></TD></TR></TABLE>
</FORM>
</TD><TD ALIGN=RIGHT>
<cfif canEdit>
	<FONT FACE="Arial, Helvetica" SIZE=2>Logged in as <B>#HTMLEditFormat(Session.phoneUser)#</B> (Directory Administrator)<BR>
	<A HREF="phonebook.cfm?action=add">Add an employee</A> | <A HREF="phonebook.cfm?action=logout">Log out</A></FONT>
<cfelse>
	<FORM ACTION="phonebook.cfm" METHOD="POST">
	<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 BGCOLOR="##CCFFCC"><TR><TD><FONT FACE="Arial, Helvetica" SIZE=1>
	User ID <INPUT TYPE="text" NAME="uid" SIZE=9> Password <INPUT TYPE="password" NAME="pw" SIZE=9>
	<INPUT TYPE="submit" NAME="Login" VALUE="Log in"><BR>
	Directory Administrators may edit the phone book. Try <B>hbrewster</B> / <B>hbrewster</B>.
	<cfif IsDefined("Session.phoneUser")><BR><FONT COLOR="##CC0000">#HTMLEditFormat(Session.phoneUser)# is not a Directory Administrator.</FONT></cfif>
	</FONT></TD></TR></TABLE>
	</FORM>
</cfif>
</TD></TR></TABLE>

<cfif (URL.action EQ "edit" OR URL.action EQ "add") AND canEdit>
	<cfset e = StructNew()>
	<cfloop list="uid,givenName,sn,title,ou,telephoneNumber,mail,l" index="f"><cfset e[f] = ""></cfloop>
	<cfif URL.action EQ "edit">
		<cftry>
			<cfldap action="query" name="one" server="#LDAP.server#" port="#LDAP.port#" start="uid=#URL.uid#,#LDAP.people#" scope="base"
			        attributes="uid,givenName,sn,title,ou,telephoneNumber,mail,l">
			<cfloop list="uid,givenName,sn,title,ou,telephoneNumber,mail,l" index="f"><cfset e[f] = one[f][1]></cfloop>
		<cfcatch type="Any"><P><FONT COLOR="##CC0000"><B>#HTMLEditFormat(cfcatch.Message)#</B></FONT></P></cfcatch>
		</cftry>
	</cfif>
	<cfif IsDefined("Form.uid")><cfloop list="uid,givenName,sn,title,ou,telephoneNumber,mail,l" index="f"><cfif IsDefined("Form." & f)><cfset e[f] = Form[f]></cfif></cfloop></cfif>
	<H3>#IIf(URL.action EQ "add", DE("Add an employee"), DE("Edit #HTMLEditFormat(e.givenName)# #HTMLEditFormat(e.sn)#"))#</H3>
	<FORM ACTION="phonebook.cfm" METHOD="POST">
	<INPUT TYPE="hidden" NAME="olduid" VALUE="#HTMLEditFormat(e.uid)#">
	<TABLE BORDER=0 CELLPADDING=3>
	<TR><TD><FONT FACE="Arial" SIZE=2>User ID (uid)</FONT></TD><TD><INPUT TYPE="text" NAME="uid" VALUE="#HTMLEditFormat(e.uid)#" SIZE=14>
		<cfif URL.action EQ "edit"><FONT SIZE=1>changing it renames the entry with ModifyDN</FONT></cfif></TD></TR>
	<TR><TD><FONT FACE="Arial" SIZE=2>First name</FONT></TD><TD><INPUT TYPE="text" NAME="givenName" VALUE="#HTMLEditFormat(e.givenName)#" SIZE=20></TD></TR>
	<TR><TD><FONT FACE="Arial" SIZE=2>Last name</FONT></TD><TD><INPUT TYPE="text" NAME="sn" VALUE="#HTMLEditFormat(e.sn)#" SIZE=20></TD></TR>
	<TR><TD><FONT FACE="Arial" SIZE=2>Title</FONT></TD><TD><INPUT TYPE="text" NAME="title" VALUE="#HTMLEditFormat(e.title)#" SIZE=30></TD></TR>
	<TR><TD><FONT FACE="Arial" SIZE=2>Department</FONT></TD><TD><SELECT NAME="ou"><cfloop query="depts"><OPTION<cfif depts.cn EQ e.ou> SELECTED</cfif>>#depts.cn#</cfloop></SELECT></TD></TR>
	<TR><TD><FONT FACE="Arial" SIZE=2>Phone</FONT></TD><TD><INPUT TYPE="text" NAME="telephoneNumber" VALUE="#HTMLEditFormat(e.telephoneNumber)#" SIZE=16></TD></TR>
	<TR><TD><FONT FACE="Arial" SIZE=2>E-mail</FONT></TD><TD><INPUT TYPE="text" NAME="mail" VALUE="#HTMLEditFormat(e.mail)#" SIZE=30></TD></TR>
	<TR><TD><FONT FACE="Arial" SIZE=2>Location</FONT></TD><TD><INPUT TYPE="text" NAME="l" VALUE="#HTMLEditFormat(e.l)#" SIZE=20></TD></TR>
	</TABLE>
	<cfif URL.action EQ "add"><INPUT TYPE="submit" NAME="AddEntry" VALUE="Add to Directory"><cfelse><INPUT TYPE="submit" NAME="SaveEntry" VALUE="Save Changes"></cfif>
	<INPUT TYPE="button" VALUE="Cancel" onClick="location='phonebook.cfm'">
	</FORM>
<cfelse>
	<!--- search: user input is escaped for the filter (RFC 2254 \2a \28 \29 \5c) --->
	<cfset term = Replace(Replace(Replace(Replace(Trim(URL.q), "\", "\5c", "ALL"), "*", "\2a", "ALL"), "(", "\28", "ALL"), ")", "\29", "ALL")>
	<cfset filter = "(objectclass=inetOrgPerson)">
	<cfif Len(term)><cfset filter = filter & "(|(cn=*#term#*)(sn=#term#*)(givenName=#term#*)(telephoneNumber=*#term#))"></cfif>
	<cfif Len(URL.dept)><cfset filter = filter & "(ou=#Replace(Replace(Replace(URL.dept, "*", "\2a", "ALL"), "(", "\28", "ALL"), ")", "\29", "ALL")#)"></cfif>
	<cfset filter = "(&" & filter & ")">
	<cfset pageSize = 10>
	<cfif NOT IsNumeric(URL.start) OR URL.start LT 1><cfset URL.start = 1></cfif>
	<cfldap action="query" name="people" server="#LDAP.server#" port="#LDAP.port#" start="#LDAP.people#" scope="onelevel"
	        filter="#filter#" attributes="uid,cn,title,ou,telephoneNumber,mail" sort="sn,givenName" sortcontrol="nocase">
	<P><FONT SIZE=1>Filter: <TT>#HTMLEditFormat(filter)#</TT> - #people.RecordCount# match(es)</FONT></P>
	<TABLE BORDER=1 CELLPADDING=4 CELLSPACING=0 WIDTH="100%">
	<TR BGCOLOR="##000066"><cfloop list="Name,Title,Department,Phone,E-mail" index="h"><TH ALIGN=LEFT><FONT FACE="Arial" SIZE=2 COLOR="##66FF66">#h#</FONT></TH></cfloop><cfif canEdit><TH></TH></cfif></TR>
	<cfloop query="people" startrow="#URL.start#" endrow="#URL.start + pageSize - 1#">
		<TR BGCOLOR="#IIf(people.CurrentRow MOD 2, DE('FFFFFF'), DE('EEEEFF'))#">
		<TD><FONT FACE="Arial" SIZE=2><B>#people.cn#</B></FONT></TD><TD><FONT FACE="Arial" SIZE=2>#people.title#</FONT></TD>
		<TD><FONT FACE="Arial" SIZE=2>#people.ou#</FONT></TD><TD NOWRAP><FONT FACE="Arial" SIZE=2>#people.telephoneNumber#</FONT></TD>
		<TD><FONT FACE="Arial" SIZE=2><A HREF="mailto:#people.mail#">#people.mail#</A></FONT></TD>
		<cfif canEdit><TD NOWRAP><FONT FACE="Arial" SIZE=1><A HREF="phonebook.cfm?action=edit&uid=#URLEncodedFormat(people.uid)#">Edit</A> |
			<A HREF="phonebook.cfm?action=delete&uid=#URLEncodedFormat(people.uid)#" onClick="return confirm('Delete #JSStringFormat(people.cn)# from the directory?')">Delete</A></FONT></TD></cfif>
		</TR>
	</cfloop>
	<cfif NOT people.RecordCount><TR><TD COLSPAN=6><FONT FACE="Arial" SIZE=2><I>Nobody by that name works here.</I></FONT></TD></TR></cfif>
	</TABLE>
	<P><FONT SIZE=2>
	<cfif URL.start GT 1><A HREF="phonebook.cfm?q=#URLEncodedFormat(URL.q)#&dept=#URLEncodedFormat(URL.dept)#&start=#Max(1, URL.start - pageSize)#">&lt;&lt; Previous #pageSize#</A></cfif>
	<cfif URL.start + pageSize LTE people.RecordCount><A HREF="phonebook.cfm?q=#URLEncodedFormat(URL.q)#&dept=#URLEncodedFormat(URL.dept)#&start=#URL.start + pageSize#">Next #pageSize# &gt;&gt;</A></cfif>
	</FONT></P>
</cfif>
<P><FONT SIZE=1>Try it from a shell, too: <TT>ldapsearch -x -H ldap://#LDAP.server#:#LDAP.port# -b "#HTMLEditFormat(LDAP.people)#" "(sn=O*)" cn telephoneNumber</TT></FONT></P>
</cfoutput>
<cfinclude template="_bottom.cfm">
