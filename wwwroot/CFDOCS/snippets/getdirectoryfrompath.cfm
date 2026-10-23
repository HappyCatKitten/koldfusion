<CFSET Path = GetCurrentTemplatePath()>
<CFSET Spool = GetDirectoryFromPath(Path) & "mail/spool/Mail1.cfmail">
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Path</TH><TH>GetDirectoryFromPath</TH><TH>GetFileFromPath</TH></TR>
<TR><TD>#Path#</TD><TD>#GetDirectoryFromPath(Path)#</TD><TD>#GetFileFromPath(Path)#</TD></TR>
<TR><TD>#Spool#</TD><TD>#GetDirectoryFromPath(Spool)#</TD><TD>#GetFileFromPath(Spool)#</TD></TR>
</TABLE>
</CFOUTPUT>
