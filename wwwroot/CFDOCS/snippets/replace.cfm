<CFSET Text = "The Web is the future. The Web is now.">
<CFOUTPUT>
<P>Original: #Text#</P>
<P>ONE: #Replace(Text, "Web", "Internet")#</P>
<P>ALL: #Replace(Text, "Web", "Internet", "ALL")#</P>
<P>Case matters: #Replace(Text, "the", "a", "ALL")#</P>
<P>Removing: #Replace("555-12-34", "-", "", "ALL")#</P>
</CFOUTPUT>
