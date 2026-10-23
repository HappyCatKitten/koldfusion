<!--- CFHTTP demo --->
<cfset pageTitle = "CFHTTP: Fetch a Web Page">
<cfparam name="Form.url" default="http://127.0.0.1:#CGI.SERVER_PORT#/">
<cfinclude template="_top.cfm">
<cfoutput>
<FORM ACTION="fetch.cfm" METHOD="POST">URL: <INPUT TYPE="text" NAME="url" VALUE="#HTMLEditFormat(Form.url)#" SIZE=50> <INPUT TYPE="submit" VALUE="Fetch">
<BR><FONT SIZE=1>http:// only &mdash; SSL needs the Netscape Enterprise Server and a $349 certificate.</FONT></FORM>
</cfoutput>
<cfhttp url="#Form.url#" method="get" timeout="10" resolveurl="yes">
<cfset title = "">
<cfset start = FindNoCase("<title>", CFHTTP.FileContent)>
<cfif start><cfset stop = FindNoCase("</title>", CFHTTP.FileContent, start)><cfif stop><cfset title = Mid(CFHTTP.FileContent, start + 7, stop - start - 7)></cfif></cfif>
<cfoutput>
<TABLE BORDER=1 CELLPADDING=5 CELLSPACING=0 BGCOLOR="##FFFFEE">
<TR><TD><B>Status</B></TD><TD>#CFHTTP.StatusCode#</TD></TR>
<TR><TD><B>MIME type</B></TD><TD>#CFHTTP.MimeType#</TD></TR>
<TR><TD><B>Title</B></TD><TD>#HTMLEditFormat(title)#</TD></TR>
<TR><TD><B>Size</B></TD><TD>#NumberFormat(Len(CFHTTP.FileContent), ",")# bytes</TD></TR>
<TR><TD VALIGN=TOP><B>Headers</B></TD><TD><FONT SIZE=1><cfloop collection="#CFHTTP.ResponseHeader#" item="h">#h#: #HTMLEditFormat(CFHTTP.ResponseHeader[h])#<BR></cfloop></FONT></TD></TR>
</TABLE>
<P>First 600 characters:</P>
<TABLE BORDER=1 CELLPADDING=6 BGCOLOR="##EEEEEE"><TR><TD><FONT FACE="Courier New" SIZE=1>#HTMLEditFormat(Left(CFHTTP.FileContent, 600))#</FONT></TD></TR></TABLE>
</cfoutput>
<cfinclude template="_bottom.cfm">
