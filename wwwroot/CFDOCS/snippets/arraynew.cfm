<CFSET Week = ArrayNew(1)>
<CFSET Week[1] = "Monday">
<CFSET Week[2] = "Tuesday">
<CFSET Week[3] = "Wednesday">

<CFSET Copy = Week>
<CFSET Copy[1] = "Blue Monday">

<CFOUTPUT>
<P>Week has #ArrayLen(Week)# elements; IsArray(Week) is #IsArray(Week)#.</P>
<P>Week[1] = #Week[1]#<BR>
Copy[1] = #Copy[1]# (assignment made a separate copy)</P>
</CFOUTPUT>
