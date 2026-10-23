<!--- sn_errorpage.cfm is an Exception handler: a full CFML page --->
<CFERROR TYPE="Exception" TEMPLATE="sn_errorpage.cfm" MAILTO="webmaster@localhost">
<CFPARAM NAME="URL.Crash" DEFAULT="No">

<CFIF URL.Crash>
  <!--- This page is about to fail; the error page takes over --->
  <CFSET Modems = 0>
  <CFSET BaudPerModem = 56000 / Modems>
</CFIF>

<P>All is well. This page has registered <B>sn_errorpage.cfm</B> as its error handler.</P>
<P><A HREF="cferror.cfm?Crash=Yes">Make the page divide by zero</A> and see the custom error
page instead of the standard error message.</P>
