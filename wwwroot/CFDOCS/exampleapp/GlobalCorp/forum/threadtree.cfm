<!---
	threadtree.cfm - recursive custom tag that draws a message thread.
	Called with CFMODULE; for each reply it calls itself one level deeper.
	Attributes:
	  Messages    query with Msg_ID, ParentID, Subject, Author, Posted
	  ParentID    draw the children of this message (0 = thread starters)
	  Depth       indent level (default 0)
	  Current     Msg_ID to highlight (default 0)
	  NewestFirst Yes = list the top level newest first (default No)
	We walk the query by row number instead of with CFLOOP QUERY, because
	every level of the recursion shares the same query and its current row.
--->
<CFPARAM NAME="Attributes.ParentID" DEFAULT="0">
<CFPARAM NAME="Attributes.Depth" DEFAULT="0">
<CFPARAM NAME="Attributes.Current" DEFAULT="0">
<CFPARAM NAME="Attributes.NewestFirst" DEFAULT="No">
<CFSET q = Attributes.Messages>
<CFIF Attributes.NewestFirst AND Attributes.Depth EQ 0>
	<CFSET FirstRow = q.RecordCount><CFSET LastRow = 1><CFSET StepBy = -1>
<CFELSE>
	<CFSET FirstRow = 1><CFSET LastRow = q.RecordCount><CFSET StepBy = 1>
</CFIF>
<CFIF q.RecordCount GT 0>
<CFLOOP INDEX="r" FROM="#FirstRow#" TO="#LastRow#" STEP="#StepBy#">
	<CFIF q.ParentID[r] EQ Attributes.ParentID>
		<CFOUTPUT>
		<TR VALIGN=TOP<CFIF q.Msg_ID[r] EQ Attributes.Current> BGCOLOR="##FFFFCC"</CFIF>>
		<TD NOWRAP><IMG SRC="/CFIDE/administrator/images/spacer.gif" WIDTH="#Attributes.Depth * 18 + 1#" HEIGHT=1><IMG SRC="/CFIDE/administrator/images/<CFIF Attributes.Depth EQ 0>folder.gif<CFELSE>file.gif</CFIF>" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
		<FONT FACE="Arial, Helvetica" SIZE=2><CFIF q.Msg_ID[r] EQ Attributes.Current><B>#HTMLEditFormat(q.Subject[r])#</B><CFELSE><A HREF="message.cfm?Msg_ID=#q.Msg_ID[r]#">#HTMLEditFormat(q.Subject[r])#</A></CFIF></FONT>
		<CFIF DateDiff("h", q.Posted[r], Now()) LT 72><IMG SRC="/images/new.gif" WIDTH=44 HEIGHT=22 ALIGN=ABSMIDDLE ALT="New!"></CFIF>
		</TD>
		<TD NOWRAP><FONT FACE="Arial, Helvetica" SIZE=1>#HTMLEditFormat(q.Author[r])#</FONT></TD>
		<TD NOWRAP><FONT FACE="Arial, Helvetica" SIZE=1>#DateFormat(q.Posted[r], "mm/dd/yy")# #TimeFormat(q.Posted[r], "h:mm tt")#</FONT></TD>
		</TR>
		</CFOUTPUT>
		<CFMODULE TEMPLATE="threadtree.cfm" Messages="#q#" ParentID="#q.Msg_ID[r]#"
			Depth="#Attributes.Depth + 1#" Current="#Attributes.Current#">
	</CFIF>
</CFLOOP>
</CFIF>
