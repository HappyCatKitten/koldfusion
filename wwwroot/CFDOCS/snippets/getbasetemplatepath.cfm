<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Called from</TH><TH>GetCurrentTemplatePath()</TH><TH>GetBaseTemplatePath()</TH></TR>
<CFOUTPUT>
<TR><TD>getbasetemplatepath.cfm (this page)</TD>
<TD>#GetFileFromPath(GetCurrentTemplatePath())#</TD>
<TD>#GetFileFromPath(GetBaseTemplatePath())#</TD></TR>
</CFOUTPUT>
<CFINCLUDE TEMPLATE="sn_syswhere.cfm">
</TABLE>
<CFOUTPUT><P>Full path: #GetBaseTemplatePath()#</CFOUTPUT>
