<!--- Version Info --->
<cfset info = KFUSION_SERVERINFO()>
<cfset pageTitle = "Version Information">
<cfinclude template="../_header.cfm">
<cfoutput>
<P><TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="90%">
<cfset rows = ArrayNew(1)>
<cfset rows[1] = "Server Product|#Server.ColdFusion.ProductName#">
<cfset rows[2] = "Version|#Server.ColdFusion.ProductVersion#">
<cfset rows[3] = "Edition|#Server.ColdFusion.ProductLevel#">
<cfset rows[4] = "Serial Number|#Server.ColdFusion.SerialNumber#">
<cfset rows[5] = "Operating System|#Server.OS.Name#">
<cfset rows[6] = "OS Version|#Server.OS.Version#">
<cfset rows[7] = "Additional Information|#Server.OS.AdditionalInformation#">
<cfset rows[8] = "Build Number|#Server.OS.BuildNumber#">
<cfloop index="i" from="1" to="#ArrayLen(rows)#">
<TR BGCOLOR="#IIf(i MOD 2, DE('FFFFFF'), DE('FFFBF0'))#"><TD WIDTH=200>#Request.f#<B>#ListFirst(rows[i], "|")#</B></FONT></TD><TD>#Request.f##ListRest(rows[i], "|")#</FONT></TD></TR>
</cfloop>
</TABLE>
<P><TABLE WIDTH="90%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>Server Statistics</B></FONT></TD></TR></TABLE>
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD>#Request.f#Server started</FONT></TD><TD>#Request.f##DateFormat(info.StartedAt, "dddd, mmmm d, yyyy")# #TimeFormat(info.StartedAt, "h:mm:ss tt")# (up #info.Uptime#)</FONT></TD></TR>
<TR><TD>#Request.f#Page requests served</FONT></TD><TD>#Request.f##NumberFormat(info.Requests, ",")#</FONT></TD></TR>
<TR><TD>#Request.f#Running / queued / timed out</FONT></TD><TD>#Request.f##info.Active# / #info.Queued# / #info.TimedOut#</FONT></TD></TR>
<TR><TD>#Request.f#Cached templates / queries</FONT></TD><TD>#Request.f##info.CachedTemplates# / #info.CachedQueries#</FONT></TD></TR>
<TR><TD>#Request.f#Install directory</FONT></TD><TD>#Request.f#<TT>#info.Root#</TT></FONT></TD></TR>
<TR><TD>#Request.f#Web root</FONT></TD><TD>#Request.f#<TT>#info.WebRoot#</TT></FONT></TD></TR>
<TR><TD>#Request.f#Listening on</FONT></TD><TD>#Request.f#<TT>#info.Bind#:#info.Port#</TT> (process #info.PID#)</FONT></TD></TR>
</TABLE>
<cfset sess = KFUSION_SESSIONS()>
<P><TABLE WIDTH="90%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>Active Applications and Sessions</B></FONT></TD></TR></TABLE>
<TABLE BORDER=0 CELLPADDING=3 WIDTH="90%">
<cfloop query="sess">
<TR BGCOLOR="#IIf(sess.CurrentRow MOD 2, DE('FFFFFF'), DE('FFFBF0'))#"><TD>#Request.f##sess.Type#</FONT></TD><TD>#Request.f#<TT>#sess.Name#</TT></FONT></TD>
<TD>#Request.f##sess.Variables# variables</FONT></TD><TD>#Request.f#last used #TimeFormat(sess.LastAccess, "h:mm:ss tt")#</FONT></TD></TR>
</cfloop>
<cfif NOT sess.RecordCount><TR><TD>#Request.f#<I>None.</I></FONT></TD></TR></cfif>
</TABLE>
<P>#Request.f#<I>KoldFusion is a nostalgic tribute to the application servers of 1999. It is not affiliated with Allaire, Macromedia,
Adobe or anyone else who may have owned a fist-shaped logo.</I></FONT>
</cfoutput>
<cfinclude template="../_footer.cfm">
