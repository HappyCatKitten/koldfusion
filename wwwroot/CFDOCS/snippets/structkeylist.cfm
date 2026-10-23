<CFSET Server_Info = StructNew()>
<CFSET Server_Info.OS = "Windows NT 4.0">
<CFSET Server_Info.RAM = "128 MB">
<CFSET Server_Info.Modem = "56K">
<CFOUTPUT>
<P>StructKeyList: #StructKeyList(Server_Info)#</P>
<P>With " / ": #StructKeyList(Server_Info, " / ")#</P>
<P>Sorted: #ListSort(StructKeyList(Server_Info), "text")#</P>
</CFOUTPUT>
