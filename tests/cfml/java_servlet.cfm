<!--- requires: java --->
<!--- CFSERVLET / CFSERVLETPARAM: parameters, attributes by reference, CFSERVLET.Output and headers --->
<cfset visits = 4>
<cfset tags = ListToArray("cfml,java")>
<CFSERVLET CODE="HelloServlet" WRITEOUTPUT="No" TIMEOUT="20" JRUNPROXY="127.0.0.1:8081">
	<CFSERVLETPARAM NAME="name" VALUE="Ben">
	<CFSERVLETPARAM NAME="visits" VARIABLE="visits" TYPE="INT">
	this text is ignored
</CFSERVLET>
<cfoutput>
output starts: #Left(Trim(Replace(CFSERVLET.Output, Chr(10), " ", "ALL")), 60)#
contains greeting: #CFSERVLET.Output CONTAINS "Hello, Ben!"#
header X-Servlet=#CFSERVLET["X-Servlet"]# Content-Type=#CFSERVLET["Content-Type"]# status=#CFSERVLET.StatusCode#
visits after the servlet: #visits#
</cfoutput>
<CFSERVLET CODE="SnoopServlet">
	<CFSERVLETPARAM NAME="color" VALUE="teal">
	<CFSERVLETPARAM NAME="tags" VARIABLE="tags">
	<CFSERVLETPARAM NAME="when" VARIABLE="visits" TYPE="DOUBLE">
</CFSERVLET>
<cftry><CFSERVLET CODE="NoSuchServlet"></CFSERVLET><cfcatch type="Application"><cfoutput>#cfcatch.message#</cfoutput></cfcatch></cftry>
<cftry><CFSERVLET CODE="HelloServlet"><CFSERVLETPARAM NAME="x"></CFSERVLET><cfcatch type="Application"><cfoutput>#cfcatch.message#</cfoutput></cfcatch></cftry>
<cftry><CFSERVLET CODE="HelloServlet"><CFSERVLETPARAM NAME="x" VARIABLE="visits" TYPE="BLOB"></CFSERVLET><cfcatch type="Application"><cfoutput>#cfcatch.message#</cfoutput></cfcatch></cftry>
