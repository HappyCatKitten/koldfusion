<CFIF IsAuthenticated()>
  <CFOUTPUT><P>#AuthenticatedUser()# logged in to the #AuthenticatedContext()# context.</CFOUTPUT>
<CFELSE>
  <CFOUTPUT><P>Not logged in; AuthenticatedContext() returns "#AuthenticatedContext()#".</CFOUTPUT>
</CFIF>
