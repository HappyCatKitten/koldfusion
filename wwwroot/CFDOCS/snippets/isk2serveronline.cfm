<CFIF IsK2ServerOnline()>
  <CFOUTPUT><P>The K2 Server is online with #ListLen(GetK2ServerCollections())# collection(s).</P></CFOUTPUT>
<CFELSE>
  <P>The K2 Server is offline; searches will fail.</P>
</CFIF>
