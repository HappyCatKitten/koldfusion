<!--- sn_repeat.cfm is a paired custom tag that repeats its body TIMES times.
      It uses CFEXIT METHOD="ExitTag" to give up when TIMES is 0,
      and CFEXIT METHOD="Loop" to run the body again. --->
<P><B>Times="3":</B><BR>
<CFMODULE TEMPLATE="sn_repeat.cfm" TIMES="3">
  <IMG SRC="/CFIDE/administrator/images/check.gif" WIDTH=16 HEIGHT=16> Please wait, dialing...<BR>
</CFMODULE></P>

<P><B>Times="0":</B><BR>
<CFMODULE TEMPLATE="sn_repeat.cfm" TIMES="0">
  You should not see this line.<BR>
</CFMODULE>
(the body was skipped)</P>

<P>Source of sn_repeat.cfm:</P>
<CFFILE ACTION="READ" FILE="#ExpandPath('sn_repeat.cfm')#" VARIABLE="Src">
<CFOUTPUT><PRE>#HTMLEditFormat(Src)#</PRE></CFOUTPUT>
