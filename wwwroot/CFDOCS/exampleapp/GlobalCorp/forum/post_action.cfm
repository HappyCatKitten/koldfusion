<!---
	forum/post_action.cfm - saves a post, then shows it.
	A thread is identified by the Msg_ID of its first message (ThreadID),
	which makes it easy to fetch a whole thread with one query.
--->
<CFIF NOT IsDefined("Form.Topic_ID")>
	<CFLOCATION URL="index.cfm" ADDTOKEN="No">
</CFIF>
<CFPARAM NAME="Form.Email" DEFAULT="">

<!--- a reply belongs to the same thread as its parent --->
<CFSET ThreadID = 0>
<CFIF Val(Form.ParentID)>
	<CFQUERY NAME="GetParent" DATASOURCE="#Request.DSN#">
		SELECT ThreadID FROM Messages WHERE Msg_ID = #Val(Form.ParentID)#
	</CFQUERY>
	<CFSET ThreadID = Val(GetParent.ThreadID)>
</CFIF>

<CFTRANSACTION>
	<CFQUERY DATASOURCE="#Request.DSN#">
		INSERT INTO Messages (Topic_ID, ParentID, ThreadID, Subject, Body, Author, Email, Posted)
		VALUES (#Val(Form.Topic_ID)#, #Val(Form.ParentID)#, #ThreadID#,
		        '#Left(Trim(Form.Subject), 100)#', '#Trim(Form.Body)#',
		        '#Left(Trim(Form.Author), 50)#', '#Left(Trim(Form.Email), 60)#',
		        <CFQUERYPARAM CFSQLTYPE="CF_SQL_TIMESTAMP" VALUE="#Now()#">)
	</CFQUERY>
	<CFQUERY NAME="GetNew" DATASOURCE="#Request.DSN#">
		SELECT MAX(Msg_ID) AS NewID FROM Messages
	</CFQUERY>
	<!--- a brand new thread starts with its own ID --->
	<CFIF ThreadID EQ 0>
		<CFQUERY DATASOURCE="#Request.DSN#">
			UPDATE Messages SET ThreadID = #GetNew.NewID# WHERE Msg_ID = #GetNew.NewID#
		</CFQUERY>
	</CFIF>
</CFTRANSACTION>

<CFLOCATION URL="message.cfm?Msg_ID=#GetNew.NewID#&posted=yes" ADDTOKEN="No">
