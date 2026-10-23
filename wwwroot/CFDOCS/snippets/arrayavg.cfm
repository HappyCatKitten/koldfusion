<!--- Average of five modem connection speeds --->
<CFSET Speeds = ListToArray("28.8,33.6,56,14.4,56")>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Speeds (Kbps)</TH><TD>#ArrayToList(Speeds, ", ")#</TD></TR>
<TR><TH>ArrayAvg</TH><TD>#NumberFormat(ArrayAvg(Speeds), "__.__")#</TD></TR>
<TR><TH>ArraySum</TH><TD>#ArraySum(Speeds)#</TD></TR>
</TABLE>
</CFOUTPUT>
