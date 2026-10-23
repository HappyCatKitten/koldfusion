<CFSET Inbox = ArrayNew(1)>
<CFOUTPUT>
<P>Inbox empty? <B>#ArrayIsEmpty(Inbox)#</B></P>
<CFSET Temp = ArrayAppend(Inbox, "You've got mail!")>
<P>After one message arrives: <B>#ArrayIsEmpty(Inbox)#</B></P>
</CFOUTPUT>
