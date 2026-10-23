<CFSET Text = "ColdFusion? coldfusion! COLDFUSION...">
<CFOUTPUT>
<P>Original: #Text#</P>
<P>ONE: #ReplaceNoCase(Text, "coldfusion", "KoldFusion")#</P>
<P>ALL: #ReplaceNoCase(Text, "coldfusion", "KoldFusion", "ALL")#</P>
<P>Replace (case-sensitive) ALL: #Replace(Text, "coldfusion", "KoldFusion", "ALL")#</P>
</CFOUTPUT>
