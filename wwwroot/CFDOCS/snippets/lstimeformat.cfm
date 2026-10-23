<CFSET T = CreateTime(16, 5, 30)>
<CFOUTPUT>
<P>Locale: #GetLocale()#</P>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Mask</TH><TH>Result</TH></TR>
<TR><TD>(none)</TD><TD>#LSTimeFormat(T)#</TD></TR>
<TR><TD>short</TD><TD>#LSTimeFormat(T, "short")#</TD></TR>
<TR><TD>medium</TD><TD>#LSTimeFormat(T, "medium")#</TD></TR>
<TR><TD>HH:mm</TD><TD>#LSTimeFormat(T, "HH:mm")#</TD></TR>
</TABLE>
</CFOUTPUT>
