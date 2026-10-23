<CFSET Encoded = "S29sZEZ1c2lvbiA0LjU=">
<CFSET Bin = ToBinary(Encoded)>
<CFOUTPUT>
<UL>
<LI>Base64 input: #Encoded#
<LI>IsBinary(result): #IsBinary(Bin)#
<LI>Length in bytes: #Len(Bin)#
<LI>As text: #ToString(Bin)#
</UL>
</CFOUTPUT>
