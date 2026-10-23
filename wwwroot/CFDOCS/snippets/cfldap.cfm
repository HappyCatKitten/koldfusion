<CFTRY>
  <CFLDAP ACTION="Query" SERVER="ldap.gibson.example" NAME="People"
          START="o=Gibson, c=US" SCOPE="Subtree"
          FILTER="(ou=Engineering)" ATTRIBUTES="cn,mail,telephoneNumber">
  <CFCATCH TYPE="Application">
    <CFOUTPUT><P><B>#CFCATCH.Message#:</B> #CFCATCH.Detail#</P></CFOUTPUT>
    <!--- Use the company database as the phone book instead --->
    <CFQUERY NAME="People" DATASOURCE="cfsnippets" MAXROWS="5">
    SELECT LastName AS cn, Email AS mail, Phone AS telephoneNumber
    FROM Employees WHERE Department = 'Engineering' ORDER BY LastName
    </CFQUERY>
  </CFCATCH>
</CFTRY>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>cn</TH><TH>mail</TH><TH>telephoneNumber</TH></TR>
<CFOUTPUT QUERY="People">
<TR><TD>#cn#</TD><TD>#mail#</TD><TD>#telephoneNumber#</TD></TR>
</CFOUTPUT>
</TABLE>
