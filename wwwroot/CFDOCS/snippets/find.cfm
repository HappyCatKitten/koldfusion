<CFSET Text = "To be or not to be, that is the question">
<CFSET Pos = Find("be", Text)>
<CFOUTPUT>
<P><I>#Text#</I></P>
<UL>
<LI>Find("be", Text) = #Pos#
<LI>Next "be" after that: #Find("be", Text, Pos + 1)#
<LI>Find("To", Text) = #Find("To", Text)#, but Find("TO", Text) = #Find("TO", Text)#
<LI>Find("Hamlet", Text) = #Find("Hamlet", Text)#
</UL>
</CFOUTPUT>
