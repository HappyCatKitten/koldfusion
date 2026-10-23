<!--- Create Client Variable Storage --->
<cfparam name="Form.StoreDSN" default="">
<cfif IsDefined("URL.StoreDSN")><cfset Form.StoreDSN = URL.StoreDSN></cfif>
<cfset msg = "">
<cfif IsDefined("Form.Create")>
	<cfif Form.StoreDSN EQ "Registry" OR Form.StoreDSN EQ "Cookie">
		<cfset msg = "The data source name may not be Registry or Cookie.">
	<cfelse>
		<cfset k = Request.reg & "\Variables\ClientStores\" & Form.StoreDSN>
		<cfregistry action="set" branch="#k#" entry="PurgeDays" value="#Val(Form.PurgeDays)#">
		<cfregistry action="set" branch="#k#" entry="Purge" value="#IIf(IsDefined('Form.Purge'), 1, 0)#">
		<cfregistry action="set" branch="#k#" entry="DisableGlobalUpdates" value="#IIf(IsDefined('Form.DisableGlobalUpdates'), 1, 0)#">
		<cfif IsDefined("Form.CreateTables")>
			<cftry>
				<cfquery datasource="#Form.StoreDSN#">CREATE TABLE IF NOT EXISTS CDATA (cfid VARCHAR(64), app VARCHAR(64), data MEMO)</cfquery>
				<cfquery datasource="#Form.StoreDSN#">CREATE TABLE IF NOT EXISTS CGLOBAL (cfid VARCHAR(64), data MEMO, lvisit DATETIME)</cfquery>
				<cfcatch type="Database"><cfset msg = "Could not create client tables: #cfcatch.Message#"></cfcatch>
			</cftry>
		</cfif>
		<cfif NOT Len(msg)><cflocation url="variables.cfm" addtoken="no"></cfif>
	</cfif>
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="Variables\ClientStores\#Form.StoreDSN#" variable="C">
<cfparam name="C.PurgeDays" default="90"><cfparam name="C.Purge" default="1"><cfparam name="C.DisableGlobalUpdates" default="0">
<cfset pageTitle = "Create Client Variable Storage: #Form.StoreDSN#">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="clientstore.cfm" METHOD="POST"><INPUT TYPE="hidden" NAME="StoreDSN" VALUE="#HTMLEditFormat(Form.StoreDSN)#">
<P>#Request.f#<INPUT TYPE="checkbox" NAME="Purge" VALUE="1"<cfif C.Purge EQ 1> CHECKED</cfif>>
<B>Purge data for clients that remain unvisited for</B> <INPUT TYPE="text" NAME="PurgeDays" VALUE="#C.PurgeDays#" SIZE=3> <B>days.</B><BR>
Enable this option if you want KoldFusion to periodically purge client data that has not been accessed in the specified number of days.
If this data source is being used by more than one KoldFusion server, as in the case of clustered servers, make sure that only one
server in the cluster is configured to purge client data.</FONT>
<P>#Request.f#<INPUT TYPE="checkbox" NAME="DisableGlobalUpdates" VALUE="1"<cfif C.DisableGlobalUpdates EQ 1> CHECKED</cfif>>
<B>Disable global client variable updates</B><BR>
This option controls how KoldFusion updates global client variables, such as HITCOUNT and LASTVISIT. If updates are disabled,
KoldFusion updates these variables only when they are set or modified. If updates are enabled, KoldFusion updates global client
variables for each page request.</FONT>
<P>#Request.f#<INPUT TYPE="checkbox" NAME="CreateTables" VALUE="1" CHECKED> <B>Create Client database tables</B><BR>
Enable this option only if this is the first time you are configuring the current data source for client variable storage. If the
current data source has already been configured for client variable storage, do not enable this option.</FONT>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Create" VALUE="Create"> <INPUT TYPE="button" VALUE="Cancel" onClick="location='variables.cfm'">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
