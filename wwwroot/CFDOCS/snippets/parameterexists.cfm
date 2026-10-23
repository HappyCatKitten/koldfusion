<CFSET Greeting = "Hello">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Old style</TH><TH>Result</TH><TH>New style</TH><TH>Result</TH></TR>
<CFOUTPUT>
<TR><TD><TT>ParameterExists(Greeting)</TT></TD><TD>#ParameterExists(Greeting)#</TD>
<TD><TT>IsDefined("Greeting")</TT></TD><TD>#IsDefined("Greeting")#</TD></TR>
<TR><TD><TT>ParameterExists(URL.Color)</TT></TD><TD>#ParameterExists(URL.Color)#</TD>
<TD><TT>IsDefined("URL.Color")</TT></TD><TD>#IsDefined("URL.Color")#</TD></TR>
<TR><TD><TT>ParameterExists(Form.Color)</TT></TD><TD>#ParameterExists(Form.Color)#</TD>
<TD><TT>IsDefined("Form.Color")</TT></TD><TD>#IsDefined("Form.Color")#</TD></TR>
</CFOUTPUT>
</TABLE>
