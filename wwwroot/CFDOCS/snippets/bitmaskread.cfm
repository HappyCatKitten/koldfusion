<!--- Pack a date into one integer: day in bits 0-4, month in bits 5-8, year offset in bits 9-15 --->
<CFSET Packed = 31 + 12 * 32 + 99 * 512>
<CFOUTPUT>
<P>Packed value: #Packed# (binary <TT>#FormatBaseN(Packed, 2)#</TT>)
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Field</TH><TH>Call</TH><TH>Value</TH></TR>
<TR><TD>Day</TD><TD><TT>BitMaskRead(Packed, 0, 5)</TT></TD><TD>#BitMaskRead(Packed, 0, 5)#</TD></TR>
<TR><TD>Month</TD><TD><TT>BitMaskRead(Packed, 5, 4)</TT></TD><TD>#BitMaskRead(Packed, 5, 4)#</TD></TR>
<TR><TD>Year - 1900</TD><TD><TT>BitMaskRead(Packed, 9, 7)</TT></TD><TD>#BitMaskRead(Packed, 9, 7)#</TD></TR>
</TABLE>
</CFOUTPUT>
