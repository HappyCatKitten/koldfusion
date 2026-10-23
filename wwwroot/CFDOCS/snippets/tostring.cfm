<CFSET Bin = ToBinary(ToBase64("Hello from the binary side"))>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>ToString(binary)</TD><TD>#ToString(Bin)#</TD></TR>
<TR><TD>ToString(42 * 2)</TD><TD>#ToString(42 * 2)#</TD></TR>
<TR><TD>ToString(1 LT 2)</TD><TD>#ToString(1 LT 2)#</TD></TR>
<TR><TD>ToString(CreateDateTime(1999,12,31,23,59,59))</TD><TD>#ToString(CreateDateTime(1999,12,31,23,59,59))#</TD></TR>
</TABLE>
</CFOUTPUT>
