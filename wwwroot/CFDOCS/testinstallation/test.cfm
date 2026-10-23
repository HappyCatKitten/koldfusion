<!--- Test your installation --->
<cfset tests = ArrayNew(1)>
<cfset t = StructNew()><cfset t.name = "CFML processing"><cfset t.ok = (1 + 1 EQ 2)><cfset t.detail = "1 + 1 = #1+1#; today is #DateFormat(Now(), 'dddd, mmmm d, yyyy')#"><cfset ArrayAppend(tests, t)>
<cftry>
	<cfquery name="q" datasource="cfsnippets">SELECT COUNT(*) AS N FROM Employees</cfquery>
	<cfset t = StructNew()><cfset t.name = "Data source cfsnippets"><cfset t.ok = true><cfset t.detail = "Connected; #q.N# employees found."><cfset ArrayAppend(tests, t)>
	<cfcatch type="Database"><cfset t = StructNew()><cfset t.name = "Data source cfsnippets"><cfset t.ok = false><cfset t.detail = cfcatch.Message><cfset ArrayAppend(tests, t)></cfcatch>
</cftry>
<cftry>
	<cfset tmp = GetTempDirectory() & "kf_installtest.txt">
	<cffile action="write" file="#tmp#" output="ok">
	<cffile action="read" file="#tmp#" variable="back">
	<cffile action="delete" file="#tmp#">
	<cfset t = StructNew()><cfset t.name = "File access (CFFILE)"><cfset t.ok = Trim(back) EQ "ok"><cfset t.detail = "Wrote, read and deleted a file in #GetTempDirectory()#"><cfset ArrayAppend(tests, t)>
	<cfcatch type="Any"><cfset t = StructNew()><cfset t.name = "File access (CFFILE)"><cfset t.ok = false><cfset t.detail = cfcatch.Message><cfset ArrayAppend(tests, t)></cfcatch>
</cftry>
<cftry>
	<cfx_hello name="installer" variable="hi">
	<cfset t = StructNew()><cfset t.name = "CFX tags"><cfset t.ok = true><cfset t.detail = hi><cfset ArrayAppend(tests, t)>
	<cfcatch type="Any"><cfset t = StructNew()><cfset t.name = "CFX tags"><cfset t.ok = false><cfset t.detail = cfcatch.Message><cfset ArrayAppend(tests, t)></cfcatch>
</cftry>
<cfset packet = "">
<cfwddx action="cfml2wddx" input="#tests[1].detail#" output="packet">
<cfset t = StructNew()><cfset t.name = "WDDX"><cfset t.ok = IsWDDX(packet)><cfset t.detail = "Serialized a string to a #Len(packet)#-byte packet"><cfset ArrayAppend(tests, t)>
<cfset t = StructNew()><cfset t.name = "Encryption"><cfset t.ok = (Encrypt("text", "key") EQ "$38YC!P  " & Chr(10))><cfset t.detail = "Encrypt(""text"",""key"") matches the classic test vector"><cfset ArrayAppend(tests, t)>
<HTML><HEAD><TITLE>KoldFusion Installation Test</TITLE></HEAD>
<BODY BGCOLOR="#FFFFFF">
<FONT FACE="Arial, Helvetica" SIZE=2>
<IMG SRC="/images/welcome_logo.gif" WIDTH=400 HEIGHT=105>
<H2>Congratulations!</H2>
<cfoutput>
<P>If you can read this page, KoldFusion Server #Server.ColdFusion.ProductVersion# (#Server.ColdFusion.ProductLevel#)
is installed on <B>#CGI.SERVER_NAME#</B> and processing CFML templates.</P>
<TABLE BORDER=1 CELLPADDING=4 CELLSPACING=0>
<TR BGCOLOR="##C0C0C0"><TH><FONT FACE="Arial" SIZE=2>Test</FONT></TH><TH><FONT FACE="Arial" SIZE=2>Result</FONT></TH><TH><FONT FACE="Arial" SIZE=2>Details</FONT></TH></TR>
<cfloop index="i" from="1" to="#ArrayLen(tests)#">
<TR><TD><FONT FACE="Arial" SIZE=2>#tests[i].name#</FONT></TD>
<TD ALIGN=CENTER><IMG SRC="/CFIDE/administrator/images/#IIf(tests[i].ok, DE('check'), DE('x'))#.gif" WIDTH=16 HEIGHT=16></TD>
<TD><FONT FACE="Arial" SIZE=2>#HTMLEditFormat(tests[i].detail)#</FONT></TD></TR>
</cfloop>
</TABLE>
</cfoutput>
<P><A HREF="/">Return to the Welcome page</A> &middot; <A HREF="/CFIDE/administrator/index.cfm">Open the Administrator</A>
</FONT>
</BODY></HTML>
