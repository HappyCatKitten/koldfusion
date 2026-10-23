<CFSET Padded = "     Hello, world!     ">
<CFOUTPUT>
<PRE>
Original: [#Padded#]
LTrim:    [#LTrim(Padded)#]
RTrim:    [#RTrim(Padded)#]
Trim:     [#Trim(Padded)#]
</PRE>
</CFOUTPUT>
