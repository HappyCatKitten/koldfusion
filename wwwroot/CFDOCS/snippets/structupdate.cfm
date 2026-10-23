<CFSET Stock = StructNew()>
<CFSET Stock.Modems = 12>
<CFSET Temp = StructUpdate(Stock, "Modems", Stock.Modems - 1)>
<CFOUTPUT><P>Sold a modem. Modems left: <B>#Stock.Modems#</B></P></CFOUTPUT>
<CFTRY>
  <CFSET Temp = StructUpdate(Stock, "Modemz", 0)>
<CFCATCH TYPE="Expression">
  <CFOUTPUT><P>Typo caught: <I>#CFCATCH.Message#</I></P></CFOUTPUT>
</CFCATCH>
</CFTRY>
