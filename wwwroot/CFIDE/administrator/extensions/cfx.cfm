<!--- Registered CFX Tags --->
<cfregistry action="getall" branch="#Request.reg#\CFX" name="tags" type="key" sort="Entry ASC">
<cfset pageTitle = "Registered CFX Tags">
<cfinclude template="../_header.cfm">
<cfoutput>
<FORM ACTION="cfxedit.cfm" METHOD="POST">
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="##669966"><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Tag name</B></FONT></TD><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Type</B></FONT></TD><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Description</B></FONT></TD></TR>
<TR BGCOLOR="##FFFFFF"><TD COLSPAN=3><INPUT TYPE="text" NAME="TagName" VALUE="CFX_" SIZE=20>
	<SELECT NAME="TagType"><OPTION VALUE="C++">C/C++<OPTION VALUE="Java">Java</SELECT> <INPUT TYPE="submit" VALUE="Add"></TD></TR>
<cfloop query="tags">
	<cfregistry action="get" branch="#Request.reg#\CFX\#tags.Entry#" entry="Description" variable="desc">
	<cfregistry action="get" branch="#Request.reg#\CFX\#tags.Entry#" entry="Type" variable="ttype">
	<TR BGCOLOR="#IIf(tags.CurrentRow MOD 2, DE('FFFBF0'), DE('FFFFFF'))#">
	<TD>#Request.f#<B><A HREF="cfxedit.cfm?TagName=#URLEncodedFormat(tags.Entry)#">#tags.Entry#</A></B></FONT></TD>
	<TD>#Request.f#<cfif ttype EQ "Java">Java<cfelse>C++</cfif></FONT></TD><TD>#Request.f##HTMLEditFormat(desc)#</FONT></TD></TR>
</cfloop>
</TABLE>
</FORM>
<P>#Request.f#<I>C++ CFX tags are shared libraries exporting <TT>void ProcessTagRequest(CFXRequest *pRequest)</TT>; see
<TT>src/kfx.h</TT> and the examples in the <TT>cfx</TT> directory of the KoldFusion distribution.
Java CFX tags are classes implementing <TT>com.allaire.cfx.CustomTag</TT> (or <TT>com.gibson.cfx.CustomTag</TT>), compiled
against <TT>cfx.jar</TT> and placed in the <TT>java/classes</TT> directory of the installation or on the Class Path set on the
<A HREF="../server/java.cfm">Java</A> page; see the examples in the <TT>java/samples</TT> directory.</I></FONT>
</cfoutput>
<cfinclude template="../_footer.cfm">
