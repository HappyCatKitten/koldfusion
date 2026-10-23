<!--- Fetch the documentation home page from this very server --->
<CFSET Scheme = "http">
<CFIF CGI.HTTPS IS "on"><CFSET Scheme = "https"></CFIF>
<CFSET Target = "#Scheme#://127.0.0.1:#CGI.SERVER_PORT#/CFDOCS/index.cfm">
<CFTRY>
  <CFHTTP URL="#Target#" METHOD="GET" TIMEOUT="10" THROWONERROR="Yes"></CFHTTP>
  <CFSET Start = FindNoCase("<TITLE>", CFHTTP.FileContent)>
  <CFSET Stop = FindNoCase("</TITLE>", CFHTTP.FileContent)>
  <CFSET PageTitle = "(none)">
  <CFIF Start GT 0 AND Stop GT Start>
    <CFSET PageTitle = Mid(CFHTTP.FileContent, Start + 7, Stop - Start - 7)>
  </CFIF>
  <CFOUTPUT>
  <TABLE BORDER=1 CELLPADDING=3>
  <TR><TD>URL</TD><TD>#Target#</TD></TR>
  <TR><TD>StatusCode</TD><TD>#CFHTTP.StatusCode#</TD></TR>
  <TR><TD>MimeType</TD><TD>#CFHTTP.MimeType#</TD></TR>
  <TR><TD>Length</TD><TD>#Len(CFHTTP.FileContent)# characters</TD></TR>
  <TR><TD>Title</TD><TD>#HTMLEditFormat(PageTitle)#</TD></TR>
  </TABLE>
  </CFOUTPUT>
  <CFCATCH TYPE="Application">
    <CFOUTPUT>
    <P><B>Could not fetch #Target#.</B><BR>#CFCATCH.Detail#</P>
    <P>(Is the KoldFusion server listening? Busy signal on the modem?)</P>
    </CFOUTPUT>
  </CFCATCH>
</CFTRY>
