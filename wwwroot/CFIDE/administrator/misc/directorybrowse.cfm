<!--- Browse the Gibson Directory Server, one level at a time --->
<cfregistry action="get" branch="#Request.reg#\DirectoryServer" entry="BaseDN" variable="baseDN">
<cfparam name="URL.dn" default="#baseDN#">
<cfset msg = "">
<cfif IsDefined("Form.DeleteEntry")>
	<!--- deletes go through CFLDAP as the Directory Manager, like any other client --->
	<cfregistry action="get" branch="#Request.reg#\DirectoryServer" entry="AdminDN" variable="mgrDN">
	<cfregistry action="get" branch="#Request.reg#\DirectoryServer" entry="AdminPassword" variable="mgrPw">
	<cftry>
		<cfldap action="delete" server="#Server.Directory.Host#" port="#Server.Directory.Port#"
		        username="#mgrDN#" password="#KFUSION_DECRYPT(mgrPw)#" dn="#Form.dn#">
		<cfset msg = "The entry #HTMLEditFormat(Form.dn)# has been deleted.">
		<cfset URL.dn = Form.parent>
	<cfcatch type="Any"><cfset msg = cfcatch.Message></cfcatch>
	</cftry>
</cfif>
<cfset kids = KFUSION_DIRECTORYSERVER("children", URL.dn)>
<cfset attrs = KFUSION_DIRECTORYSERVER("entry", URL.dn)>
<cfset pageTitle = "Browse Directory">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<P>#Request.f#<B>Entry:</B> <FONT FACE="Courier New, Courier">
<!--- breadcrumbs from the base DN down --->
<cfset trail = "">
<cfset rest = URL.dn>
<cfset crumbs = ArrayNew(1)>
<cfloop condition="Len(rest)">
	<cfset ArrayPrepend(crumbs, rest)>
	<cfif CompareNoCase(Replace(rest, " ", "", "ALL"), Replace(baseDN, " ", "", "ALL")) EQ 0 OR NOT Find(",", rest)><cfbreak></cfif>
	<cfset rest = Trim(ListRest(rest))>
</cfloop>
<cfloop index="i" from="1" to="#ArrayLen(crumbs)#"><cfif i GT 1> &gt; </cfif><A HREF="directorybrowse.cfm?dn=#URLEncodedFormat(crumbs[i])#">#HTMLEditFormat(Trim(ListFirst(crumbs[i])))#</A></cfloop>
</FONT></FONT>
<cfif NOT attrs.RecordCount>
	<P>#Request.f#There is no entry with this distinguished name.</FONT>
<cfelse>
<P><TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="##669966"><TD WIDTH="30%"><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Attribute</B></FONT></TD><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Value</B></FONT></TD></TR>
<cfset last = "">
<cfloop query="attrs">
	<TR BGCOLOR="#IIf(attrs.CurrentRow MOD 2, DE('FFFFFF'), DE('FFFBF0'))#" VALIGN=TOP>
	<TD>#Request.f#<cfif attrs.Attribute NEQ last><B>#attrs.Attribute#</B></cfif></FONT></TD>
	<TD><FONT FACE="Courier New, Courier" SIZE=2>#HTMLEditFormat(attrs.Value)#</FONT></TD></TR>
	<cfset last = attrs.Attribute>
</cfloop>
</TABLE>
<cfif NOT kids.RecordCount>
	<FORM ACTION="directorybrowse.cfm" METHOD="POST" STYLE="margin:6px 0 0 0">
	<INPUT TYPE="hidden" NAME="dn" VALUE="#HTMLEditFormat(URL.dn)#"><INPUT TYPE="hidden" NAME="parent" VALUE="#HTMLEditFormat(Trim(ListRest(URL.dn)))#">
	<INPUT TYPE="submit" NAME="DeleteEntry" VALUE="Delete Entry" onClick="return confirm('Delete this entry from the directory?')">
	</FORM>
</cfif>
</cfif>
<P><TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="##669966"><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Entries below (#kids.RecordCount#)</B></FONT></TD>
<TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Object Class</B></FONT></TD><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Children</B></FONT></TD></TR>
<cfloop query="kids">
	<TR BGCOLOR="#IIf(kids.CurrentRow MOD 2, DE('FFFBF0'), DE('FFFFFF'))#">
	<TD>#Request.f#<IMG SRC="../images/#IIf(kids.Children, DE('folder'), DE('file'))#.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE BORDER=0>
	<B><A HREF="directorybrowse.cfm?dn=#URLEncodedFormat(kids.DN)#">#HTMLEditFormat(kids.RDN)#</A></B></FONT></TD>
	<TD>#Request.f##kids.ObjectClass#</FONT></TD><TD>#Request.f##kids.Children#</FONT></TD></TR>
</cfloop>
<cfif NOT kids.RecordCount><TR><TD COLSPAN=3>#Request.f#<I>This entry has no children.</I></FONT></TD></TR></cfif>
</TABLE>
<FORM><INPUT TYPE="button" VALUE="Back" onClick="location='directory.cfm'"></FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
