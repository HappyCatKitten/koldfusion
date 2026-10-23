<CFSET Base = CreateDate(2000, 1, 31)>
<CFOUTPUT>
<P>Starting from #DateFormat(Base, "mmmm d, yyyy")#:</P>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Expression</TH><TH>Result</TH></TR>
<CFLOOP INDEX="Part" LIST="yyyy,q,m,ww,d">
<TR><TD>DateAdd("#Part#", 1, Base)</TD>
    <TD>#DateFormat(DateAdd(Part, 1, Base), "mmm d, yyyy")#</TD></TR>
</CFLOOP>
<TR><TD>DateAdd("d", -31, Base)</TD><TD>#DateFormat(DateAdd("d", -31, Base), "mmm d, yyyy")#</TD></TR>
<TR><TD>DateAdd("h", 36, Base)</TD><TD>#DateAdd("h", 36, Base)#</TD></TR>
<TR><TD>DateAdd("n", 90, Base)</TD><TD>#DateAdd("n", 90, Base)#</TD></TR>
</TABLE>
</CFOUTPUT>
