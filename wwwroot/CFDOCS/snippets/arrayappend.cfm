<!--- Build a shopping list one item at a time --->
<CFSET Groceries = ArrayNew(1)>
<CFSET Temp = ArrayAppend(Groceries, "Coffee")>
<CFSET Temp = ArrayAppend(Groceries, "Bagels")>
<CFSET Temp = ArrayAppend(Groceries, "Floppy disks")>

<CFOUTPUT>
<P>The list now has #ArrayLen(Groceries)# items:</P>
<OL>
<CFLOOP INDEX="i" FROM="1" TO="#ArrayLen(Groceries)#">
  <LI>#Groceries[i]#
</CFLOOP>
</OL>
</CFOUTPUT>
