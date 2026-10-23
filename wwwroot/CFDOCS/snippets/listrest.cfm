<CFSET Queue = "Alice,Bob,Carol,Dave">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Now serving</TH><TH>Still waiting</TH></TR>
<CFLOOP CONDITION="Len(Queue) GT 0">
<CFOUTPUT>
<TR><TD>#ListFirst(Queue)#</TD><TD>#ListRest(Queue)#&nbsp;</TD></TR>
</CFOUTPUT>
<CFSET Queue = ListRest(Queue)>
</CFLOOP>
</TABLE>
