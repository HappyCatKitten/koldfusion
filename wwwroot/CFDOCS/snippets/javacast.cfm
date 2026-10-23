<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Call</TH><TH>Result</TH></TR>
<TR><TD>JavaCast("int", 42)</TD><TD>#JavaCast("int", 42)#</TD></TR>
<TR><TD>JavaCast("double", "3.14")</TD><TD>#JavaCast("double", "3.14")#</TD></TR>
<TR><TD>JavaCast("String", 1999)</TD><TD>#JavaCast("String", 1999)#</TD></TR>
</TABLE>
</CFOUTPUT>
<CFTRY>
  <CFSET Vec = CreateObject("JAVA", "java.util.Vector")>
<CFCATCH TYPE="Object">
  <CFOUTPUT><P>Creating the Java object to pass them to: <I>#CFCATCH.Message#</I></CFOUTPUT>
</CFCATCH>
</CFTRY>
