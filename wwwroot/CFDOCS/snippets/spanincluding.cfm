<CFSET Digits = "0123456789">
<CFSET Inputs = "1999 Party,42nd Street,No numbers here">
<UL>
<CFLOOP LIST="#Inputs#" INDEX="s">
<CFOUTPUT><LI>"#s#" starts with [#SpanIncluding(s, Digits)#]</CFOUTPUT>
</CFLOOP>
</UL>
