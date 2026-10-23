<CFSET Padded = "Gibson Mainframe Co.          ">
<CFOUTPUT>
<P>Before: [#Padded#] is #Len(Padded)# characters</P>
<P>After RTrim: [#RTrim(Padded)#] is #Len(RTrim(Padded))# characters</P>
</CFOUTPUT>
