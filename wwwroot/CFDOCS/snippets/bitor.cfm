<CFSET Read = 1><CFSET Write = 2><CFSET Delete = 4>
<CFSET Rights = 0>
<CFSET Rights = BitOr(Rights, Read)>
<CFSET Rights = BitOr(Rights, Write)>
<CFSET Rights = BitOr(Rights, Write)>  <!--- twice is harmless --->
<CFOUTPUT>
<P>Rights = #Rights# (binary <TT>#FormatBaseN(Rights, 2)#</TT>)
<UL>
<LI>Read: #YesNoFormat(BitAnd(Rights, Read))#
<LI>Write: #YesNoFormat(BitAnd(Rights, Write))#
<LI>Delete: #YesNoFormat(BitAnd(Rights, Delete))#
</UL>
<P>BitOr(12, 10) = #BitOr(12, 10)#
</CFOUTPUT>
