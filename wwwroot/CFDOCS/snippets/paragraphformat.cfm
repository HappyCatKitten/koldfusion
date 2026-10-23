<CFSET NL = Chr(13) & Chr(10)>
<CFSET Memo = "Our web server will be down this weekend" & NL
    & "while we install the Y2K patches." & NL & NL
    & "Please save your work early and often." & NL & NL
    & "-- The IS department">
<TABLE BORDER=1 CELLPADDING=5 WIDTH="400">
<TR><TH>Without ParagraphFormat</TH></TR>
<TR><TD><CFOUTPUT>#Memo#</CFOUTPUT></TD></TR>
<TR><TH>With ParagraphFormat</TH></TR>
<TR><TD><CFOUTPUT>#ParagraphFormat(Memo)#</CFOUTPUT></TD></TR>
</TABLE>
