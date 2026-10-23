<!--- Index a Verity collection --->
<cfparam name="URL.collection" default="">
<cfif IsDefined("Form.Submit")>
	<cfset r = KFUSION_VERITY("index", Form.Collection, Form.Directory, Form.Extensions, IsDefined("Form.Recurse"), Form.ReturnURL)>
	<cfset pageTitle = "Index Verity Collection">
	<cfinclude template="../_header.cfm">
	<cfmodule template="../_tags/status.cfm" message="#r.Message#" back="verity.cfm">
	<cfinclude template="../_footer.cfm">
	<cfabort>
</cfif>
<cfset info = KFUSION_SERVERINFO()>
<cfset pageTitle = "Index Verity Collection: #URL.collection#">
<cfinclude template="../_header.cfm">
<cfoutput>
<FORM ACTION="verityindex.cfm" METHOD="POST"><INPUT TYPE="hidden" NAME="Collection" VALUE="#HTMLEditFormat(URL.collection)#">
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD>#Request.f#<B>File Extensions</B></FONT></TD><TD><INPUT TYPE="text" NAME="Extensions" VALUE=".htm, .html, .cfm, .cfml" SIZE=30></TD></TR>
<TR><TD>#Request.f#<B>Directory Path</B></FONT></TD><TD><INPUT TYPE="text" NAME="Directory" VALUE="#info.WebRoot#" SIZE=45 STYLE="font-family:Courier New,monospace">
	<INPUT TYPE="button" VALUE="Browse Server..." onClick="browseServer('Directory')"></TD></TR>
<TR><TD></TD><TD>#Request.f#<INPUT TYPE="checkbox" NAME="Recurse" VALUE="1" CHECKED> Recursively index sub directories</FONT></TD></TR>
<TR><TD>#Request.f#<B>Return URL</B></FONT></TD><TD><INPUT TYPE="text" NAME="ReturnURL" VALUE="http://127.0.0.1:#info.Port#/" SIZE=45></TD></TR>
<TR><TD>#Request.f#<B>Language</B></FONT></TD><TD><SELECT NAME="Language"><OPTION>English</SELECT></TD></TR>
</TABLE>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Submit" VALUE="Submit"> <INPUT TYPE="button" VALUE="Cancel" onClick="location='verity.cfm'">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
