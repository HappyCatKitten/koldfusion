<!--- This page posts a form to itself; the ?Echo=Yes request just echoes what it got --->
<CFIF IsDefined("URL.Echo")>
  <CFPARAM NAME="Form.Name" DEFAULT="(missing)">
  <CFPARAM NAME="Cookie.Flavor" DEFAULT="(missing)">
  <CFOUTPUT>Name=#HTMLEditFormat(Form.Name)#; Cookie=#HTMLEditFormat(Cookie.Flavor)#</CFOUTPUT>
  <CFABORT>
</CFIF>
<CFSET Scheme = "http">
<CFIF CGI.HTTPS IS "on"><CFSET Scheme = "https"></CFIF>
<CFSET Target = "#Scheme#://127.0.0.1:#CGI.SERVER_PORT#/CFDOCS/snippets/cfhttpparam.cfm">
<CFTRY>
  <CFHTTP URL="#Target#" METHOD="POST" TIMEOUT="10" THROWONERROR="Yes">
    <CFHTTPPARAM TYPE="URL" NAME="Echo" VALUE="Yes">
    <CFHTTPPARAM TYPE="FormField" NAME="Name" VALUE="Ann & Andy">
    <CFHTTPPARAM TYPE="Cookie" NAME="Flavor" VALUE="Oatmeal">
    <CFHTTPPARAM TYPE="CGI" NAME="X-Requested-By" VALUE="KoldFusion">
  </CFHTTP>
  <CFOUTPUT>
  <TABLE BORDER=1 CELLPADDING=3>
  <TR><TD>Status</TD><TD>#CFHTTP.StatusCode#</TD></TR>
  <TR><TD>The other side saw</TD><TD>#Trim(CFHTTP.FileContent)#</TD></TR>
  </TABLE>
  </CFOUTPUT>
  <CFCATCH TYPE="Application">
    <CFOUTPUT><P><B>The request did not get through:</B> #CFCATCH.Detail#</P></CFOUTPUT>
  </CFCATCH>
</CFTRY>
