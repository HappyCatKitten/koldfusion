<!--- Add / edit a scheduled task --->
<cfparam name="Form.TaskName" default="">
<cfif IsDefined("URL.TaskName")><cfset Form.TaskName = URL.TaskName></cfif>
<cfset Form.TaskName = Trim(Form.TaskName)>
<cfif NOT Len(Form.TaskName)><cflocation url="tasks.cfm" addtoken="no"></cfif>
<cfset msg = "">
<cfif IsDefined("Form.Save")>
	<cfif Form.Schedule EQ "once"><cfset interval = "once">
	<cfelseif Form.Schedule EQ "recurring"><cfset interval = Form.Recurrence>
	<cfelse><cfset interval = Val(Form.EveryMinutes) * 60></cfif>
	<cfif Form.Schedule EQ "once"><cfset stime = Form.OnceTime>
	<cfelseif Form.Schedule EQ "recurring"><cfset stime = Form.RecurTime>
	<cfelse><cfset stime = Form.DailyStart></cfif>
	<cftry>
		<cfschedule action="update" task="#Form.TaskName#" operation="HTTPRequest" url="#Form.URL#"
			startdate="#Form.StartDate#" starttime="#stime#" enddate="#Form.EndDate#"
			endtime="#IIf(Form.Schedule EQ 'daily', 'Form.DailyEnd', DE(''))#" interval="#interval#"
			requesttimeout="#Val(Form.RequestTimeout)#" username="#Form.Username#" password="#Form.Password#"
			proxyserver="#Form.ProxyServer#" publish="#IIf(IsDefined('Form.Publish'), DE('yes'), DE('no'))#"
			path="#Form.PublishPath#" file="#Form.PublishFile#" resolveurl="#IIf(IsDefined('Form.ResolveURL'), DE('yes'), DE('no'))#">
		<cflocation url="tasks.cfm" addtoken="no">
		<cfcatch type="Application"><cfset msg = cfcatch.Detail></cfcatch>
	</cftry>
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="Schedule\#Form.TaskName#" variable="T">
<cfset isNew = NOT StructKeyExists(T, "url")>
<cfloop list="url,username,password,proxyserver,path,file,enddate,endtime,publish,resolveurl" index="f"><cfparam name="T.#f#" default=""></cfloop>
<cfparam name="T.startdate" default="#DateFormat(Now(), 'mm/dd/yyyy')#">
<cfparam name="T.starttime" default="#TimeFormat(DateAdd('n', 15, Now()), 'HH:mm:ss')#">
<cfparam name="T.interval" default="once">
<cfparam name="T.requesttimeout" default="30">
<cfif T.interval EQ "once"><cfset mode = "once"><cfelseif IsNumeric(T.interval)><cfset mode = "daily"><cfelse><cfset mode = "recurring"></cfif>
<cfset pageTitle = IIf(isNew, DE("Add Scheduler Task"), DE("Edit Scheduler Task"))>
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="taskedit.cfm" METHOD="POST"><INPUT TYPE="hidden" NAME="TaskName" VALUE="#HTMLEditFormat(Form.TaskName)#">
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD>#Request.f#<B>Task Name</B></FONT></TD><TD>#Request.f#<B>#HTMLEditFormat(Form.TaskName)#</B></FONT></TD></TR>
<TR><TD VALIGN=TOP>#Request.f#<B>Duration</B></FONT></TD><TD>#Request.f#Start Date: <INPUT TYPE="text" NAME="StartDate" VALUE="#T.startdate#" SIZE=10>
	&nbsp; End Date: <INPUT TYPE="text" NAME="EndDate" VALUE="#T.enddate#" SIZE=10> (optional)</FONT></TD></TR>
<TR><TD VALIGN=TOP>#Request.f#<B>Schedule to run</B></FONT></TD><TD>#Request.f#
	<B>Note: The Scheduler checks for newly scheduled tasks every minute.</B><BR>
	<INPUT TYPE="radio" NAME="Schedule" VALUE="once"<cfif mode EQ "once"> CHECKED</cfif>> <B>One-time.</B>
	Schedules to run the task once on the Start Date. Specify the time: <INPUT TYPE="text" NAME="OnceTime" VALUE="#T.starttime#" SIZE=8>
	when you would like the task to execute.<BR>
	<INPUT TYPE="radio" NAME="Schedule" VALUE="recurring"<cfif mode EQ "recurring"> CHECKED</cfif>> <B>Recurring</B>
	<SELECT NAME="Recurrence"><cfloop list="Daily,Weekly,Monthly" index="r"><OPTION VALUE="#LCase(r)#"<cfif T.interval EQ r> SELECTED</cfif>>#r#</cfloop></SELECT>
	Schedules tasks which occur once every day, week or month for the duration of the task. The scheduling begins on Start Date and
	occurs every scheduled day at time: <INPUT TYPE="text" NAME="RecurTime" VALUE="#T.starttime#" SIZE=8><BR>
	<INPUT TYPE="radio" NAME="Schedule" VALUE="daily"<cfif mode EQ "daily"> CHECKED</cfif>> <B>Daily every</B>
	<INPUT TYPE="text" NAME="EveryMinutes" VALUE="#IIf(IsNumeric(T.interval), 'T.interval / 60', DE('60'))#" SIZE=4> <B>minutes</B>
	between <INPUT TYPE="text" NAME="DailyStart" VALUE="#T.starttime#" SIZE=8> and <INPUT TYPE="text" NAME="DailyEnd" VALUE="#T.endtime#" SIZE=8>.<BR>
	<I>Times are on the 24 hour clock.</I></FONT></TD></TR>
<TR><TD>#Request.f#<B>Operation</B></FONT></TD><TD>#Request.f#HTTPRequest</FONT></TD></TR>
<TR><TD>#Request.f#<B>URL</B></FONT></TD><TD><INPUT TYPE="text" NAME="URL" VALUE="#HTMLEditFormat(T.url)#" SIZE=50></TD></TR>
<TR><TD>#Request.f#<B>Username</B></FONT></TD><TD><INPUT TYPE="text" NAME="Username" VALUE="#HTMLEditFormat(T.username)#" SIZE=15>
	#Request.f#<B>Password</B></FONT> <INPUT TYPE="password" NAME="Password" VALUE="#HTMLEditFormat(KFUSION_DECRYPT(T.password))#" SIZE=15></TD></TR>
<TR><TD>#Request.f#<B>Request Time out</B></FONT></TD><TD>#Request.f#<INPUT TYPE="text" NAME="RequestTimeout" VALUE="#T.requesttimeout#" SIZE=4> seconds</FONT></TD></TR>
<TR><TD>#Request.f#<B>Proxy server</B></FONT></TD><TD><INPUT TYPE="text" NAME="ProxyServer" VALUE="#HTMLEditFormat(T.proxyserver)#" SIZE=30></TD></TR>
<TR><TD VALIGN=TOP>#Request.f#<B>Publish</B></FONT></TD><TD>#Request.f#<INPUT TYPE="checkbox" NAME="Publish" VALUE="1"<cfif T.publish EQ "yes"> CHECKED</cfif>> Save output to a file<BR>
	File <INPUT TYPE="text" NAME="PublishPath" VALUE="#HTMLEditFormat(T.path)#" SIZE=30 STYLE="font-family:Courier New,monospace"> /
	<INPUT TYPE="text" NAME="PublishFile" VALUE="#HTMLEditFormat(T.file)#" SIZE=15><BR>
	<INPUT TYPE="checkbox" NAME="ResolveURL" VALUE="1"<cfif T.resolveurl EQ "yes"> CHECKED</cfif>> Resolve URL (make relative links absolute)</FONT></TD></TR>
</TABLE>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Save" VALUE="#IIf(isNew, DE('Create'), DE('Update'))#"> <INPUT TYPE="button" VALUE="Cancel" onClick="location='tasks.cfm'">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
