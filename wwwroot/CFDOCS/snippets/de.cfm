<CFSET Quote = 'Andreessen said "Netscape everywhere"'>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Expression</TH><TH>Result</TH></TR>
<TR><TD>DE("Hello")</TD><TD>#DE("Hello")#</TD></TR>
<TR><TD>DE(Quote)</TD><TD>#HTMLEditFormat(DE(Quote))#</TD></TR>
<TR><TD>Evaluate(DE(Quote))</TD><TD>#HTMLEditFormat(Evaluate(DE(Quote)))#</TD></TR>
<TR><TD>IIf(Year(Now()) GT 1999, DE("Y2K survived"), DE("Party!"))</TD>
    <TD>#IIf(Year(Now()) GT 1999, DE("Y2K survived"), DE("Party!"))#</TD></TR>
</TABLE>
</CFOUTPUT>
