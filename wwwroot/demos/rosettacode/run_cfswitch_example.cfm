<!--- KoldFusion Demo Gallery companion (not from Rosetta Code).
      cfswitch_example.cfm is a skeleton that expects a variable X to exist.
      This runner sets X from the URL (default 2) and CFINCLUDEs the original. --->
<cfparam name="URL.x" default="2">
<cfset x = URL.x>
<html>
<head><title>CFSWITCH skeleton</title></head>
<body bgcolor="#FFFFFF">
<font face="Arial, Helvetica" size="2">
<h2>Conditional structures: CFSWITCH</h2>
<p>Try <a href="run_cfswitch_example.cfm?x=1">x=1</a> |
<a href="run_cfswitch_example.cfm?x=2">x=2</a> |
<a href="run_cfswitch_example.cfm?x=99">x=99</a>.
Every branch of the Rosetta skeleton says "do something" - that's the joke.</p>
<cfoutput><p><b>x = #HTMLEditFormat(x)#</b>, the included skeleton says:</p></cfoutput>
<blockquote><b><cfinclude template="cfswitch_example.cfm"></b></blockquote>
</font>
</body>
</html>
