<CFTRY>
  <CFSET Num = CreateObject("JAVA", "java.lang.Integer")>
  <CFTRY>
    <CFSET N = Num.parseInt("forty-two")>
    <CFCATCH TYPE="Object">
      <CFSET Ex = GetException(Num)>
      <CFOUTPUT>
      <P>CFCATCH.Message: <B>#CFCATCH.Message#</B><BR>
      Ex.getMessage(): <B>#Ex.getMessage()#</B><BR>
      Ex.getClass().getName(): <B>#Ex.getClass().getName()#</B></P>
      </CFOUTPUT>
    </CFCATCH>
  </CFTRY>
  <CFCATCH TYPE="Object">
    <CFOUTPUT><P>No Java Virtual Machine: <I>#CFCATCH.Message#</I></P></CFOUTPUT>
  </CFCATCH>
</CFTRY>
