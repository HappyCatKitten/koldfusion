<CFQUERY NAME="GetParks" DATASOURCE="cfsnippets">
SELECT ParkName FROM Parks WHERE Region = 'Pacific West'
</CFQUERY>
<CFSET ParkList = ValueList(GetParks.ParkName)>
<CFPARAM NAME="URL.Word" DEFAULT="SEASHORE">
<CFSET Pos = ListContainsNoCase(ParkList, URL.Word)>
<CFOUTPUT>
<P>Parks in the Pacific West region: #ListLen(ParkList)#</P>
<CFIF Pos>
  <P>The first park whose name contains "#URL.Word#" is number #Pos#:
  <B>#ListGetAt(ParkList, Pos)#</B></P>
<CFELSE>
  <P>No Pacific West park name contains "#URL.Word#".</P>
</CFIF>
<FORM ACTION="listcontainsnocase.cfm" METHOD="get">
Search for: <INPUT TYPE="text" NAME="Word" VALUE="#HTMLEditFormat(URL.Word)#">
<INPUT TYPE="submit" VALUE="Search">
</FORM>
</CFOUTPUT>
