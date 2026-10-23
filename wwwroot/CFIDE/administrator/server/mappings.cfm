<!--- Mappings --->
<cfset base = Request.reg & "\Mappings">
<cfset msg = "">
<cfparam name="Form.LogicalPath" default="/">
<cfparam name="Form.DirectoryPath" default="">
<cfparam name="URL.edit" default="">
<cfif IsDefined("Form.AddMapping")>
	<cfset lp = Trim(Form.LogicalPath)>
	<cfif Left(lp, 1) NEQ "/"><cfset lp = "/" & lp></cfif>
	<cfif lp EQ "/" OR NOT Len(Trim(Form.DirectoryPath))>
		<cfset msg = "Enter a logical path other than / and a directory path.">
	<cfelseif NOT DirectoryExists(Trim(Form.DirectoryPath))>
		<cfset msg = "The directory #HTMLEditFormat(Form.DirectoryPath)# does not exist on the server.">
	<cfelse>
		<cfif Len(Form.OldPath) AND Form.OldPath NEQ lp><cfregistry action="delete" branch="#base#" entry="#Form.OldPath#"></cfif>
		<cfregistry action="set" branch="#base#" entry="#lp#" value="#Trim(Form.DirectoryPath)#">
		<cfset msg = "The mapping #lp# has been saved.">
		<cfset Form.LogicalPath = "/"><cfset Form.DirectoryPath = "">
	</cfif>
</cfif>
<cfif IsDefined("Form.DeleteMapping") AND Len(Form.OldPath)>
	<cfregistry action="delete" branch="#base#" entry="#Form.OldPath#">
	<cfset msg = "The mapping #Form.OldPath# has been deleted.">
</cfif>
<cfregistry action="getall" branch="#base#" name="maps" type="string" sort="Entry ASC">
<cfset oldPath = "">
<cfif Len(URL.edit)>
	<cfloop query="maps"><cfif maps.Entry EQ URL.edit><cfset Form.LogicalPath = maps.Entry><cfset Form.DirectoryPath = maps.Value><cfset oldPath = maps.Entry></cfif></cfloop>
</cfif>
<cfset pageTitle = IIf(Len(oldPath), DE("Edit Mapping"), DE("Add New Mapping"))>
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="mappings.cfm" METHOD="POST"><INPUT TYPE="hidden" NAME="OldPath" VALUE="#HTMLEditFormat(oldPath)#">
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD>#Request.f#<B>Logical Path</B></FONT></TD><TD><INPUT TYPE="text" NAME="LogicalPath" VALUE="#HTMLEditFormat(Form.LogicalPath)#" SIZE=30></TD>
	<TD>#Request.f#Type in an alias for the directory path specified below (e.g. /images/).</FONT></TD></TR>
<TR><TD>#Request.f#<B>Directory Path</B></FONT></TD><TD><INPUT TYPE="text" NAME="DirectoryPath" VALUE="#HTMLEditFormat(Form.DirectoryPath)#" SIZE=30></TD>
	<TD><INPUT TYPE="button" VALUE="Browse Server..." onClick="browseServer('DirectoryPath')"></TD></TR>
</TABLE>
<P>#Request.f#Enter the directory path for the alias or click <B>Browse Server</B> to select a directory. Click <B>Add Mapping</B> to complete
the process. To change or delete a logical path, select it from the list below.</FONT>
<P><INPUT TYPE="submit" NAME="AddMapping" VALUE="#IIf(Len(oldPath), DE('Update Mapping'), DE('Add Mapping'))#">
<cfif Len(oldPath)><INPUT TYPE="submit" NAME="DeleteMapping" VALUE="Delete"></cfif>
<INPUT TYPE="button" VALUE="Cancel" onClick="location='mappings.cfm'">
</FORM>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="##669966"><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Logical Path</B></FONT></TD><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Directory Path</B></FONT></TD></TR>
<TR BGCOLOR="##FFFFFF"><TD>#Request.f#<B>/</B></FONT></TD><TD>#Request.f#<TT>#KFUSION_SERVERINFO().WebRoot#/</TT></FONT></TD></TR>
<cfloop query="maps">
<TR BGCOLOR="#IIf(maps.CurrentRow MOD 2, DE('FFFBF0'), DE('FFFFFF'))#"><TD>#Request.f#<B><A HREF="mappings.cfm?edit=#URLEncodedFormat(maps.Entry)#">#maps.Entry#</A></B></FONT></TD>
<TD>#Request.f#<A HREF="mappings.cfm?edit=#URLEncodedFormat(maps.Entry)#"><TT>#maps.Value#</TT></A></FONT></TD></TR>
</cfloop>
</TABLE>
</cfoutput>
<cfinclude template="../_footer.cfm">
