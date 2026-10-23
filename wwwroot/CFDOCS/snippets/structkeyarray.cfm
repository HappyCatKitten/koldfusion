<CFSET Fruit = StructNew()>
<CFSET Fruit.Pear = 3>
<CFSET Fruit.Apple = 7>
<CFSET Fruit.Kiwi = 1>
<CFSET Keys = StructKeyArray(Fruit)>
<CFSET Temp = ArraySort(Keys, "textnocase")>
<TABLE BORDER=1 CELLPADDING=3>
<CFLOOP INDEX="i" FROM="1" TO="#ArrayLen(Keys)#">
<CFOUTPUT><TR><TD>#Keys[i]#</TD><TD ALIGN="RIGHT">#Fruit[Keys[i]]#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
