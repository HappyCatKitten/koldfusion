<!--- Verity site search --->
<cfset pageTitle = "Search This Site">
<cfparam name="URL.criteria" default="">
<cfset colls = "">
<cfregistry action="getall" branch="HKEY_LOCAL_MACHINE\SOFTWARE\Allair\KoldFusion\CurrentVersion\Verity\Collections" name="colls" type="key">
<cfif NOT ListFindNoCase(ValueList(colls.Entry), "kfsite") OR IsDefined("URL.reindex")>
	<cfif NOT ListFindNoCase(ValueList(colls.Entry), "kfsite")><cfcollection action="create" collection="kfsite"></cfif>
	<cfindex collection="kfsite" action="refresh" type="path" key="#ExpandPath('/')#" extensions=".htm,.html,.cfm" recurse="yes" urlpath="/">
	<cfset reindexed = true>
</cfif>
<cfinclude template="_top.cfm">
<cfoutput>
<FORM ACTION="search.cfm" METHOD="GET">
<IMG SRC="/images/globe.gif" WIDTH=32 HEIGHT=32 ALIGN=ABSMIDDLE> Search for: <INPUT TYPE="text" NAME="criteria" VALUE="#HTMLEditFormat(URL.criteria)#" SIZE=30>
<INPUT TYPE="submit" VALUE="Search!"> <A HREF="search.cfm?reindex=1">(rebuild index)</A>
<BR><FONT SIZE=1>Try: <A HREF="search.cfm?criteria=administrator">administrator</A>, <A HREF="search.cfm?criteria=cfquery">cfquery</A>,
<A HREF="search.cfm?criteria=guestbook, verity">guestbook, verity</A>, <A HREF="search.cfm?criteria=%22web application server%22">"web application server"</A>. Commas mean OR, NOT excludes.</FONT>
</FORM>
<cfif IsDefined("reindexed")><P><I>The site was just (re)indexed.</I></cfif>
</cfoutput>
<cfif Len(Trim(URL.criteria))>
	<cfsearch name="results" collection="kfsite" criteria="#URL.criteria#" maxrows="25">
	<cfoutput><P>Found <B>#results.RecordCount#</B> matching documents<cfif results.RecordCount> (searched #results.RecordsSearched#)</cfif>:</P></cfoutput>
	<OL>
	<cfoutput query="results">
	<LI><A HREF="#results.URL#"><B>#HTMLEditFormat(Title)#</B></A> <FONT SIZE=1 COLOR="##666666">score #NumberFormat(Score * 100)#%</FONT><BR>
	<FONT SIZE=1>#HTMLEditFormat(Left(Summary, 180))#...</FONT><BR><BR>
	</cfoutput>
	</OL>
</cfif>
<cfinclude template="_bottom.cfm">
