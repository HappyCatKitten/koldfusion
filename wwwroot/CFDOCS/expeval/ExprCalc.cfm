<!---
	/CFDOCS/expeval/ExprCalc.cfm - the Expression Evaluator
	Type a CFML expression, see what Evaluate() makes of it. Keeps a per-session history.
	Evaluate() can call any function on the server, so the page only answers to 127.0.0.1.
--->
<cfif NOT ListFind("127.0.0.1,::1", CGI.REMOTE_ADDR)>
<HTML><HEAD><TITLE>Expression Evaluator</TITLE><LINK REL="stylesheet" TYPE="text/css" HREF="/CFDOCS/kfdocs.css"></HEAD>
<BODY BGCOLOR="#FFFFF0">
<H1>Expression Evaluator</H1>
<P><IMG SRC="/CFIDE/administrator/images/lock.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
<B>Sorry, the Expression Evaluator only works from a browser on the server itself (127.0.0.1).</B></P>
<P>It evaluates whatever you type, with the full power of CFML, on this machine. That is a wonderful
learning tool for the person sitting at the server and a wonderful attack tool for everybody else.
We learned this in 1999 so that you do not have to.</P>
<P><A HREF="/CFDOCS/dochome.cfm">Back to the documentation</A></P>
</BODY></HTML>
<cfabort>
</cfif>

<cfapplication name="KFExpressionEvaluator" sessionmanagement="Yes" sessiontimeout="#CreateTimeSpan(0, 0, 30, 0)#">
<cfparam name="Form.Expr" default="">
<cfparam name="URL.expr" default="">
<cfparam name="URL.clear" default="No">
<cfif NOT Len(Form.Expr) AND Len(URL.expr)><cfset Form.Expr = URL.expr></cfif>
<cfset Variables.maxHistory = 25>

<cflock scope="Session" type="Exclusive" timeout="10">
	<cfif NOT IsDefined("Session.ExprHistory") OR URL.clear>
		<cfset Session.ExprHistory = ArrayNew(1)>
	</cfif>
</cflock>

<cfset Variables.didEval = Len(Trim(Form.Expr)) GT 0>
<cfset Variables.ok = 0>
<cfif Variables.didEval>
	<cfset Variables.started = GetTickCount()>
	<cftry>
		<cfset Variables.result = Evaluate(Form.Expr)>
		<cfset Variables.ok = 1>
		<cfcatch type="Any">
			<cfset Variables.errType = CFCATCH.Type>
			<cfset Variables.errMessage = CFCATCH.Message>
			<cfset Variables.errDetail = CFCATCH.Detail>
		</cfcatch>
	</cftry>
	<cfset Variables.elapsed = GetTickCount() - Variables.started>

	<!--- what kind of value is it? --->
	<cfif NOT Variables.ok>
		<cfset Variables.kind = "Error">
	<cfelseif IsQuery(Variables.result)><cfset Variables.kind = "Query">
	<cfelseif IsStruct(Variables.result)><cfset Variables.kind = "Structure">
	<cfelseif IsArray(Variables.result)><cfset Variables.kind = "Array">
	<cfelseif IsBinary(Variables.result)><cfset Variables.kind = "Binary">
	<cfelseif NOT IsSimpleValue(Variables.result)><cfset Variables.kind = "Object">
	<cfelseif IsNumeric(Variables.result)><cfset Variables.kind = "Number">
	<cfelseif ListFindNoCase("Yes,No,True,False", Variables.result)><cfset Variables.kind = "Boolean">
	<cfelseif IsDate(Variables.result)><cfset Variables.kind = "Date/time">
	<cfelse><cfset Variables.kind = "String"></cfif>

	<cfif Variables.ok>
		<cfif IsSimpleValue(Variables.result)>
			<cfset Variables.short = Variables.result>
			<cfif Len(Variables.short) GT 60><cfset Variables.short = Left(Variables.short, 57) & "..."></cfif>
		<cfelseif Variables.kind EQ "Array"><cfset Variables.short = "[array of #ArrayLen(Variables.result)#]">
		<cfelseif Variables.kind EQ "Structure"><cfset Variables.short = "[structure with #StructCount(Variables.result)# keys]">
		<cfelseif Variables.kind EQ "Query"><cfset Variables.short = "[query, #Variables.result.RecordCount# rows]">
		<cfelse><cfset Variables.short = "[#LCase(Variables.kind)#]"></cfif>
	<cfelse>
		<cfset Variables.short = Variables.errMessage>
	</cfif>

	<cfset Variables.entry = StructNew()>
	<cfset Variables.entry.Expr = Form.Expr>
	<cfset Variables.entry.Kind = Variables.kind>
	<cfset Variables.entry.Short = Variables.short>
	<cflock scope="Session" type="Exclusive" timeout="10">
		<cfset ArrayPrepend(Session.ExprHistory, Variables.entry)>
		<cfloop condition="ArrayLen(Session.ExprHistory) GT Variables.maxHistory">
			<cfset ArrayDeleteAt(Session.ExprHistory, ArrayLen(Session.ExprHistory))>
		</cfloop>
		<cfset Variables.history = Duplicate(Session.ExprHistory)>
	</cflock>
<cfelse>
	<cflock scope="Session" type="ReadOnly" timeout="10">
		<cfset Variables.history = Duplicate(Session.ExprHistory)>
	</cflock>
</cfif>

<HTML>
<HEAD>
<TITLE>Expression Evaluator</TITLE>
<LINK REL="stylesheet" TYPE="text/css" HREF="/CFDOCS/kfdocs.css">
<SCRIPT LANGUAGE="JavaScript">
<!--
function useExample(s) {
	document.forms[0].Expr.value = s;
	document.forms[0].Expr.focus();
}
//-->
</SCRIPT>
</HEAD>
<BODY BGCOLOR="#FFFFF0" LINK="#0000CC" VLINK="#663399" onLoad="document.forms[0].Expr.focus()">
<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=2><TR>
<TD><A HREF="/CFDOCS/dochome.cfm"><IMG SRC="/CFDOCS/images/doc_up.gif" WIDTH=16 HEIGHT=16 BORDER=0 ALT="Documentation home"></A></TD>
<TD><A HREF="/CFDOCS/dochome.cfm"><IMG SRC="/CFDOCS/images/doc_home.gif" WIDTH=16 HEIGHT=16 BORDER=0 ALT="Documentation home"></A></TD>
<TD><A HREF="/CFDOCS/langref/index.htm"><IMG SRC="/CFDOCS/images/doc_index.gif" WIDTH=16 HEIGHT=16 BORDER=0 ALT="CFML Language Reference"></A></TD>
</TR></TABLE>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR VALIGN=BOTTOM>
	<TD><H1>Expression Evaluator</H1></TD>
	<TD ALIGN=RIGHT><IMG SRC="/CFIDE/administrator/images/kf_logo_small.gif" WIDTH=120 HEIGHT=40 ALT="KoldFusion"></TD>
</TR>
</TABLE>
<HR NOSHADE SIZE=1>
<P>Type any CFML expression and press <B>Evaluate</B>. The expression is passed to
<A HREF="/CFDOCS/langref/evaluate.htm"><CODE>Evaluate()</CODE></A> and the result is shown together with its type.
Remember the CFML operators: <CODE>EQ NEQ GT LT GTE LTE AND OR NOT MOD &amp;</CODE>.</P>

<cfoutput>
<FORM ACTION="ExprCalc.cfm" METHOD="POST">
<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0 BGCOLOR="##E8E8D8" WIDTH="100%"><TR><TD>
<B>Expression</B><BR>
<INPUT TYPE="text" NAME="Expr" SIZE=70 VALUE="#HTMLEditFormat(Form.Expr)#">
<INPUT TYPE="submit" VALUE="Evaluate">
<BR><FONT SIZE=1>Try:
<A HREF="javascript:useExample('2 ^ 10 + 1')">2 ^ 10 + 1</A> &middot;
<A HREF="javascript:useExample('DateFormat(Now(), ''dddd, mmmm d, yyyy'')')">DateFormat(Now(), ...)</A> &middot;
<A HREF="javascript:useExample('DateDiff(''d'', Now(), CreateDate(2000, 1, 1))')">days until 2000</A> &middot;
<A HREF="javascript:useExample('ListSort(''pear,Apple,fig'', ''textnocase'')')">ListSort</A> &middot;
<A HREF="javascript:useExample('ListToArray(''red,green,blue'')')">ListToArray</A> &middot;
<A HREF="javascript:useExample('Server.ColdFusion')">Server.ColdFusion</A> &middot;
<A HREF="javascript:useExample('IsLeapYear(2000) AND NOT IsLeapYear(1900)')">Y2K test</A> &middot;
<A HREF="javascript:useExample('Hash(''KoldFusion'')')">Hash</A> &middot;
<A HREF="javascript:useExample('1 / 0')">1 / 0</A>
</FONT>
</TD></TR></TABLE>
</FORM>
</cfoutput>

<cfif Variables.didEval>
	<H3>Result</H3>
	<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=1 BGCOLOR="#999999">
	<cfoutput>
	<TR BGCOLOR="##FFFFFF" VALIGN=TOP><TD BGCOLOR="##669966"><FONT COLOR="##FFFFFF"><B>Expression</B></FONT></TD><TD><CODE>#HTMLEditFormat(Form.Expr)#</CODE></TD></TR>
	<cfif Variables.ok>
		<TR BGCOLOR="##FFFFFF" VALIGN=TOP><TD BGCOLOR="##669966"><FONT COLOR="##FFFFFF"><B>Result</B></FONT></TD>
		<TD><cfmodule template="showvalue.cfm" value="#Variables.result#"></TD></TR>
		<TR BGCOLOR="##FFFBF0"><TD BGCOLOR="##669966"><FONT COLOR="##FFFFFF"><B>Type</B></FONT></TD><TD>#Variables.kind#</TD></TR>
		<cfif IsSimpleValue(Variables.result)>
			<TR BGCOLOR="##FFFFFF"><TD BGCOLOR="##669966"><FONT COLOR="##FFFFFF"><B>Length</B></FONT></TD><TD>#Len(Variables.result)# characters</TD></TR>
		</cfif>
	<cfelse>
		<TR BGCOLOR="##FFEEEE" VALIGN=TOP><TD BGCOLOR="##CC3333"><FONT COLOR="##FFFFFF"><B>Error</B></FONT></TD>
		<TD><B>#Variables.errMessage#</B><cfif Len(Variables.errDetail)><BR><FONT SIZE=1>#Variables.errDetail#</FONT></cfif>
		<BR><FONT SIZE=1>Exception type: #HTMLEditFormat(Variables.errType)#</FONT></TD></TR>
	</cfif>
	<TR BGCOLOR="##FFFBF0"><TD BGCOLOR="##669966"><FONT COLOR="##FFFFFF"><B>Time</B></FONT></TD><TD>#Variables.elapsed# ms</TD></TR>
	</cfoutput>
	</TABLE>
</cfif>

<cfif ArrayLen(Variables.history)>
	<H3>History <FONT SIZE=1>(this session, newest first &middot; <A HREF="ExprCalc.cfm?clear=Yes">clear</A>)</FONT></H3>
	<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=1 BGCOLOR="#999999" WIDTH="100%">
	<TR BGCOLOR="#669966"><TH ALIGN=LEFT><FONT COLOR="#FFFFFF">Expression</FONT></TH><TH ALIGN=LEFT><FONT COLOR="#FFFFFF">Type</FONT></TH><TH ALIGN=LEFT><FONT COLOR="#FFFFFF">Result</FONT></TH></TR>
	<cfoutput>
	<cfloop index="i" from="1" to="#ArrayLen(Variables.history)#">
		<cfset h = Variables.history[i]>
		<cfif i MOD 2><cfset Variables.bg = "FFFFFF"><cfelse><cfset Variables.bg = "FFFBF0"></cfif>
		<TR BGCOLOR="###Variables.bg#" VALIGN=TOP>
		<TD><A HREF="ExprCalc.cfm?expr=#URLEncodedFormat(h.Expr)#"><CODE>#HTMLEditFormat(h.Expr)#</CODE></A></TD>
		<TD><FONT SIZE=1><cfif h.Kind EQ "Error"><FONT COLOR="##CC0000">Error</FONT><cfelse>#h.Kind#</cfif></FONT></TD>
		<TD><FONT SIZE=1>#HTMLEditFormat(h.Short)#</FONT></TD>
		</TR>
	</cfloop>
	</cfoutput>
	</TABLE>
</cfif>

<H3>A word about the old Expression Evaluator</H3>
<P CLASS="note"><IMG SRC="/CFIDE/administrator/images/warn.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
The Expression Evaluator that shipped in 1999 had two extra buttons, <I>Open</I> and <I>Upload</I>, so you could
load a file into it and save one back. They were handy. They also worked for any visitor on the Internet, on any file
the server could reach, which made every freshly installed server a public file manager with a CFML calculator
attached. Allair security bulletin ASB99-01 recommended removing the sample pages from production servers, and a
lot of administrators spent a long weekend finding out why. This edition has no file features at all, and it refuses
to talk to anyone but 127.0.0.1. You are welcome.</P>
<P><FONT SIZE=1>Production tip: remove <CODE>/CFDOCS</CODE> from public servers anyway. Old habits keep you safe.</FONT></P>

<HR NOSHADE SIZE=1>
<FONT SIZE=1 CLASS="copyright">Copyright &copy; 1995-1999, Allair Corporation. All rights reserved.</FONT>
</BODY>
</HTML>
