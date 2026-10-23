<CFSET Text = "Hello, world. Goodbye, Y2K bug!">
<CFOUTPUT>
<UL>
<LI>Up to the first comma: #SpanExcluding(Text, ",")#
<LI>Up to the first punctuation: #SpanExcluding(Text, ",.!?")#
<LI>User part of webmaster@localhost: #SpanExcluding("webmaster@localhost", "@")#
</UL>
</CFOUTPUT>
