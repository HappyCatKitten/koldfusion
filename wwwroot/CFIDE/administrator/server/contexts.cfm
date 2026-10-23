<!--- Security Contexts, Rules and Policies --->
<cfset base = Request.reg & "\Security\Contexts">
<cfset msg = "">
<cfif IsDefined("Form.AddContext") AND Len(Trim(Form.ContextName))>
	<cfregistry action="set" branch="#base#\#Trim(Form.ContextName)#" entry="Description" value="#Form.Description#">
	<cfregistry action="set" branch="#base#\#Trim(Form.ContextName)#" entry="UserDirectories" value="#IIf(IsDefined('Form.UserDirectories'), 'Form.UserDirectories', DE(''))#">
	<cfset msg = "The security context #Trim(Form.ContextName)# has been created.">
</cfif>
<cfif IsDefined("URL.deletecontext")>
	<cfregistry action="delete" branch="#base#\#URL.deletecontext#">
	<cfset msg = "The security context #URL.deletecontext# has been deleted.">
</cfif>
<cfif IsDefined("Form.AddRule") AND Len(Trim(Form.RuleName))>
	<cfset k = "#base#\#Form.Context#\Rules\#Trim(Form.RuleName)#">
	<cfregistry action="set" branch="#k#" entry="ResourceType" value="#Form.ResourceType#">
	<cfregistry action="set" branch="#k#" entry="Resource" value="#Form.Resource#">
	<cfregistry action="set" branch="#k#" entry="Actions" value="#Form.Actions#">
	<cfset msg = "Rule #Trim(Form.RuleName)# added.">
</cfif>
<cfif IsDefined("Form.AddPolicy") AND Len(Trim(Form.PolicyName))>
	<cfset k = "#base#\#Form.Context#\Policies\#Trim(Form.PolicyName)#">
	<cfregistry action="set" branch="#k#" entry="Rules" value="#IIf(IsDefined('Form.PolicyRules'), 'Form.PolicyRules', DE(''))#">
	<cfregistry action="set" branch="#k#" entry="Users" value="#Form.PolicyUsers#">
	<cfset msg = "Policy #Trim(Form.PolicyName)# added.">
</cfif>
<cfif IsDefined("URL.deleterule")><cfregistry action="delete" branch="#base#\#URL.context#\Rules\#URL.deleterule#"><cfset msg = "Rule removed."></cfif>
<cfif IsDefined("URL.deletepolicy")><cfregistry action="delete" branch="#base#\#URL.context#\Policies\#URL.deletepolicy#"><cfset msg = "Policy removed."></cfif>
<cfregistry action="getall" branch="#base#" name="ctxs" type="key">
<cfregistry action="getall" branch="#Request.reg#\Security\UserDirectories" name="dirs" type="key">
<cfset pageTitle = "Security Contexts">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<P>#Request.f#A security context groups user directories with the rules (what may be done to which resource) and policies
(which users get which rules) that applications check with IsAuthorized().</FONT>
<cfloop query="ctxs">
	<cfset cname = ctxs.Entry>
	<cfregistry action="get" branch="#base#\#cname#" entry="Description" variable="desc">
	<cfregistry action="get" branch="#base#\#cname#" entry="UserDirectories" variable="udirs">
	<cfregistry action="getall" branch="#base#\#cname#\Rules" name="rules" type="key">
	<cfregistry action="getall" branch="#base#\#cname#\Policies" name="pols" type="key">
	<P><TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
	<TR BGCOLOR="##669966"><TD COLSPAN=2><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>#cname#</B> - #desc# (user directories: #udirs#)</FONT>
	&nbsp;<FONT FACE="Arial" SIZE=1><A HREF="contexts.cfm?deletecontext=#URLEncodedFormat(cname)#" STYLE="color:white" onClick="return confirm('Delete context?')">[delete]</A></FONT></TD></TR>
	<TR VALIGN=TOP><TD WIDTH="50%" BGCOLOR="##FFFBF0">#Request.f#<B>Rules</B><BR>
	<cfloop query="rules">
		<cfregistry action="get" branch="#base#\#cname#\Rules\#rules.Entry#" entry="ResourceType" variable="rt">
		<cfregistry action="get" branch="#base#\#cname#\Rules\#rules.Entry#" entry="Resource" variable="rr">
		<cfregistry action="get" branch="#base#\#cname#\Rules\#rules.Entry#" entry="Actions" variable="ra">
		<TT>#rules.Entry#</TT>: #rt# <I>#rr#</I> [#ra#] <A HREF="contexts.cfm?context=#URLEncodedFormat(cname)#&deleterule=#URLEncodedFormat(rules.Entry)#">x</A><BR>
	</cfloop>
	<FORM ACTION="contexts.cfm" METHOD="POST" STYLE="margin:4px 0 0 0"><INPUT TYPE="hidden" NAME="Context" VALUE="#cname#">
	Rule <INPUT TYPE="text" NAME="RuleName" SIZE=8>
	<SELECT NAME="ResourceType"><OPTION>Application<OPTION>CFML<OPTION>File<OPTION>DataSource<OPTION>Component<OPTION>Collection<OPTION>CustomTag<OPTION>Function<OPTION>Tag<OPTION>UserObject</SELECT><BR>
	Resource <INPUT TYPE="text" NAME="Resource" SIZE=12> Actions <INPUT TYPE="text" NAME="Actions" VALUE="*" SIZE=10>
	<INPUT TYPE="submit" NAME="AddRule" VALUE="Add"></FORM></FONT></TD>
	<TD BGCOLOR="##FFFFFF">#Request.f#<B>Policies</B><BR>
	<cfloop query="pols">
		<cfregistry action="get" branch="#base#\#cname#\Policies\#pols.Entry#" entry="Rules" variable="pr">
		<cfregistry action="get" branch="#base#\#cname#\Policies\#pols.Entry#" entry="Users" variable="pu">
		<TT>#pols.Entry#</TT>: users <I>#pu#</I> get rules <I>#pr#</I> <A HREF="contexts.cfm?context=#URLEncodedFormat(cname)#&deletepolicy=#URLEncodedFormat(pols.Entry)#">x</A><BR>
	</cfloop>
	<FORM ACTION="contexts.cfm" METHOD="POST" STYLE="margin:4px 0 0 0"><INPUT TYPE="hidden" NAME="Context" VALUE="#cname#">
	Policy <INPUT TYPE="text" NAME="PolicyName" SIZE=8> Users <INPUT TYPE="text" NAME="PolicyUsers" SIZE=12><BR>
	Rules <SELECT NAME="PolicyRules" MULTIPLE SIZE=2><cfloop query="rules"><OPTION>#rules.Entry#</cfloop></SELECT>
	<INPUT TYPE="submit" NAME="AddPolicy" VALUE="Add"></FORM></FONT></TD></TR>
	</TABLE>
</cfloop>
<P><TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>New Security Context</B></FONT></TD></TR></TABLE>
<FORM ACTION="contexts.cfm" METHOD="POST">
<TABLE BORDER=0 CELLPADDING=2>
<TR><TD>#Request.f#Name</FONT></TD><TD><INPUT TYPE="text" NAME="ContextName" SIZE=20></TD></TR>
<TR><TD>#Request.f#Description</FONT></TD><TD><INPUT TYPE="text" NAME="Description" SIZE=40></TD></TR>
<TR><TD VALIGN=TOP>#Request.f#User Directories</FONT></TD><TD><SELECT NAME="UserDirectories" MULTIPLE SIZE=3><cfloop query="dirs"><OPTION SELECTED>#dirs.Entry#</cfloop></SELECT></TD></TR>
</TABLE>
<INPUT TYPE="submit" NAME="AddContext" VALUE="Add"> <INPUT TYPE="button" VALUE="Back" onClick="location='advancedsecurity.cfm'">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
