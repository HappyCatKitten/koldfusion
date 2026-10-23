<!--- machine-readable server metrics for the kfstat command (localhost only, needs performance monitoring enabled) --->
<cfsetting enablecfoutputonly="yes" showdebugoutput="no">
<cfregistry action="get" branch="HKEY_LOCAL_MACHINE\SOFTWARE\Gibson\KoldFusion\CurrentVersion\Debug" entry="EnablePerformanceMonitoring" variable="pm">
<cfcontent type="text/plain">
<cfif CGI.REMOTE_ADDR NEQ "127.0.0.1"><cfoutput>Access denied.</cfoutput><cfabort></cfif>
<cfif pm NEQ "1"><cfoutput>Performance monitoring is disabled. Enable it on the Debugging page of the KoldFusion Administrator.</cfoutput><cfabort></cfif>
<cfset m = GetMetricData("perf_monitor")>
<cfoutput>#m.PageHits# #m.ReqQueued# #m.ReqRunning# #m.ReqTimedOut# #m.BytesIn# #m.BytesOut# #m.DBHits# #m.AvgQueueTime# #m.AvgReqTime# #m.AvgDBTime#</cfoutput>
