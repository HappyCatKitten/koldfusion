<!--- Who works in Engineering? Ask the Gibson Directory Server --->
<CFLDAP ACTION="Query" NAME="People"
        SERVER="#Server.Directory.Host#" PORT="#Server.Directory.Port#"
        START="ou=People, #Server.Directory.BaseDN#" SCOPE="OneLevel"
        FILTER="(&(objectclass=person)(ou=Engineering))"
        ATTRIBUTES="cn,title,mail,telephoneNumber" SORT="cn" SORTCONTROL="nocase">
<CFOUTPUT><P>#People.RecordCount# people work in Engineering.</P></CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Name</TH><TH>Title</TH><TH>E-mail</TH><TH>Phone</TH></TR>
<CFOUTPUT QUERY="People">
<TR><TD>#cn#</TD><TD>#title#</TD><TD>#mail#</TD><TD>#telephoneNumber#</TD></TR>
</CFOUTPUT>
</TABLE>
<!--- Errors carry the LDAP result code --->
<CFTRY>
  <CFLDAP ACTION="Query" NAME="Nobody" SERVER="#Server.Directory.Host#" PORT="#Server.Directory.Port#"
          START="ou=Nowhere, #Server.Directory.BaseDN#" ATTRIBUTES="cn">
  <CFCATCH TYPE="Any">
    <CFOUTPUT><P><B>#CFCATCH.Message#</B> (ErrorCode #CFCATCH.ErrorCode#)</P></CFOUTPUT>
  </CFCATCH>
</CFTRY>
