<!--- KoldFusion Demo Gallery: mechanical CF 4.5 port of addition.cfm (the original sits next to this file, unchanged).
      Change: XHTML-style self-closing CF tags ("<cfset x = 1 />") were removed - that syntax arrived with
      ColdFusion MX and CF 4.5 reads the trailing "/" as a division operator. Renamed to addition45.cfm so it can be called as CF_ADDITION45 without shadowing the original.
      All credit and the original licence (see SOURCE.txt) belong to the original author. --->
<cfset caller.addition = attributes.first + attributes.second>
<cfexit method="exitTag">
