<!--- ?flush=yes deletes the cached copy and comes back here --->
<CFIF IsDefined("URL.flush")>
  <CFCACHE ACTION="FLUSH" DIRECTORY="#GetTempDirectory()#" EXPIREURL="#CGI.SCRIPT_NAME#">
  <CFLOCATION URL="cfcache.cfm" ADDTOKEN="No">
</CFIF>
<!--- Serve a saved copy if it is less than one minute old --->
<CFCACHE ACTION="CACHE" DIRECTORY="#GetTempDirectory()#" TIMEOUT="#DateAdd('n', -1, Now())#">

<CFQUERY NAME="Courses" DATASOURCE="cfsnippets">
SELECT CorName, CorLevel FROM CourseList WHERE CorLevel = 'Advanced' ORDER BY CorName
</CFQUERY>
<CFOUTPUT>
<P>This page was generated at <B>#TimeFormat(Now(), "HH:mm:ss")#</B>. Reload it: for the next
minute you get the cached copy, and the time does not change.</P>
<UL><CFLOOP QUERY="Courses"><LI>#CorName#</CFLOOP></UL>
<P><A HREF="cfcache.cfm?flush=yes">Flush the cache</A></P>
</CFOUTPUT>
