<CFSET Text = "Call 555-1234 or 555-9876 before Y2K">
<CFSET Match = REFind("([0-9]{3})-([0-9]{4})", Text, 1, "True")>
<CFOUTPUT>
<P>#Text#</P>
<UL>
<LI>First digit at: #REFind("[[:digit:]]", Text)#
<LI>Second number at: #REFind("[0-9]{3}-", Text, 10)#
<LI>"y2k" (case-sensitive): #REFind("y2k", Text)#
<LI>Whole match: #Mid(Text, Match.pos[1], Match.len[1])#
<LI>Exchange: #Mid(Text, Match.pos[2], Match.len[2])#, line: #Mid(Text, Match.pos[3], Match.len[3])#
</UL>
</CFOUTPUT>
