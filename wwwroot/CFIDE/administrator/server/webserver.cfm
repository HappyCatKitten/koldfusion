<!--- Web Server and SSL (a KoldFusion extra: ColdFusion 4.5 left this to IIS or Netscape Enterprise Server) --->
<cfset msg = "">
<cfif IsDefined("Form.Apply")>
	<cfset nums = "KeepAliveTimeout,KeepAliveMaxRequests,HeaderTimeout,MaxConnections,SSLPort">
	<cfset ok = 1>
	<cfloop list="#nums#" index="f"><cfif NOT IsNumeric(Form[f]) OR Form[f] LT 1 OR Form[f] GT 65535><cfset ok = 0></cfif></cfloop>
	<cfif ok>
		<cfloop list="KeepAliveTimeout,KeepAliveMaxRequests,HeaderTimeout,MaxConnections" index="f">
			<cfmodule template="../_tags/setreg.cfm" key="Server" entry="#f#" value="#Int(Form[f])#">
		</cfloop>
		<cfmodule template="../_tags/setreg.cfm" key="Server" entry="KeepAlive" value="#IIf(IsDefined('Form.KeepAlive'), 1, 0)#">
		<cfmodule template="../_tags/setreg.cfm" key="SSL" entry="Enabled" value="#IIf(IsDefined('Form.SSLEnabled'), 1, 0)#">
		<cfmodule template="../_tags/setreg.cfm" key="SSL" entry="Port" value="#Int(Form.SSLPort)#">
		<cfmodule template="../_tags/setreg.cfm" key="SSL" entry="CertificateFile" value="#Trim(Form.CertificateFile)#">
		<cfmodule template="../_tags/setreg.cfm" key="SSL" entry="KeyFile" value="#Trim(Form.KeyFile)#">
		<cfmodule template="../_tags/setreg.cfm" key="SSL" entry="RequestClientCertificates" value="#IIf(IsDefined('Form.RequestClientCertificates'), 1, 0)#">
		<cfmodule template="../_tags/setreg.cfm" key="SSL" entry="VerifyServerCertificates" value="#IIf(IsDefined('Form.VerifyServerCertificates'), 1, 0)#">
		<cfset msg = "The web server settings have been applied. Keep-alive settings apply to new connections; SSL listener changes take effect when the KoldFusion Application Server is restarted.">
	<cfelse>
		<cfset msg = "The timeouts, limits and the SSL port must be whole numbers between 1 and 65535.">
	</cfif>
</cfif>
<cfif IsDefined("Form.Generate")>
	<cfset gen = KFUSION_SSL("generate")>
	<cfset msg = gen.Message>
	<cfif gen.OK AND NOT FindNoCase("using it now", msg)><cfset msg = msg & " Restart the KoldFusion Application Server to start using it."></cfif>
</cfif>
<cfif IsDefined("Form.Restart")>
	<cfset KFUSION_RESTART()>
	<cfset msg = "The KoldFusion Application Server is restarting. Please wait a few seconds and reload this page.">
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="Server" variable="S">
<cfmodule template="../_tags/getreg.cfm" key="SSL" variable="L">
<cfparam name="S.KeepAlive" default="1">
<cfparam name="S.KeepAliveTimeout" default="15">
<cfparam name="S.KeepAliveMaxRequests" default="100">
<cfparam name="S.HeaderTimeout" default="20">
<cfparam name="S.MaxConnections" default="400">
<cfparam name="L.Enabled" default="1">
<cfparam name="L.Port" default="8543">
<cfparam name="L.CertificateFile" default="">
<cfparam name="L.KeyFile" default="">
<cfparam name="L.RequestClientCertificates" default="0">
<cfparam name="L.VerifyServerCertificates" default="1">
<cfset ssl = KFUSION_SSL()>
<cfset pageTitle = "Web Server and SSL">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="webserver.cfm" METHOD="POST">
<P><TABLE WIDTH="90%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>HTTP Connections</B></FONT></TD></TR></TABLE>

<P>#Request.f#<INPUT TYPE="checkbox" NAME="KeepAlive" VALUE="1"<cfif S.KeepAlive EQ 1> CHECKED</cfif>>
<B>Allow persistent (keep-alive) connections</B><BR>
HTTP/1.1 browsers, and HTTP/1.0 browsers that ask for keep-alive, can send many requests over one connection instead of
dialing in again for every image. Requests may be pipelined; they are answered in order.</FONT>

<P>#Request.f#<B>Close idle connections after</B> <INPUT TYPE="text" NAME="KeepAliveTimeout" VALUE="#S.KeepAliveTimeout#" SIZE=3> <B>seconds</B>
&nbsp;&nbsp; <B>and after</B> <INPUT TYPE="text" NAME="KeepAliveMaxRequests" VALUE="#S.KeepAliveMaxRequests#" SIZE=4> <B>requests</B><BR>
Every open connection keeps a server thread waiting. When more than three quarters of the connection limit is in use, new
responses close their connection instead.</FONT>

<P>#Request.f#<B>Request header timeout</B> <INPUT TYPE="text" NAME="HeaderTimeout" VALUE="#S.HeaderTimeout#" SIZE=3> <B>seconds</B>
&nbsp;&nbsp; <B>Maximum connections</B> <INPUT TYPE="text" NAME="MaxConnections" VALUE="#S.MaxConnections#" SIZE=4><BR>
A browser must send its complete request headers (and finish the SSL handshake) within this time, so a client that
trickles in one byte at a time cannot tie up the server. Request bodies get 30 seconds plus one second for every 64 KB.
Connections beyond the maximum are answered with "503 Service Unavailable".</FONT>

<P><TABLE WIDTH="90%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>Secure Sockets Layer (SSL)</B></FONT></TD></TR></TABLE>
<P><TABLE BORDER=0 CELLPADDING=3>
<TR><TD>#Request.f#SSL libraries</FONT></TD><TD>#Request.f#<cfif ssl.Available>#ssl.Library# <TT>(#ssl.LibraryFile#)</TT><cfelse><FONT COLOR="##CC0000"><B>Not available</B></FONT> - #ssl.Reason#. Install OpenSSL (libssl.so.3 or libssl.so.1.1) to use SSL.</cfif></FONT></TD></TR>
<TR><TD>#Request.f#Secure listener</FONT></TD><TD>#Request.f#<cfif ssl.ListeningPort GT 0>Listening on <TT>https://#CGI.SERVER_NAME#:#ssl.ListeningPort#/</TT><cfelse>Off</cfif></FONT></TD></TR>
<TR><TD>#Request.f#This request</FONT></TD><TD>#Request.f#<cfif CGI.HTTPS EQ "on">Secure (#CGI.CERT_KEYSIZE#-bit encryption)<cfelse>Not secure</cfif></FONT></TD></TR>
</TABLE>

<P>#Request.f#<INPUT TYPE="checkbox" NAME="SSLEnabled" VALUE="1"<cfif L.Enabled EQ 1> CHECKED</cfif>>
<B>Enable the secure listener on port</B> <INPUT TYPE="text" NAME="SSLPort" VALUE="#L.Port#" SIZE=5><BR>
Pages requested with https:// see CGI.HTTPS = "on", CGI.SERVER_PORT_SECURE = 1 and the CGI.CERT_ variables, as they would
under IIS 4.0. The <TT>kfserver --ssl-port</TT> option overrides the port (0 turns the listener off).</FONT>

<P>#Request.f#<B>Server certificate (PEM)</B><BR>
<INPUT TYPE="text" NAME="CertificateFile" VALUE="#HTMLEditFormat(L.CertificateFile)#" SIZE=60><BR>
<B>Private key (PEM)</B><BR>
<INPUT TYPE="text" NAME="KeyFile" VALUE="#HTMLEditFormat(L.KeyFile)#" SIZE=60><BR>
A virtual site can have a certificate of its own: put <TT>&lt;name&gt;.localhost.crt</TT> and <TT>.key</TT> in the
<TT>ssl</TT> folder of the install directory, and browsers that send the host name (SNI) will get it.</FONT>

<P><TABLE BORDER=0 CELLPADDING=3>
<cfif ssl.CertificateExists AND Len(ssl.Subject)>
<TR><TD>#Request.f#Subject</FONT></TD><TD>#Request.f##HTMLEditFormat(ssl.Subject)#</FONT></TD></TR>
<TR><TD>#Request.f#Issued by</FONT></TD><TD>#Request.f##HTMLEditFormat(ssl.Issuer)#<cfif ssl.Issuer EQ ssl.Subject> (self-signed: browsers will warn about it)</cfif></FONT></TD></TR>
<TR><TD>#Request.f#Key size</FONT></TD><TD>#Request.f##ssl.KeySize# bits</FONT></TD></TR>
<cfif IsDate(ssl.Expires)><TR><TD>#Request.f#Expires</FONT></TD><TD>#Request.f##DateFormat(ssl.Expires, "mmmm d, yyyy")#</FONT></TD></TR></cfif>
<cfelseif ssl.CertificateExists>
<TR><TD COLSPAN=2>#Request.f#The certificate file exists but could not be read.</FONT></TD></TR>
<cfelse>
<TR><TD COLSPAN=2>#Request.f#<FONT COLOR="##CC0000">There is no certificate yet.</FONT></FONT></TD></TR>
</cfif>
</TABLE>
<cfif Len(ssl.OpenSSLCommand)>
<P>#Request.f#<INPUT TYPE="submit" NAME="Generate" VALUE="Generate Self-Signed Certificate"
 onClick="return confirm('Replace the server certificate with a new self-signed certificate for localhost?')"><BR>
Uses <TT>#ssl.OpenSSLCommand#</TT> to make a certificate for localhost, *.localhost, 127.0.0.1 and every virtual site,
issued by "Gibson Mainframe Co." and valid for ten years. In 1999 you would have mailed a certificate request to VeriSign.</FONT>
<cfelse>
<P>#Request.f#To make a certificate by hand:<BR>
<TT>openssl req -x509 -newkey rsa:2048 -sha256 -days 3650 -nodes -keyout kfserver.key -out kfserver.crt
-subj "/CN=localhost/O=Gibson Mainframe Co." -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1"</TT></FONT>
</cfif>

<P>#Request.f#<INPUT TYPE="checkbox" NAME="RequestClientCertificates" VALUE="1"<cfif L.RequestClientCertificates EQ 1> CHECKED</cfif>>
<B>Ask browsers for a client certificate</B><BR>
Any certificate is accepted; pages can read it from CGI.CERT_SUBJECT, CGI.CERT_ISSUER and CGI.CERT_SERIALNUMBER, and
CGI.CERT_FLAGS is 1 when one was sent (3 when its issuer is not trusted).</FONT>

<P>#Request.f#<INPUT TYPE="checkbox" NAME="VerifyServerCertificates" VALUE="1"<cfif L.VerifyServerCertificates EQ 1> CHECKED</cfif>>
<B>Verify server certificates in CFHTTP</B><BR>
CFHTTP checks the certificate of an https:// server against the system's certificate authorities (and trusts this
server's own certificate). Clear this to accept any certificate, as most 1999 software did; a single tag can also say
CHECKCERTIFICATE="No".</FONT>

<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Apply" VALUE="Apply"> <INPUT TYPE="reset" VALUE="Cancel">
&nbsp;&nbsp;&nbsp;&nbsp;<INPUT TYPE="submit" NAME="Restart" VALUE="Restart Server..." onClick="return confirm('Restart the KoldFusion Application Server now?')">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
