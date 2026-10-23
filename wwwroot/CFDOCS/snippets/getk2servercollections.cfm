<CFSET Colls = GetK2ServerCollections()>
<CFOUTPUT>
<P>The K2 Server serves #ListLen(Colls)# collection(s)<CFIF Len(Colls)>: #Colls#</CFIF>.</P>
</CFOUTPUT>
