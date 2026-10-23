<CFSET Path = "/CFDOCS/snippets/listfirst.cfm">
<CFSET Email = "webmaster@localhost">
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Expression</TH><TH>Result</TH></TR>
<TR><TD>ListFirst("Larry,Moe,Curly")</TD><TD>#ListFirst("Larry,Moe,Curly")#</TD></TR>
<TR><TD>ListFirst(Path, "/")</TD><TD>#ListFirst(Path, "/")#</TD></TR>
<TR><TD>ListFirst(Email, "@")</TD><TD>#ListFirst(Email, "@")#</TD></TR>
<TR><TD>ListFirst("")</TD><TD>[#ListFirst("")#]</TD></TR>
</TABLE>
</CFOUTPUT>
