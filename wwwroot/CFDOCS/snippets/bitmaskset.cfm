<CFSET Packed = 0>
<CFSET Packed = BitMaskSet(Packed, 31, 0, 5)>   <!--- day   --->
<CFSET Packed = BitMaskSet(Packed, 12, 5, 4)>   <!--- month --->
<CFSET Packed = BitMaskSet(Packed, 99, 9, 7)>   <!--- year - 1900 --->
<CFOUTPUT>
<P>Packed date: #Packed# (binary <TT>#FormatBaseN(Packed, 2)#</TT>)
<P>Unpacked: #BitMaskRead(Packed, 5, 4)#/#BitMaskRead(Packed, 0, 5)#/#1900 + BitMaskRead(Packed, 9, 7)#
<P>Too big for the field: <TT>BitMaskSet(0, 255, 4, 3)</TT> = #BitMaskSet(0, 255, 4, 3)#
(only 3 bits, <TT>111</TT>, were stored)
</CFOUTPUT>
