<!--- sn_pagetitle.cfm draws a title bar from Variables.PageTitle,
      and sets Variables.TitleDrawn for the including page to use --->
<CFSET PageTitle = "Quarterly Parks Report">
<CFINCLUDE TEMPLATE="sn_pagetitle.cfm">

<CFQUERY NAME="Parks" DATASOURCE="cfsnippets">
SELECT ParkName, State FROM Parks WHERE Region = 'Southwest' ORDER BY ParkName
</CFQUERY>
<UL>
<CFOUTPUT QUERY="Parks"><LI>#ParkName# (#State#)</CFOUTPUT>
</UL>

<CFSET PageTitle = "Appendix: No Parks Were Harmed">
<CFINCLUDE TEMPLATE="sn_pagetitle.cfm">
<CFOUTPUT><P>The include file has drawn #TitleDrawn# title bars on this page.</P></CFOUTPUT>
