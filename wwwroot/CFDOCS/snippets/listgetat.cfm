<CFSET Days = "Sun,Mon,Tue,Wed,Thu,Fri,Sat">
<CFOUTPUT>
<P>Today is #ListGetAt(Days, DayOfWeek(Now()))#.</P>
<P>Y2K falls on a #ListGetAt(Days, DayOfWeek(CreateDate(2000, 1, 1)))#.</P>
</CFOUTPUT>
<CFTRY>
  <CFOUTPUT>#ListGetAt(Days, 8)#</CFOUTPUT>
<CFCATCH TYPE="Expression">
  <CFOUTPUT><P>Asking for day 8 gives an error: <I>#CFCATCH.Message#</I></P></CFOUTPUT>
</CFCATCH>
</CFTRY>
