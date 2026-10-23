<CFSET Branch = "HKEY_LOCAL_MACHINE\SOFTWARE\Gibson\KoldFusion\Snippets">
<!--- Create a subkey with two values --->
<CFREGISTRY ACTION="Set" BRANCH="#Branch#" ENTRY="Demo" TYPE="Key">
<CFREGISTRY ACTION="Set" BRANCH="#Branch#\Demo" ENTRY="Greeting" TYPE="String" VALUE="Hello, registry">
<CFREGISTRY ACTION="Set" BRANCH="#Branch#\Demo" ENTRY="Visits" TYPE="DWord" VALUE="1999">

<CFREGISTRY ACTION="GetAll" BRANCH="#Branch#\Demo" NAME="Entries" TYPE="Any" SORT="Entry">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Entry</TH><TH>Type</TH><TH>Value</TH></TR>
<CFOUTPUT QUERY="Entries">
<TR><TD>#Entry#</TD><TD>#Type#</TD><TD>#Value#</TD></TR>
</CFOUTPUT>
</TABLE>

<CFREGISTRY ACTION="Get" BRANCH="#Branch#\Demo" ENTRY="Greeting" VARIABLE="Said">
<CFOUTPUT><P>Get returned: #Said#</P></CFOUTPUT>

<!--- Clean up: remove the whole Demo key --->
<CFREGISTRY ACTION="Delete" BRANCH="#Branch#\Demo">
<CFREGISTRY ACTION="GetAll" BRANCH="#Branch#" NAME="Left" TYPE="Key">
<CFOUTPUT><P>Subkeys left under Snippets: #Left.RecordCount#</P></CFOUTPUT>
