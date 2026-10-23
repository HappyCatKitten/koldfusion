<CFSETTING ENABLECFOUTPUTONLY="Yes">
This sentence is outside CFOUTPUT, so you will not see it.
<CFSET Today = Now()>
<CFQUERY NAME="Depts" DATASOURCE="cfsnippets">
SELECT Dept_Name, Location FROM Departments ORDER BY Dept_Name
</CFQUERY>
<CFOUTPUT>
<P>With ENABLECFOUTPUTONLY on, only CFOUTPUT text reaches the browser.
Today is #DateFormat(Today, "dddd, mmmm d, yyyy")#.</P>
<TABLE BORDER=1 CELLPADDING=3>
</CFOUTPUT>
<CFOUTPUT QUERY="Depts"><TR><TD>#Dept_Name#</TD><TD>#Location#</TD></TR></CFOUTPUT>
<CFOUTPUT></TABLE></CFOUTPUT>
<CFSETTING ENABLECFOUTPUTONLY="No">
<P>ENABLECFOUTPUTONLY is off again, so plain text shows up as usual.</P>
