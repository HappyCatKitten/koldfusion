<CFIF IsK2ServerDocCountExceeded()>
  <P><B>The Verity K2 Server is over its document limit.</B> Purge or delete a collection.</P>
<CFELSE>
  <CFOUTPUT><P>Room for #NumberFormat(GetK2ServerDocCountLimit() - GetK2ServerDocCount())# more documents.</P></CFOUTPUT>
</CFIF>
