<CFPARAM NAME="URL.Comment" DEFAULT="I <B>love</B> this site & its ""cool"" tags!">
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Raw output</TH><TD>#URL.Comment#</TD></TR>
<TR><TH>HTMLEditFormat</TH><TD>#HTMLEditFormat(URL.Comment)#</TD></TR>
</TABLE>
<FORM ACTION="htmleditformat.cfm" METHOD="get">
<INPUT TYPE="text" NAME="Comment" SIZE="50" VALUE="#HTMLEditFormat(URL.Comment)#">
<INPUT TYPE="submit" VALUE="Try it">
</FORM>
</CFOUTPUT>
