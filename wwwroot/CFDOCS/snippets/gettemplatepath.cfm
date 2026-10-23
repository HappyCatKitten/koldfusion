<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>GetTemplatePath()</TD><TD>#GetTemplatePath()#</TD></TR>
<TR><TD>GetBaseTemplatePath()</TD><TD>#GetBaseTemplatePath()#</TD></TR>
<TR><TD>Same?</TD><TD>#YesNoFormat(GetTemplatePath() IS GetBaseTemplatePath())#</TD></TR>
</TABLE>
</CFOUTPUT>
