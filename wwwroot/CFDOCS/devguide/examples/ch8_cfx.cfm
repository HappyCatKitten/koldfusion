<!--- ch8_cfx.cfm: calling CFX tags written in C --->
<P><CFX_HELLO NAME="KoldFusion developer"></P>

<!--- Ask the tag to put its result in a variable instead of the page --->
<CFX_HELLO NAME="variable" VARIABLE="Greeting">
<CFOUTPUT><P>CFX_HELLO returned: <I>#Greeting#</I></P></CFOUTPUT>

<P>Rolling three dice: <CFX_DICE ROLLS="3" SIDES="6" VARIABLE="DiceTotal"></P>
<CFOUTPUT><P>The total is #DiceTotal#.
<CFIF DiceTotal GTE 15>Lucky!<CFELSE>Better luck next time.</CFIF></P></CFOUTPUT>
