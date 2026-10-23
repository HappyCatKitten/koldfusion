<CFSET Encoded = "name=Tom%20%26%20Jerry&city=New+York&note=100%25+sure">
<UL>
<CFLOOP LIST="#Encoded#" DELIMITERS="&" INDEX="pair">
<CFOUTPUT><LI>#ListFirst(pair, "=")# = #URLDecode(ListLast(pair, "="))#</CFOUTPUT>
</CFLOOP>
</UL>
