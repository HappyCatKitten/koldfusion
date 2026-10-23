<CFSET Card = "4111-1111-1111-1111">
<CFOUTPUT>
<P>Original: #Card#</P>
<P>Without the dashes, the hard way:
#RemoveChars(RemoveChars(RemoveChars(Card, 15, 1), 10, 1), 5, 1)#</P>
<P>Everything after the first group removed: #RemoveChars(Card, 5, 100)#</P>
</CFOUTPUT>
