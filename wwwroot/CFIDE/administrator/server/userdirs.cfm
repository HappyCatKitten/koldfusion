<!--- User Directories and their users --->
<cfset base = Request.reg & "\Security\UserDirectories">
<cfset msg = "">
<cfif IsDefined("Form.AddDir") AND Len(Trim(Form.DirName))>
	<cfset k = base & "\" & Trim(Form.DirName)>
	<cfregistry action="set" branch="#k#" entry="Namespace" value="#Form.Namespace#">
	<cfregistry action="set" branch="#k#" entry="Location" value="#Form.Location#">
	<cfregistry action="set" branch="#k#" entry="Description" value="#Form.Description#">
	<cfset msg = "The user directory #Trim(Form.DirName)# has been added.">
</cfif>
<cfif IsDefined("URL.deletedir")>
	<cfregistry action="delete" branch="#base#\#URL.deletedir#">
	<cfset msg = "The user directory #URL.deletedir# has been deleted.">
</cfif>
<cfif IsDefined("Form.AddUser") AND Len(Trim(Form.UserName))>
	<cfset k = base & "\" & Form.Dir & "\Users\" & Trim(Form.UserName)>
	<cfregistry action="set" branch="#k#" entry="Password" value="#KFUSION_ENCRYPT(Form.UserPassword)#">
	<cfregistry action="set" branch="#k#" entry="FullName" value="#Form.FullName#">
	<cfset msg = "The user #Trim(Form.UserName)# has been added to #Form.Dir#.">
</cfif>
<cfif IsDefined("URL.deleteuser")>
	<cfregistry action="delete" branch="#base#\#URL.dir#\Users\#URL.deleteuser#">
	<cfset msg = "The user #URL.deleteuser# has been removed.">
</cfif>
<cfregistry action="getall" branch="#base#" name="dirs" type="key">
<cfset pageTitle = "User Directories">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<P>#Request.f#A user directory is a store of user names and passwords that security contexts authenticate against.
KoldFusion keeps users in its own registry directory; the LDAP and Windows NT namespaces are listed for nostalgia.</FONT>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="##669966"><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Name</B></FONT></TD><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Namespace</B></FONT></TD>
<TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Users</B></FONT></TD><TD></TD></TR>
<cfloop query="dirs">
	<cfregistry action="get" branch="#base#\#dirs.Entry#" entry="Namespace" variable="ns">
	<cfregistry action="getall" branch="#base#\#dirs.Entry#\Users" name="users" type="key">
	<TR BGCOLOR="#IIf(dirs.CurrentRow MOD 2, DE('FFFFFF'), DE('FFFBF0'))#" VALIGN=TOP>
	<TD>#Request.f#<B>#dirs.Entry#</B></FONT></TD><TD>#Request.f##ns#</FONT></TD>
	<TD>#Request.f#<cfloop query="users">#users.Entry# <A HREF="userdirs.cfm?dir=#URLEncodedFormat(dirs.Entry)#&deleteuser=#URLEncodedFormat(users.Entry)#">[remove]</A><BR></cfloop>
	<FORM ACTION="userdirs.cfm" METHOD="POST" STYLE="margin:0"><INPUT TYPE="hidden" NAME="Dir" VALUE="#dirs.Entry#">
	User <INPUT TYPE="text" NAME="UserName" SIZE=10> Password <INPUT TYPE="password" NAME="UserPassword" SIZE=10>
	Full name <INPUT TYPE="text" NAME="FullName" SIZE=14> <INPUT TYPE="submit" NAME="AddUser" VALUE="Add User"></FORM></FONT></TD>
	<TD>#Request.f#<A HREF="userdirs.cfm?deletedir=#URLEncodedFormat(dirs.Entry)#" onClick="return confirm('Delete this user directory?')">Delete</A></FONT></TD></TR>
</cfloop>
</TABLE>
<P><TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>New User Directory</B></FONT></TD></TR></TABLE>
<FORM ACTION="userdirs.cfm" METHOD="POST">
<TABLE BORDER=0 CELLPADDING=2>
<TR><TD>#Request.f#Name</FONT></TD><TD><INPUT TYPE="text" NAME="DirName" SIZE=20></TD></TR>
<TR><TD>#Request.f#Namespace</FONT></TD><TD><SELECT NAME="Namespace"><OPTION>KoldFusion Registry<OPTION>LDAP<OPTION>Windows NT<OPTION>ODBC</SELECT></TD></TR>
<TR><TD>#Request.f#Location</FONT></TD><TD><INPUT TYPE="text" NAME="Location" VALUE="localhost" SIZE=30></TD></TR>
<TR><TD>#Request.f#Description</FONT></TD><TD><INPUT TYPE="text" NAME="Description" SIZE=40></TD></TR>
</TABLE>
<INPUT TYPE="submit" NAME="AddDir" VALUE="Add"> <INPUT TYPE="button" VALUE="Back" onClick="location='advancedsecurity.cfm'">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
