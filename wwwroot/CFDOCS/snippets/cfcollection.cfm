<!--- A throwaway collection: create it, fill it, search it, delete it --->
<CFSET CollName = "snippets_temp">

<!--- tidy up after an interrupted earlier run --->
<CFTRY>
  <CFCOLLECTION ACTION="DELETE" COLLECTION="#CollName#">
<CFCATCH TYPE="Any"></CFCATCH>
</CFTRY>

<CFCOLLECTION ACTION="CREATE" COLLECTION="#CollName#">
<CFINDEX COLLECTION="#CollName#" ACTION="UPDATE" TYPE="PATH"
    KEY="#ExpandPath('/CFDOCS/langref/')#" EXTENSIONS=".htm"
    URLPATH="/CFDOCS/langref">
<CFCOLLECTION ACTION="OPTIMIZE" COLLECTION="#CollName#">
<CFSEARCH NAME="Hits" COLLECTION="#CollName#" CRITERIA="collection" MAXROWS="5">
<CFCOLLECTION ACTION="DELETE" COLLECTION="#CollName#">

<CFOUTPUT>
<H3>Collection #CollName#: created, indexed, searched and deleted</H3>
<P>Language Reference pages that mention "collection" (#Hits.RecordCount# shown):
</CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Score</TH><TH>Page</TH></TR>
<CFOUTPUT QUERY="Hits">
<TR><TD>#Score#</TD><TD><A HREF="#Hits.URL#">#Title#</A></TD></TR>
</CFOUTPUT>
</TABLE>
