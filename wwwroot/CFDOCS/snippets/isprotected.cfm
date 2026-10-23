<CFSET Resource = "Payroll">
<CFOUTPUT>
<P>IsProtected("Application", "#Resource#") = #IsProtected("Application", Resource)#
<P>
<CFIF NOT IsProtected("Application", Resource)>
  The #Resource# application is open to everyone. Come on in.
<CFELSEIF IsAuthorized("Application", Resource)>
  Welcome, #AuthenticatedUser()#.
<CFELSE>
  Sorry, you need to log in to use #Resource#.
</CFIF>
</CFOUTPUT>
