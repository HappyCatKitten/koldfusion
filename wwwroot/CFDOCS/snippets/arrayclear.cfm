<CFSET Tasks = ListToArray("Patch Y2K bug,Back up server,Order pizza")>
<CFOUTPUT>
<P>Before: #ArrayLen(Tasks)# tasks (#ArrayToList(Tasks, "; ")#)</P>
<CFSET Temp = ArrayClear(Tasks)>
<P>After ArrayClear: #ArrayLen(Tasks)# tasks.
ArrayIsEmpty says <B>#ArrayIsEmpty(Tasks)#</B>.</P>
</CFOUTPUT>
