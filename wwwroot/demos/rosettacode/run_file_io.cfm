<!--- KoldFusion Demo Gallery companion (not from Rosetta Code).
      file_io.cfm silently copies input.txt to output.txt when input.txt exists.
      The gallery ships a sample input.txt; this runner deletes any old
      output.txt, CFINCLUDEs the original and then shows what was written. --->
<cfset here = GetDirectoryFromPath(GetCurrentTemplatePath())>
<cfif FileExists(here & "output.txt")>
	<cffile action="delete" file="#here#output.txt">
</cfif>
<cfinclude template="file_io.cfm">
<html>
<head><title>File input/output</title></head>
<body bgcolor="#FFFFFF">
<font face="Arial, Helvetica" size="2">
<h2>File input/output</h2>
<cfif FileExists(here & "output.txt")>
	<cffile action="read" file="#here#output.txt" variable="result">
	<p>file_io.cfm copied <tt>input.txt</tt> to <tt>output.txt</tt>. output.txt now contains:</p>
	<cfoutput>#HTMLCodeFormat(result)#</cfoutput>
<cfelse>
	<p><b>output.txt was not created.</b></p>
</cfif>
</font>
</body>
</html>
