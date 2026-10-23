<!--- Try both kinds of impersonation and report what happens --->
<TABLE BORDER=1 CELLPADDING=4>
<TR><TH>TYPE</TH><TH>Result</TH></TR>
<CFLOOP LIST="CF,OS" INDEX="ImpType">
  <CFOUTPUT><TR><TD>#ImpType#</TD><TD></CFOUTPUT>
  <CFTRY>
    <CFIMPERSONATE SECURITYCONTEXT="Snippets" USERNAME="reports"
        PASSWORD="reports" TYPE="#ImpType#">
      <CFOUTPUT>Running as #AuthenticatedUser()#.
      May read the reports directory:
      #IsAuthorized("File", "/reports/*", "Read")#</CFOUTPUT>
    </CFIMPERSONATE>
  <CFCATCH TYPE="Security">
    <CFOUTPUT><B>#CFCATCH.Message#</B> #CFCATCH.Detail#</CFOUTPUT>
  </CFCATCH>
  </CFTRY>
  </TD></TR>
</CFLOOP>
</TABLE>
<CFOUTPUT><P>After the end tag, AuthenticatedUser() is "#AuthenticatedUser()#".</CFOUTPUT>
