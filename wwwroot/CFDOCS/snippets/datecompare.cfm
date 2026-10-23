<CFSET A = CreateDateTime(1999, 12, 31, 10, 0, 0)>
<CFSET B = CreateDateTime(1999, 12, 31, 18, 30, 0)>
<CFOUTPUT>
<P>A = #A#<BR>B = #B#</P>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Precision</TH><TH>DateCompare(A, B, ...)</TH></TR>
<CFLOOP INDEX="Part" LIST="s,n,h,d,m,yyyy">
<TR><TD>#Part#</TD><TD>#DateCompare(A, B, Part)#</TD></TR>
</CFLOOP>
</TABLE>
<P>DateCompare(B, A) = #DateCompare(B, A)#</P>
</CFOUTPUT>
