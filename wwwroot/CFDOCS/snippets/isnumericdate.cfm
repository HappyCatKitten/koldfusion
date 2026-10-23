<CFSET Millennium = CreateDate(2000, 1, 1)>
<CFSET Eve = Millennium - 1>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Value</TH><TH>IsNumericDate</TH><TH>IsDate</TH></TR>
<CFOUTPUT>
<TR><TD>Millennium = CreateDate(2000, 1, 1)</TD><TD>#IsNumericDate(Millennium)#</TD><TD>#IsDate(Millennium)#</TD></TR>
<TR><TD>Eve = Millennium - 1 = #Eve#</TD><TD>#IsNumericDate(Eve)#</TD><TD>#IsDate(Eve)#</TD></TR>
<TR><TD>"12/31/1999"</TD><TD>#IsNumericDate("12/31/1999")#</TD><TD>#IsDate("12/31/1999")#</TD></TR>
<TR><TD>"Y2K"</TD><TD>#IsNumericDate("Y2K")#</TD><TD>#IsDate("Y2K")#</TD></TR>
</CFOUTPUT>
</TABLE>
<CFOUTPUT><P>Day #Eve# is #DateFormat(Eve, "dddd, mmmm d, yyyy")#. Party like it's day #Eve#!</CFOUTPUT>
