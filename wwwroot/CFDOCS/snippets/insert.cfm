<CFSET Phone = "6175551234">
<CFSET Pretty = Insert(") ", Phone, 3)>
<CFSET Pretty = Insert("-", Pretty, 8)>
<CFSET Pretty = Insert("(", Pretty, 0)>
<CFOUTPUT>
<P>Raw: #Phone#<BR>
Formatted: #Pretty#</P>
<P>Appending: #Insert(".cfm", "index", 5)#</P>
</CFOUTPUT>
