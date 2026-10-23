<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Call</TH><TH>Result</TH></TR>
<TR><TD>JavaCast("int", 42.9)</TD><TD>#JavaCast("int", 42.9)#</TD></TR>
<TR><TD>JavaCast("double", "3.14")</TD><TD>#JavaCast("double", "3.14")#</TD></TR>
<TR><TD>JavaCast("String", 1999)</TD><TD>#JavaCast("String", 1999)#</TD></TR>
<TR><TD>JavaCast("bool", 1)</TD><TD>#JavaCast("bool", 1)#</TD></TR>
</TABLE>
</CFOUTPUT>
<CFTRY>
  <!--- String.valueOf has an int, a double, a boolean and an Object version --->
  <CFSET S = CreateObject("JAVA", "java.lang.String")>
  <CFOUTPUT>
  <P>valueOf(int 7) = #S.valueOf(JavaCast("int", 7))#<BR>
  valueOf(double 7) = #S.valueOf(JavaCast("double", 7))#<BR>
  valueOf(boolean) = #S.valueOf(JavaCast("bool", "yes"))#</P>
  </CFOUTPUT>
  <CFCATCH TYPE="Object">
    <CFOUTPUT><P>Calling Java: <I>#CFCATCH.Message#</I></P></CFOUTPUT>
  </CFCATCH>
</CFTRY>
