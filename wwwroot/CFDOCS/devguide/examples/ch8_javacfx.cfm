<!--- ch8_javacfx.cfm: CFX tags written in Java (they need a Java Virtual Machine) --->
<CFTRY>
  <P><CFX_HELLOCOLDFUSION NAME="Les"></P>
  <CFX_JAVAQUERY ACTION="properties" NAME="JavaInfo">
  <TABLE BORDER=1 CELLPADDING=2>
  <CFOUTPUT QUERY="JavaInfo">
    <CFIF ListFind("java.version,java.vendor,os.name", Name)><TR><TD>#Name#</TD><TD>#Value#</TD></TR></CFIF>
  </CFOUTPUT>
  </TABLE>
  <CFCATCH TYPE="Any">
    <CFOUTPUT><P>The Java CFX tags could not run: <I>#CFCATCH.Message#</I></P></CFOUTPUT>
  </CFCATCH>
</CFTRY>
