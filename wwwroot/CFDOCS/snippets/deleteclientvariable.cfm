<CFAPPLICATION NAME="SnippetClientDemo" CLIENTMANAGEMENT="Yes" CLIENTSTORAGE="Cookie">
<CFSET Client.FavoriteColor = "Teal">
<CFSET Client.ModemSpeed = "28.8">
<CFOUTPUT>
<P>Before: #GetClientVariablesList()#
<P>DeleteClientVariable("ModemSpeed") returned #DeleteClientVariable("ModemSpeed")#
(we upgraded to 56K).
<P>DeleteClientVariable("Pager") returned #DeleteClientVariable("Pager")#
<P>After: #GetClientVariablesList()#
<P>IsDefined("Client.ModemSpeed"): #IsDefined("Client.ModemSpeed")#
</CFOUTPUT>
