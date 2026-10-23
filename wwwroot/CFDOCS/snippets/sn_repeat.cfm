<!--- sn_repeat.cfm: helper custom tag for the CFEXIT example.
      Usage: <CFMODULE TEMPLATE="sn_repeat.cfm" TIMES="3"> body </CFMODULE> --->
<CFPARAM NAME="Attributes.Times" DEFAULT="1">
<CFIF ThisTag.ExecutionMode IS "Start">
  <CFIF Attributes.Times LT 1>
    <CFEXIT METHOD="ExitTag">
  </CFIF>
  <CFSET ThisTag.Pass = 1>
<CFELSE>
  <CFIF ThisTag.Pass LT Attributes.Times>
    <CFSET ThisTag.Pass = ThisTag.Pass + 1>
    <CFEXIT METHOD="Loop">
  </CFIF>
</CFIF>
