<CFIF IsDefined("URL.CFTREEITEMKEY")>
  <CFOUTPUT><P>You clicked the item <B>#HTMLEditFormat(URL.CFTREEITEMKEY)#</B>.</CFOUTPUT>
</CFIF>

<CFFORM NAME="Map" ACTION="cftreeitem.cfm">
<CFTREE NAME="SiteMap" WIDTH="320">
  <CFTREEITEM VALUE="server" DISPLAY="KoldFusion Server 4.5" IMG="computer">
  <CFTREEITEM VALUE="docs" DISPLAY="Documentation" PARENT="server">
  <CFTREEITEM VALUE="langref" DISPLAY="CFML Language Reference"
      PARENT="docs" HREF="cftreeitem.cfm">
  <CFTREEITEM VALUE="snippets" DISPLAY="Examples" PARENT="docs"
      HREF="cftreeitem.cfm">
  <CFTREEITEM VALUE="admin" DISPLAY="Administrator" PARENT="server" EXPAND="No">
  <CFTREEITEM VALUE="datasources" DISPLAY="Data Sources" PARENT="admin"
      IMG="fixed" HREF="cftreeitem.cfm">
  <CFTREEITEM VALUE="verity" DISPLAY="Verity Collections" PARENT="admin"
      IMG="cd" HREF="cftreeitem.cfm">
</CFTREE>
</CFFORM>
