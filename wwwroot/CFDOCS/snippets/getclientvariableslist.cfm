<CFAPPLICATION NAME="SnippetClientDemo" CLIENTMANAGEMENT="Yes" CLIENTSTORAGE="Cookie">
<CFSET Client.Browser = "Netscape 4.7">
<CFSET Client.Modem = "56K">
<CFSET Client.Visits = Client.HitCount>
<CFOUTPUT>
<P>Your client ID is #Client.CFID#.
<P>Variables you may change: <B>#GetClientVariablesList()#</B>
<UL>
<CFLOOP LIST="#GetClientVariablesList()#" INDEX="v">
  <LI>Client.#v# = #Evaluate("Client." & v)#
</CFLOOP>
</UL>
</CFOUTPUT>
