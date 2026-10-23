<!--- ch7_errorpage.cfm: install an error template, then (optionally) fail --->
<CFERROR TYPE="Request" TEMPLATE="ch7_error.cfm" MAILTO="webmaster@localhost">
<CFPARAM NAME="URL.Break" DEFAULT="No">

<P>This page has a custom error template installed.</P>
<CFIF URL.Break IS "Yes">
  <!--- Refer to a variable that does not exist --->
  <CFOUTPUT>#NoSuchVariable#</CFOUTPUT>
<CFELSE>
  <P><A HREF="ch7_errorpage.cfm?Break=Yes">Cause an error</A> to see it.</P>
</CFIF>
