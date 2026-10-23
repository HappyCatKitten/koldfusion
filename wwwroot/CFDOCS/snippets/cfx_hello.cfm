<P><B>CFX_HELLO</B>: <CFX_HELLO NAME="Netscape Navigator user"></P>
<CFX_HELLO NAME="Ada" VARIABLE="Greeting">
<CFOUTPUT><P>Stored in a variable: <I>#Greeting#</I></P></CFOUTPUT>

<P><B>CFX_DICE</B>: <CFX_DICE ROLLS="3" SIDES="6" VARIABLE="Total"></P>
<CFOUTPUT><P>The total, from VARIABLE: #Total#<CFIF Total GTE 15> (jackpot!)</CFIF></P></CFOUTPUT>
<CFTRY>
  <CFX_DICE ROLLS="0">
  <CFCATCH TYPE="Application"><CFOUTPUT><P>Zero dice: #CFCATCH.Message#</P></CFOUTPUT></CFCATCH>
</CFTRY>

<P><B>CFX_SYSINFO</B>:</P>
<CFX_SYSINFO NAME="Sys">
<TABLE BORDER=1 CELLPADDING=3>
<CFOUTPUT QUERY="Sys"><TR><TD>#Item#</TD><TD>#Value#</TD></TR></CFOUTPUT>
</TABLE>
