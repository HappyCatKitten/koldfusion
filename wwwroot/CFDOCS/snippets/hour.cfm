<CFSET H = Hour(Now())>
<CFOUTPUT>
<P>Hour("2:30 PM") = #Hour("2:30 PM")#, Hour(CreateTime(0, 15, 0)) = #Hour(CreateTime(0, 15, 0))#</P>
<P>It is #H# o'clock at the server. Good
<CFIF H LT 12>morning<CFELSEIF H LT 18>afternoon<CFELSE>evening</CFIF>!</P>
</CFOUTPUT>
