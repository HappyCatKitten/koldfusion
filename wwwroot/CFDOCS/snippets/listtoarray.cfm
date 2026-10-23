<CFSET Tags = "CFQUERY,CFOUTPUT,,CFIF,CFLOOP">
<CFSET TagArray = ListToArray(Tags)>
<CFOUTPUT>
<P>The list has #ListLen(Tags)# elements; the array has #ArrayLen(TagArray)#.</P>
</CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Index</TH><TH>Element</TH></TR>
<CFLOOP INDEX="I" FROM="1" TO="#ArrayLen(TagArray)#">
<CFOUTPUT><TR><TD>#I#</TD><TD>#TagArray[I]#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<CFSET Sorted = ArraySort(TagArray, "text")>
<CFOUTPUT><P>Sorted and back to a list: #ArrayToList(TagArray, ", ")#</P></CFOUTPUT>
