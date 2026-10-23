<CFSET Tools = "hammer,crowbar,Screwdriver,wrench">
<CFOUTPUT>
<P>List: #Tools#</P>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Expression</TH><TH>Result</TH></TR>
<TR><TD>ListContains(Tools, "bar")</TD><TD>#ListContains(Tools, "bar")#</TD></TR>
<TR><TD>ListContains(Tools, "screw")</TD><TD>#ListContains(Tools, "screw")#</TD></TR>
<TR><TD>ListContains(Tools, "Screw")</TD><TD>#ListContains(Tools, "Screw")#</TD></TR>
<TR><TD>ListFind(Tools, "bar")</TD><TD>#ListFind(Tools, "bar")#</TD></TR>
</TABLE>
</CFOUTPUT>
