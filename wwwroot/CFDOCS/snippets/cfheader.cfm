<!--- Tell browsers and proxies not to keep a copy of this page --->
<CFSET Stamp = GetHTTPTimeString(Now())>
<CFHEADER NAME="Expires" VALUE="#Stamp#">
<CFHEADER NAME="Pragma" VALUE="no-cache">
<CFHEADER NAME="Cache-Control" VALUE="no-cache, must-revalidate">
<CFHEADER NAME="X-Snippet" VALUE="CFHEADER example">

<P>This response was sent with these extra headers:</P>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR BGCOLOR="##CCCCFF"><TH>Header</TH><TH>Value</TH></TR>
<TR><TD>Expires</TD><TD>#Stamp#</TD></TR>
<TR><TD>Pragma</TD><TD>no-cache</TD></TR>
<TR><TD>Cache-Control</TD><TD>no-cache, must-revalidate</TD></TR>
<TR><TD>X-Snippet</TD><TD>CFHEADER example</TD></TR>
</TABLE>
</CFOUTPUT>
