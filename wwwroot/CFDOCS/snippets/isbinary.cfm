<CFSET Text = "KoldFusion">
<CFSET Encoded = ToBase64(Text)>
<CFSET Bin = ToBinary(Encoded)>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Value</TH><TH>IsBinary</TH></TR>
<CFOUTPUT>
<TR><TD>"#Text#"</TD><TD>#IsBinary(Text)#</TD></TR>
<TR><TD>ToBase64: "#Encoded#"</TD><TD>#IsBinary(Encoded)#</TD></TR>
<TR><TD>ToBinary(that)</TD><TD>#IsBinary(Bin)#</TD></TR>
<TR><TD>ToString(that): "#ToString(Bin)#"</TD><TD>#IsBinary(ToString(Bin))#</TD></TR>
</CFOUTPUT>
</TABLE>
