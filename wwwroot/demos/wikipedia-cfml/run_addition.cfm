<!--- KoldFusion Demo Gallery companion (not from Wikipedia).
      call_addition.cfm is verbatim from the article and never prints its result;
      the custom tag it calls (addition.cfm) uses CFMX-style "/>" closers. This
      runner calls the CF 4.5 port (addition45.cfm) the same way and shows the
      CALLER-scope result the tag hands back. --->
<cfparam name="URL.first" default="1">
<cfparam name="URL.second" default="2">
<cfif NOT IsNumeric(URL.first)><cfset URL.first = 1></cfif>
<cfif NOT IsNumeric(URL.second)><cfset URL.second = 2></cfif>
<html>
<head><title>CF_ADDITION - the Wikipedia custom tag</title></head>
<body bgcolor="#FFFFFF">
<font face="Arial, Helvetica" size="2">
<h2>&lt;CF_ADDITION&gt;</h2>
<p>The custom-tag example from Wikipedia's "ColdFusion Markup Language" article:
the tag adds ATTRIBUTES.first and ATTRIBUTES.second and writes the sum back
to the calling page as CALLER.addition.</p>

<cf_addition45 first="#URL.first#" second="#URL.second#">

<cfoutput>
<p><tt>&lt;cf_addition first="#URL.first#" second="#URL.second#"&gt;</tt>
&nbsp;=&gt;&nbsp; <b>addition = #addition#</b></p>
</cfoutput>

<form action="run_addition.cfm" method="get">
<cfoutput>
<input type="text" name="first" size="5" value="#HTMLEditFormat(URL.first)#"> +
<input type="text" name="second" size="5" value="#HTMLEditFormat(URL.second)#">
</cfoutput>
<input type="submit" value=" = ">
</form>
</font>
</body>
</html>
