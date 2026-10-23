<CFSET Capitals = StructNew()>
<CFSET Capitals.France = "Paris">
<CFSET Capitals.Japan = "Tokyo">
<CFSET Capitals.Peru = "Lima">
<CFSET Country = "Japan">
<CFOUTPUT>
<P>The capital of #Country# is <B>#StructFind(Capitals, Country)#</B>.</P>
</CFOUTPUT>
<CFTRY>
  <CFSET Temp = StructFind(Capitals, "Atlantis")>
<CFCATCH TYPE="Expression">
  <CFOUTPUT><P>Atlantis: <I>#CFCATCH.Message#</I></P></CFOUTPUT>
</CFCATCH>
</CFTRY>
