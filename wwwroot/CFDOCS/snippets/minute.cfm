<CFSET T = CreateDateTime(1999, 12, 31, 23, 45, 30)>
<CFOUTPUT>
<P>#T#</P>
<P>Hour #Hour(T)#, minute #Minute(T)#, second #Second(T)#.
Only #60 - Minute(T)# minutes until the year 2000!</P>
</CFOUTPUT>
