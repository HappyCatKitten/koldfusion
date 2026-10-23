<CFSET Codes = "AK,AZ,CA,CO,NV,UT">
<CFPARAM NAME="URL.State" DEFAULT="CA">
<CFOUTPUT>
<P>Western states we cover: #Codes#</P>
<CFIF ListFind(Codes, URL.State)>
  <P><B>#URL.State#</B> is element #ListFind(Codes, URL.State)# of the list.</P>
<CFELSE>
  <P><B>#URL.State#</B> is not in the list. (ListFind is case-sensitive, so "ca" would not match.)</P>
</CFIF>
<FORM ACTION="listfind.cfm" METHOD="get">
State code: <INPUT TYPE="text" NAME="State" SIZE="3" VALUE="#HTMLEditFormat(URL.State)#">
<INPUT TYPE="submit" VALUE="Look it up">
</FORM>
</CFOUTPUT>
