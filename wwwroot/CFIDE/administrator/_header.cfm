<!--- common page header: set Variables.pageTitle before including --->
<cfparam name="pageTitle" default="KoldFusion Administrator">
<cfparam name="pageHelp" default="">
<cfoutput>
<HTML>
<HEAD>
<TITLE>KoldFusion Administrator - #pageTitle#</TITLE>
<SCRIPT LANGUAGE="JavaScript">
<!--
function browseServer(field) {
	var w = window.open('#Request.adm#/browse.cfm?field=' + escape(field) + '&dir=' + escape(eval('document.forms[0].' + field + '.value')),
		'browse', 'width=420,height=430,scrollbars=yes,resizable=yes');
	w.focus();
}
//-->
</SCRIPT>
</HEAD>
<BODY BGCOLOR="##FFFFFF" LINK="##0000FF" VLINK="##336633" ALINK="##669966" LEFTMARGIN=20 MARGINWIDTH=20>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR><TD ALIGN=RIGHT><IMG SRC="#Request.adm#/images/kf_logo.gif" WIDTH=200 HEIGHT=70 ALT="KoldFusion"></TD></TR>
<TR><TD><FONT FACE="Arial, Helvetica" SIZE="4"><B>#pageTitle#</B></FONT></TD></TR>
</TABLE>
<cfif Len(pageHelp)><P>#Request.f##pageHelp#</FONT></cfif>
</cfoutput>
