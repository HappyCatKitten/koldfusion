<CFSET Text = "Call 555-1234 or 555-9876, before 1/1/2000!">
<CFOUTPUT>
<P>Original: #Text#</P>
<UL>
<LI>Digits hidden: #REReplace(Text, "[[:digit:]]", "x", "ALL")#
<LI>First number swapped: #REReplace(Text, "([0-9]{3})-([0-9]{4})", "\2-\1")#
<LI>Date to ISO: #REReplace(Text, "([0-9]+)/([0-9]+)/([0-9]{4})", "\3-\1-\2")#
<LI>Tags stripped: #REReplace("<B>Bold</B> and <I>italic</I>", "<[^>]*>", "", "ALL")#
<LI>Spaces squeezed: #REReplace("too    many     spaces", "[[:space:]]+", " ", "ALL")#
</UL>
</CFOUTPUT>
