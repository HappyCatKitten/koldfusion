<CFSET Cart = ArrayNew(1)>
<CFSET Grid = ArrayNew(2)>
<CFSET Customer = StructNew()>
<CFSET Name = "Floyd">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Variable</TH><TH>IsArray</TH><TH>IsArray(v, 1)</TH><TH>IsArray(v, 2)</TH></TR>
<CFLOOP INDEX="v" LIST="Cart,Grid,Customer,Name">
<CFSET val = Evaluate(v)>
<CFOUTPUT><TR><TD>#v#</TD><TD>#IsArray(val)#</TD><TD>#IsArray(val, 1)#</TD><TD>#IsArray(val, 2)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
