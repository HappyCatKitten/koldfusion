<CFSET Tips = "Bookmark this page!,Upgrade to Netscape 4.7.,Y2K is just around the corner.,Use CFQUERYPARAM.">
<CFOUTPUT>
<P>You rolled: #RandRange(1, 6)# and #RandRange(1, 6)#
<P>Tip of the day: <I>#ListGetAt(Tips, RandRange(1, ListLen(Tips)))#</I>
</CFOUTPUT>
<!--- Roll 600 dice and count the results --->
<CFSET Counts = ArrayNew(1)>
<CFSET ArraySet(Counts, 1, 6, 0)>
<CFLOOP INDEX="i" FROM="1" TO="600"><CFSET r = RandRange(1, 6)><CFSET Counts[r] = Counts[r] + 1></CFLOOP>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Face</TH><TH>Count (of 600)</TH></TR>
<CFLOOP INDEX="f" FROM="1" TO="6">
<CFOUTPUT><TR><TD ALIGN="CENTER">#f#</TD><TD ALIGN="RIGHT">#Counts[f]#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
