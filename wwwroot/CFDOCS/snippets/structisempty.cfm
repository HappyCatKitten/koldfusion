<CFSET Errors = StructNew()>
<CFPARAM NAME="URL.Email" DEFAULT="nobody">
<CFIF Find("@", URL.Email) EQ 0>
  <CFSET Errors.Email = "That does not look like an e-mail address.">
</CFIF>
<CFOUTPUT>
<CFIF StructIsEmpty(Errors)>
  <P>All fields are fine.</P>
<CFELSE>
  <P><B>Please fix #StructCount(Errors)# field(s):</B> #Errors.Email#</P>
</CFIF>
</CFOUTPUT>
