<!--- KoldFusion Demo Gallery: mechanical CF 4.5 port of day_of_week.cfm (the original sits next to this file, unchanged).
      Change: XHTML-style self-closing CF tags ("<cfset x = 1 />") were removed - that syntax arrived with
      ColdFusion MX and CF 4.5 reads the trailing "/" as a division operator. 
      All credit and the original licence (see SOURCE.txt) belong to the original author. --->
<cfloop from = "2008" to = "2121" index = "i">
    <cfset myDate = createDate(i, 12, 25)>
    <cfif dayOfWeek(myDate) eq 1>
        December 25th falls on a Sunday in <cfoutput>#i#</cfoutput><br />
    </cfif>
</cfloop>
