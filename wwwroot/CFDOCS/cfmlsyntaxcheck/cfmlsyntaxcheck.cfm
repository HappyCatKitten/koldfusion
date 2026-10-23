<!---
	/CFDOCS/cfmlsyntaxcheck/cfmlsyntaxcheck.cfm - the CFML Syntax Checker
	Parses CFML with the server's own parser (KFUSION_CHECKSYNTAX) without running it:
	either code pasted into the form, or every .cfm file in a directory under the web root.
	Checking directories reads files on the server, so that part only works from 127.0.0.1.
--->
<cfparam name="Form.Mode" default="paste">
<cfparam name="Form.Code" default="">
<cfparam name="Form.Directory" default="/CFDOCS/snippets">
<cfparam name="Form.Extensions" default="cfm,cfml">
<cfset Variables.local = ListFind("127.0.0.1,::1", CGI.REMOTE_ADDR) GT 0>
<cfset Variables.maxFiles = 1000>
<cfset Variables.ran = IsDefined("Form.Check")>
<cfset Variables.problem = "">
<cfset Results = QueryNew("File,OK,Line,Col,Message,Detail")>

<cfif Variables.ran AND Form.Mode EQ "paste">
	<!--- ============================================= pasted code --->
	<cfif NOT Len(Trim(Form.Code))>
		<cfset Variables.problem = "Paste some CFML into the box first.">
	<cfelse>
		<cfset r = KFUSION_CHECKSYNTAX(Form.Code, "(pasted code)")>
		<cfset QueryAddRow(Results)>
		<cfset QuerySetCell(Results, "File", "(pasted code)")>
		<cfset QuerySetCell(Results, "OK", r.OK)>
		<cfset QuerySetCell(Results, "Line", r.Line)>
		<cfset QuerySetCell(Results, "Col", r.Column)>
		<cfset QuerySetCell(Results, "Message", r.Message)>
		<cfset QuerySetCell(Results, "Detail", r.Detail)>
	</cfif>
<cfelseif Variables.ran AND Form.Mode EQ "dir">
	<!--- ============================================= a directory --->
	<cfset Variables.webDir = Trim(Replace(Form.Directory, "\", "/", "ALL"))>
	<cfif Left(Variables.webDir, 1) NEQ "/"><cfset Variables.webDir = "/" & Variables.webDir></cfif>
	<cfset Variables.webRoot = ExpandPath("/")>
	<cfif NOT Variables.local>
		<cfset Variables.problem = "Checking directories reads files on the server, so it is only available when you browse from the server itself (127.0.0.1). You can still paste code.">
	<cfelseif Find("..", Variables.webDir) OR REFind("[^A-Za-z0-9_./ -]", Variables.webDir)>
		<cfset Variables.problem = "Please give a plain directory path under the web root, such as /CFDOCS/snippets.">
	<cfelseif NOT DirectoryExists(ExpandPath(Variables.webDir))>
		<cfset Variables.problem = "The directory #Variables.webDir# does not exist under the web root.">
	<cfelse>
		<!--- walk the tree breadth-first; CFDIRECTORY does not recurse in 4.5 --->
		<cfset Variables.todo = ArrayNew(1)>
		<cfset ArrayAppend(Variables.todo, Variables.webDir)>
		<cfset Variables.count = 0>
		<cfloop condition="ArrayLen(Variables.todo) GT 0 AND Variables.count LT Variables.maxFiles">
			<cfset Variables.here = Variables.todo[1]>
			<cfset ArrayDeleteAt(Variables.todo, 1)>
			<cfif Right(Variables.here, 1) NEQ "/"><cfset Variables.here = Variables.here & "/"></cfif>
			<cfdirectory action="list" directory="#ExpandPath(Variables.here)#" name="Listing" sort="name asc">
			<cfloop query="Listing">
				<cfif Listing.Type EQ "Dir">
					<cfif IsDefined("Form.Recurse") AND Listing.Name NEQ "." AND Listing.Name NEQ "..">
						<cfset ArrayAppend(Variables.todo, Variables.here & Listing.Name)>
					</cfif>
				<cfelseif ListFindNoCase(Form.Extensions, ListLast(Listing.Name, ".")) AND Variables.count LT Variables.maxFiles>
					<cfset Variables.count = Variables.count + 1>
					<cffile action="read" file="#ExpandPath(Variables.here & Listing.Name)#" variable="Variables.source">
					<cfset r = KFUSION_CHECKSYNTAX(Variables.source, Variables.here & Listing.Name)>
					<cfset QueryAddRow(Results)>
					<cfset QuerySetCell(Results, "File", Variables.here & Listing.Name)>
					<cfset QuerySetCell(Results, "OK", r.OK)>
					<cfset QuerySetCell(Results, "Line", r.Line)>
					<cfset QuerySetCell(Results, "Col", r.Column)>
					<cfset QuerySetCell(Results, "Message", r.Message)>
					<cfset QuerySetCell(Results, "Detail", r.Detail)>
				</cfif>
			</cfloop>
		</cfloop>
		<cfif NOT Results.RecordCount>
			<cfset Variables.problem = "No files with the extensions #Form.Extensions# were found in #Variables.webDir#.">
		</cfif>
	</cfif>
</cfif>

<cfset Variables.nBad = 0>
<cfloop query="Results"><cfif NOT Results.OK><cfset Variables.nBad = Variables.nBad + 1></cfif></cfloop>

<HTML>
<HEAD>
<TITLE>CFML Syntax Checker</TITLE>
<LINK REL="stylesheet" TYPE="text/css" HREF="/CFDOCS/kfdocs.css">
<SCRIPT LANGUAGE="JavaScript">
<!--
function pickMode(m) {
	var f = document.forms[0];
	for (var i = 0; i < f.Mode.length; i++) if (f.Mode[i].value == m) f.Mode[i].checked = true;
}
//-->
</SCRIPT>
</HEAD>
<BODY BGCOLOR="#FFFFF0" LINK="#0000CC" VLINK="#663399">
<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=2><TR>
<TD><A HREF="/CFDOCS/dochome.cfm"><IMG SRC="/CFDOCS/images/doc_up.gif" WIDTH=16 HEIGHT=16 BORDER=0 ALT="Documentation home"></A></TD>
<TD><A HREF="/CFDOCS/dochome.cfm"><IMG SRC="/CFDOCS/images/doc_home.gif" WIDTH=16 HEIGHT=16 BORDER=0 ALT="Documentation home"></A></TD>
<TD><A HREF="/CFDOCS/langref/index.htm"><IMG SRC="/CFDOCS/images/doc_index.gif" WIDTH=16 HEIGHT=16 BORDER=0 ALT="CFML Language Reference"></A></TD>
</TR></TABLE>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR VALIGN=BOTTOM>
	<TD><H1><IMG SRC="/CFIDE/administrator/images/check.gif" WIDTH=16 HEIGHT=16> CFML Syntax Checker</H1></TD>
	<TD ALIGN=RIGHT><IMG SRC="/CFIDE/administrator/images/kf_logo_small.gif" WIDTH=120 HEIGHT=40 ALT="KoldFusion"></TD>
</TR>
</TABLE>
<HR NOSHADE SIZE=1>
<P>The Syntax Checker runs your templates through the KoldFusion 4.5 parser and reports anything it cannot
understand: unclosed tags, unbalanced <CODE>#</CODE> signs, broken expressions, tags in the wrong place. Nothing is
executed, so it is safe to point it at any template. It is the polite thing to do before upgrading a server, and the
smart thing to do before a demo.</P>
<P><FONT SIZE=1>The checker only finds <I>syntax</I> errors. A misspelled variable or a missing table is found
the old-fashioned way: at run time, in front of your boss.</FONT></P>

<cfoutput>
<FORM ACTION="cfmlsyntaxcheck.cfm" METHOD="POST">
<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0>
<TR VALIGN=TOP>
	<TD><INPUT TYPE="radio" NAME="Mode" VALUE="paste"<cfif Form.Mode NEQ "dir"> CHECKED</cfif>></TD>
	<TD><B>Check this code</B><BR>
	<TEXTAREA NAME="Code" ROWS=10 COLS=72 WRAP="off" onFocus="pickMode('paste')">#HTMLEditFormat(Form.Code)#</TEXTAREA></TD>
</TR>
<TR VALIGN=TOP>
	<TD><INPUT TYPE="radio" NAME="Mode" VALUE="dir"<cfif Form.Mode EQ "dir"> CHECKED</cfif>></TD>
	<TD><B>Check every template in this directory</B> <FONT SIZE=1>(a path under the web root<cfif NOT Variables.local>; available from the server only</cfif>)</FONT><BR>
	<INPUT TYPE="text" NAME="Directory" SIZE=40 VALUE="#HTMLEditFormat(Form.Directory)#" onFocus="pickMode('dir')">
	<INPUT TYPE="checkbox" NAME="Recurse" VALUE="1"<cfif IsDefined("Form.Recurse")> CHECKED</cfif>> include subdirectories
	&nbsp; extensions <INPUT TYPE="text" NAME="Extensions" SIZE=10 VALUE="#HTMLEditFormat(Form.Extensions)#"></TD>
</TR>
<TR><TD></TD><TD><INPUT TYPE="submit" NAME="Check" VALUE="Check Syntax"></TD></TR>
</TABLE>
</FORM>
</cfoutput>

<cfif Len(Variables.problem)>
	<P><IMG SRC="/CFIDE/administrator/images/warn.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
	<B><cfoutput>#HTMLEditFormat(Variables.problem)#</cfoutput></B></P>
</cfif>

<cfif Results.RecordCount>
	<H3>Results</H3>
	<cfoutput>
	<P>Checked <B>#Results.RecordCount#</B> template<cfif Results.RecordCount NEQ 1>s</cfif>:
	<cfif Variables.nBad EQ 0><FONT COLOR="##006600"><B>no syntax errors found.</B></FONT>
	<cfelse><FONT COLOR="##CC0000"><B>#Variables.nBad# with errors</B></FONT>, #Evaluate(Results.RecordCount - Variables.nBad)# clean.</cfif>
	<cfif Results.RecordCount GE Variables.maxFiles>(Stopped after #Variables.maxFiles# files.)</cfif></P>
	</cfoutput>
	<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=1 BGCOLOR="#999999" WIDTH="100%">
	<TR BGCOLOR="#669966">
		<TH ALIGN=LEFT><FONT COLOR="#FFFFFF">Template</FONT></TH>
		<TH><FONT COLOR="#FFFFFF">Status</FONT></TH>
		<TH><FONT COLOR="#FFFFFF">Line</FONT></TH>
		<TH><FONT COLOR="#FFFFFF">Col</FONT></TH>
		<TH ALIGN=LEFT><FONT COLOR="#FFFFFF">Message</FONT></TH>
	</TR>
	<cfoutput query="Results">
		<cfif Results.OK>
			<cfset Variables.bg = "FFFFFF">
		<cfelse>
			<cfset Variables.bg = "FFEEEE">
		</cfif>
		<TR BGCOLOR="###Variables.bg#" VALIGN=TOP>
		<TD><CODE>#HTMLEditFormat(Results.File)#</CODE></TD>
		<TD ALIGN=CENTER><cfif Results.OK><IMG SRC="/CFIDE/administrator/images/check.gif" WIDTH=16 HEIGHT=16 ALT="OK"><cfelse><IMG SRC="/CFIDE/administrator/images/x.gif" WIDTH=16 HEIGHT=16 ALT="Error"></cfif></TD>
		<TD ALIGN=RIGHT><cfif NOT Results.OK>#Results.Line#</cfif></TD>
		<TD ALIGN=RIGHT><cfif NOT Results.OK>#Results.Col#</cfif></TD>
		<TD><cfif Results.OK><FONT SIZE=1>OK</FONT><cfelse>#Results.Message#<cfif Len(Results.Detail)><BR><FONT SIZE=1>#Results.Detail#</FONT></cfif></cfif></TD>
		</TR>
	</cfoutput>
	</TABLE>
	<cfif Form.Mode EQ "paste" AND Results.RecordCount EQ 1 AND NOT Results.OK AND Results.Line GT 0>
		<!--- show the offending line --->
		<cfset Variables.lines = ListToArray(Replace(Form.Code, Chr(13), "", "ALL"), Chr(10))>
		<cfset Variables.src = Replace(Form.Code, Chr(13), "", "ALL")>
		<cfset Variables.lineNo = 1>
		<cfset Variables.pos = 1>
		<cfloop condition="Variables.lineNo LT Results.Line AND Variables.pos GT 0">
			<cfset Variables.pos = Find(Chr(10), Variables.src, Variables.pos)>
			<cfif Variables.pos><cfset Variables.pos = Variables.pos + 1></cfif>
			<cfset Variables.lineNo = Variables.lineNo + 1>
		</cfloop>
		<cfif Variables.pos GT 0>
			<cfset Variables.endPos = Find(Chr(10), Variables.src, Variables.pos)>
			<cfif Variables.endPos EQ 0><cfset Variables.endPos = Len(Variables.src) + 1></cfif>
			<cfset Variables.theLine = Mid(Variables.src, Variables.pos, Variables.endPos - Variables.pos)>
			<cfoutput>
			<P><B>Line #Results.Line#:</B></P>
			<PRE>#HTMLEditFormat(Variables.theLine)#
#RepeatString(" ", Max(Results.Col - 1, 0))#^</PRE>
			</cfoutput>
		</cfif>
	</cfif>
</cfif>

<HR NOSHADE SIZE=1>
<P><FONT SIZE=1>Behind the scenes: <A HREF="/CFDOCS/langref/kfusion_checksyntax.htm"><CODE>KFUSION_CHECKSYNTAX(code [, name])</CODE></A>
returns a structure with the keys OK, Message, Detail, Line and Column. Templates read with <CODE>CFFILE</CODE>,
directories listed with <CODE>CFDIRECTORY</CODE>.</FONT></P>
<FONT SIZE=1 CLASS="copyright">Copyright &copy; 1995-1999, Allair Corporation. All rights reserved.</FONT>
</BODY>
</HTML>
