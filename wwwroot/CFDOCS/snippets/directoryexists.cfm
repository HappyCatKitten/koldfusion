<CFSET Here = GetDirectoryFromPath(GetCurrentTemplatePath())>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Path</TH><TH>DirectoryExists</TH></TR>
<TR><TD>#Here#</TD><TD>#DirectoryExists(Here)#</TD></TR>
<TR><TD>#GetTempDirectory()#</TD><TD>#DirectoryExists(GetTempDirectory())#</TD></TR>
<TR><TD>#ExpandPath("NoSuchFolder")#</TD><TD>#DirectoryExists(ExpandPath("NoSuchFolder"))#</TD></TR>
<TR><TD>#GetCurrentTemplatePath()# (a file)</TD><TD>#DirectoryExists(GetCurrentTemplatePath())#</TD></TR>
</TABLE>
</CFOUTPUT>
