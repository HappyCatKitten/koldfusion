<CFSET Customer = StructNew()>
<CFSET Customer.Name = "Pat">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Expression</TH><TH>Result</TH></TR>
<CFLOOP INDEX="v" LIST="Customer,Customer.Name,Customer.Email,Variables.Customer,URL.Color,Color,Form.Color">
<CFOUTPUT><TR><TD><TT>IsDefined("#v#")</TT></TD><TD>#IsDefined(v)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<CFIF IsDefined("URL.Color")>
  <CFOUTPUT><P>Your favorite color is #URL.Color#.</CFOUTPUT>
<CFELSE>
  <P>Try adding <TT>?Color=Blue</TT> to the URL.
</CFIF>
