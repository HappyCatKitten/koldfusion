<CFOUTPUT>
<P>The current locale is <B>#GetLocale()#</B>.</P>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Function</TH><TH>Result</TH></TR>
<TR><TD>LSDateFormat(Now(), "long")</TD><TD>#LSDateFormat(Now(), "long")#</TD></TR>
<TR><TD>LSTimeFormat(Now())</TD><TD>#LSTimeFormat(Now())#</TD></TR>
<TR><TD>LSCurrencyFormat(1999.99)</TD><TD>#LSCurrencyFormat(1999.99)#</TD></TR>
</TABLE>
</CFOUTPUT>
