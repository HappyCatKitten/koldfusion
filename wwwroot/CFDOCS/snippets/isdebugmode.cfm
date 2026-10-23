<CFOUTPUT>
<P>Debug mode right now: <B>#IsDebugMode()#</B>
</CFOUTPUT>
<CFIF IsDebugMode()>
  <P><FONT COLOR="Red">Developer note: this page was built at <CFOUTPUT>#TimeFormat(Now(), "HH:mm:ss")#</CFOUTPUT>.</FONT>
</CFIF>
<CFSETTING SHOWDEBUGOUTPUT="No">
<CFOUTPUT>
<P>After CFSETTING SHOWDEBUGOUTPUT="No": <B>#IsDebugMode()#</B>
</CFOUTPUT>
