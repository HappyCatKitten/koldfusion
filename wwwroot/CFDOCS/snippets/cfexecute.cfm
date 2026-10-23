<P>The server's clock says:
<B><CFEXECUTE NAME="/bin/date" ARGUMENTS="+%m/%d/%Y" TIMEOUT="5"></CFEXECUTE></B></P>

<!--- Capture output in a file, then read it back --->
<CFSET OutFile = GetTempDirectory() & "cfexecute_demo.txt">
<CFEXECUTE NAME="/bin/echo" ARGUMENTS="Greetings from the command line" OUTPUTFILE="#OutFile#" TIMEOUT="5">
</CFEXECUTE>
<CFFILE ACTION="READ" FILE="#OutFile#" VARIABLE="Captured">
<CFFILE ACTION="DELETE" FILE="#OutFile#">
<CFOUTPUT><P>From OUTPUTFILE: <TT>#HTMLEditFormat(Trim(Captured))#</TT></P></CFOUTPUT>

<!--- A program that takes too long --->
<CFTRY>
  <CFEXECUTE NAME="/bin/sleep" ARGUMENTS="5" TIMEOUT="1"></CFEXECUTE>
  <CFCATCH TYPE="Application">
    <CFOUTPUT><P><B>#CFCATCH.Message#</B> #CFCATCH.Detail#</P></CFOUTPUT>
  </CFCATCH>
</CFTRY>
