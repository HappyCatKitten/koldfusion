<CFPARAM NAME="URL.Name" DEFAULT="   Grace Hopper   ">
<CFOUTPUT>
<P>You typed [#URL.Name#] (#Len(URL.Name)# characters).</P>
<P>Trimmed: [#Trim(URL.Name)#] (#Len(Trim(URL.Name))# characters).</P>
<CFIF Len(Trim(URL.Name)) EQ 0><P><B>Please enter a name!</B></P></CFIF>
</CFOUTPUT>
<FORM ACTION="trim.cfm" METHOD="GET">
Name: <INPUT TYPE="Text" NAME="Name"> <INPUT TYPE="Submit" VALUE="Trim it">
</FORM>
