<!--- footer.cfm - closes the parks pages --->
<CFSET ThisFile = ReplaceNoCase(CGI.SCRIPT_NAME, "/CFDOCS/exampleapp/", "")>
<CFOUTPUT>
</FONT>
<BR><HR SIZE=1 NOSHADE COLOR="##006633">
<FONT FACE="Verdana, Arial, Helvetica" SIZE=1 COLOR="##666666">
<A HREF="index.cfm">Parks home</A> &middot;
<A HREF="javascript:void(window.open('/CFDOCS/exampleapp/sourcewindow.cfm?file=#URLEncodedFormat(ThisFile)#','cfsource','width=680,height=500,scrollbars=yes,resizable=yes'))">View the source of this page</A> &middot;
<A HREF="/CFDOCS/examplehome.cfm">Example Applications</A><BR>
Park descriptions are original text written for this KoldFusion sample. Check with the park before you travel!
</FONT>
</TD></TR></TABLE>
</BODY>
</HTML>
</CFOUTPUT>
