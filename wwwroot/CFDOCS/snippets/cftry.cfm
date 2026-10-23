<!--- Four things that go wrong, each caught by a different CFCATCH --->
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Attempt</TH><TH>Caught by</TH><TH>CFCATCH.Type</TH><TH>CFCATCH.Message</TH><TH>TagContext[1]</TH></TR>
<CFLOOP INDEX="Attempt" LIST="Bad SQL,Divide by zero,Missing file,Custom error">
  <CFOUTPUT><TR><TD>#Attempt#</TD></CFOUTPUT>
  <CFTRY>
    <CFSWITCH EXPRESSION="#Attempt#">
      <CFCASE VALUE="Bad SQL">
        <CFQUERY NAME="Oops" DATASOURCE="cfsnippets">SELECT * FROM NoSuchTable</CFQUERY>
      </CFCASE>
      <CFCASE VALUE="Divide by zero"><CFSET Result = 1 / 0></CFCASE>
      <CFCASE VALUE="Missing file"><CFINCLUDE TEMPLATE="sn_nowhere.cfm"></CFCASE>
      <CFCASE VALUE="Custom error"><CFTHROW TYPE="Snippets.Demo" MESSAGE="Thrown on purpose"></CFCASE>
    </CFSWITCH>
  <CFCATCH TYPE="Database">
    <CFOUTPUT><TD>Database</TD><TD>#CFCATCH.Type#</TD><TD>#CFCATCH.Message#</TD>
    <TD>#CFCATCH.TagContext[1].ID#, line #CFCATCH.TagContext[1].Line#</TD></CFOUTPUT>
  </CFCATCH>
  <CFCATCH TYPE="Expression">
    <CFOUTPUT><TD>Expression</TD><TD>#CFCATCH.Type#</TD><TD>#CFCATCH.Message#</TD>
    <TD>#CFCATCH.TagContext[1].ID#, line #CFCATCH.TagContext[1].Line#</TD></CFOUTPUT>
  </CFCATCH>
  <CFCATCH TYPE="Any">
    <CFOUTPUT><TD>Any</TD><TD>#CFCATCH.Type#</TD><TD>#CFCATCH.Message#</TD>
    <TD>#CFCATCH.TagContext[1].ID#, line #CFCATCH.TagContext[1].Line#</TD></CFOUTPUT>
  </CFCATCH>
  </CFTRY>
  </TR>
</CFLOOP>
</TABLE>
<P>The page carried on after every error.</P>
