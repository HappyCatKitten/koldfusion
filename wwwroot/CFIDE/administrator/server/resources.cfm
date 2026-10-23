<!--- Resource View: every protected resource across all contexts --->
<cfset base = Request.reg & "\Security\Contexts">
<cfregistry action="getall" branch="#base#" name="ctxs" type="key">
<cfset pageTitle = "Resource View">
<cfinclude template="../_header.cfm">
<cfoutput>
<P>#Request.f#Every resource protected by a rule, by resource type.</FONT>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="##669966"><cfloop list="Resource Type,Resource,Actions,Rule,Context" index="h"><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>#h#</B></FONT></TD></cfloop></TR>
<cfset row = 0>
<cfloop query="ctxs">
	<cfregistry action="getall" branch="#base#\#ctxs.Entry#\Rules" name="rules" type="key">
	<cfloop query="rules">
		<cfset row = row + 1>
		<cfmodule template="../_tags/getreg.cfm" key="Security\Contexts\#ctxs.Entry#\Rules\#rules.Entry#" variable="R">
		<TR BGCOLOR="#IIf(row MOD 2, DE('FFFFFF'), DE('FFFBF0'))#"><TD>#Request.f##R.ResourceType#</FONT></TD><TD>#Request.f#<TT>#R.Resource#</TT></FONT></TD>
		<TD>#Request.f##R.Actions#</FONT></TD><TD>#Request.f##rules.Entry#</FONT></TD><TD>#Request.f##ctxs.Entry#</FONT></TD></TR>
	</cfloop>
</cfloop>
<cfif row EQ 0><TR><TD COLSPAN=5>#Request.f#<I>No resources are protected.</I></FONT></TD></TR></cfif>
</TABLE>
<FORM><INPUT TYPE="button" VALUE="Back" onClick="location='advancedsecurity.cfm'"></FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
