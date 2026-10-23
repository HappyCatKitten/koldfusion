<CFSET Quote = "He said ""It's 1999!"" and left.">
<CFOUTPUT>
<P>Escaped: <TT>#HTMLEditFormat(JSStringFormat(Quote))#</TT></P>
<SCRIPT LANGUAGE="JavaScript">
var msg = '#JSStringFormat(Quote)#';
document.write('<P>Written by JavaScript: ' + msg + '</P>');
</SCRIPT>
</CFOUTPUT>
