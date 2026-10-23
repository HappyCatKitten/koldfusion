<!--- Registered CFX Tags --->
<cfregistry action="getall" branch="#Request.reg#\CFX" name="tags" type="key" sort="Entry ASC">
<cfset pageTitle = "Registered CFX Tags">
<cfinclude template="../_header.cfm">
<cfoutput>
<FORM ACTION="cfxedit.cfm" METHOD="POST">
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="##669966"><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Tag name</B></FONT></TD><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Description</B></FONT></TD></TR>
<TR BGCOLOR="##FFFFFF"><TD><INPUT TYPE="text" NAME="TagName" VALUE="CFX_" SIZE=20>
	<SELECT NAME="TagType"><OPTION VALUE="C++">C/C++<OPTION VALUE="Java">Java</SELECT> <INPUT TYPE="submit" VALUE="Add"></TD><TD></TD></TR>
<cfloop query="tags">
	<cfregistry action="get" branch="#Request.reg#\CFX\#tags.Entry#" entry="Description" variable="desc">
	<TR BGCOLOR="#IIf(tags.CurrentRow MOD 2, DE('FFFBF0'), DE('FFFFFF'))#">
	<TD>#Request.f#<B><A HREF="cfxedit.cfm?TagName=#URLEncodedFormat(tags.Entry)#">#tags.Entry#</A></B></FONT></TD><TD>#Request.f##HTMLEditFormat(desc)#</FONT></TD></TR>
</cfloop>
</TABLE>
</FORM>
<P>#Request.f#<I>CFX tags are shared libraries exporting <TT>void ProcessTagRequest(CFXRequest *pRequest)</TT>; see
<TT>src/kfx.h</TT> and the examples in the <TT>cfx</TT> directory of the KoldFusion distribution.</I></FONT>
</cfoutput>
<cfinclude template="../_footer.cfm">
