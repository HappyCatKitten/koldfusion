<!--- footer.cfm - closes every HRApp page --->
<CFSET ThisFile = ReplaceNoCase(CGI.SCRIPT_NAME, "/CFDOCS/exampleapp/", "")>
<CFOUTPUT>
<BR>
<HR SIZE=1 NOSHADE>
<FONT FACE="#Request.Font#" SIZE=1 COLOR="##666666">
Data source: <B>#Request.DSN#</B> &middot;
<A HREF="javascript:void(window.open('/CFDOCS/exampleapp/sourcewindow.cfm?file=#URLEncodedFormat(ThisFile)#','cfsource','width=680,height=500,scrollbars=yes,resizable=yes'))">View the source of this page</A> &middot;
<A HREF="/CFDOCS/examplehome.cfm">Example Applications</A>
</FONT>
</BODY>
</HTML>
</CFOUTPUT>
