<CFSET Msg = "Line one" & Chr(13) & Chr(10) & "Line two" & Chr(13) & Chr(10)>
<CFSET Clean = StripCR(Msg)>
<CFOUTPUT>
<P>Before: #Len(Msg)# characters</P>
<P>After StripCR: #Len(Clean)# characters</P>
<PRE>#Clean#</PRE>
</CFOUTPUT>
