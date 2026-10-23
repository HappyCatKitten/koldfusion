<CFSET Files = "Application.cfm,fileexists.cfm,missing.cfm">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>File</TH><TH>FileExists(ExpandPath(file))</TH></TR>
<CFLOOP LIST="#Files#" INDEX="f">
<CFOUTPUT><TR><TD>#f#</TD><TD>#FileExists(ExpandPath(f))#</TD></TR></CFOUTPUT>
</CFLOOP>
<CFOUTPUT><TR><TD>#GetTempDirectory()# (a directory)</TD><TD>#FileExists(GetTempDirectory())#</TD></TR></CFOUTPUT>
</TABLE>
