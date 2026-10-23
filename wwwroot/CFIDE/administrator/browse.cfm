<!--- "Browse Server..." directory picker (the 4.x Administrator used a Java applet for this) --->
<cfparam name="URL.dir" default="">
<cfparam name="URL.field" default="">
<cfset info = KFUSION_SERVERINFO()>
<cfset dir = Trim(URL.dir)>
<cfif NOT Len(dir) OR NOT DirectoryExists(dir)>
	<cfif Len(dir) AND FileExists(dir)><cfset dir = GetDirectoryFromPath(dir)><cfelse><cfset dir = info.Root></cfif>
</cfif>
<cfif Right(dir, 1) EQ "/" AND Len(dir) GT 1><cfset dir = Left(dir, Len(dir) - 1)></cfif>
<cfset parent = GetDirectoryFromPath(dir)>
<cfif Len(parent) GT 1 AND Right(parent, 1) EQ "/"><cfset parent = Left(parent, Len(parent) - 1)></cfif>
<cfdirectory action="list" directory="#dir#" name="entries" sort="Type ASC, Name ASC">
<HTML><HEAD><TITLE>Browse Server</TITLE>
<SCRIPT LANGUAGE="JavaScript">
<!--
function pick(path) {
	var f = <cfoutput>'#JSStringFormat(URL.field)#'</cfoutput>;
	if (window.opener && window.opener.document.forms[0][f]) window.opener.document.forms[0][f].value = path;
	window.close();
}
//-->
</SCRIPT></HEAD>
<BODY BGCOLOR="#C0C0C0">
<cfoutput>
<TABLE WIDTH="100%" BORDER=1 CELLPADDING=4 CELLSPACING=0 BGCOLOR="##FFFFFF"><TR><TD>
<FONT FACE="Arial" SIZE=2><B>#HTMLEditFormat(dir)#</B></FONT><BR>
<FONT FACE="Arial" SIZE=2>
<IMG SRC="images/folder.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE> <A HREF="browse.cfm?field=#URLEncodedFormat(URL.field)#&dir=#URLEncodedFormat(parent)#">..</A><BR>
<cfloop query="entries">
	<cfif entries.Name NEQ "." AND entries.Name NEQ "..">
	<cfif entries.Type EQ "Dir">
		<IMG SRC="images/folder.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE> <A HREF="browse.cfm?field=#URLEncodedFormat(URL.field)#&dir=#URLEncodedFormat(dir & '/' & entries.Name)#">#entries.Name#</A><BR>
	<cfelse>
		<IMG SRC="images/file.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE> <A HREF="javascript:pick('#JSStringFormat(dir & '/' & entries.Name)#')">#entries.Name#</A><BR>
	</cfif>
	</cfif>
</cfloop>
</FONT></TD></TR></TABLE>
<FORM><INPUT TYPE="button" VALUE="Select This Directory" onClick="pick('#JSStringFormat(dir)#')"> <INPUT TYPE="button" VALUE="Cancel" onClick="window.close()"></FORM>
</cfoutput>
</BODY></HTML>
