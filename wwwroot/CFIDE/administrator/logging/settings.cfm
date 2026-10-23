<!--- General Error Logging --->
<cfset msg = "">
<cfif IsDefined("Form.Apply")>
	<cfif NOT DirectoryExists(Trim(Form.LogDirectory))>
		<cfset msg = "The log directory #HTMLEditFormat(Form.LogDirectory)# does not exist.">
	<cfelse>
		<cfmodule template="../_tags/setreg.cfm" key="Server" entry="AdminEmail" value="#Trim(Form.AdminEmail)#">
		<cfmodule template="../_tags/setreg.cfm" key="Server" entry="LogDirectory" value="#Trim(Form.LogDirectory)#">
		<cfmodule template="../_tags/setreg.cfm" key="Logging" entry="LogSlowPages" value="#IIf(IsDefined('Form.LogSlowPages'), 1, 0)#">
		<cfmodule template="../_tags/setreg.cfm" key="Logging" entry="SlowPageSeconds" value="#Val(Form.SlowPageSeconds)#">
		<cfmodule template="../_tags/setreg.cfm" key="Logging" entry="SystemLogging" value="#IIf(IsDefined('Form.SystemLogging'), 1, 0)#">
		<cfset msg = "Logging settings have been applied.">
	</cfif>
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="Server" variable="S">
<cfmodule template="../_tags/getreg.cfm" key="Logging" variable="L">
<cfset pageTitle = "General Error Logging">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="settings.cfm" METHOD="POST">
<P>#Request.f#<B>Administrator E-Mail</B><BR><INPUT TYPE="text" NAME="AdminEmail" VALUE="#HTMLEditFormat(S.AdminEmail)#" SIZE=40><BR>
Type in the email address of the server administrator. This address will appear under each error message for reporting purposes.
This global setting can be overridden in specific web applications using the application framework in the Application.cfm file.</FONT>
<P>#Request.f#<B>Log Directory</B><BR><INPUT TYPE="text" NAME="LogDirectory" VALUE="#HTMLEditFormat(S.LogDirectory)#" SIZE=50 STYLE="font-family:Courier New,monospace">
<INPUT TYPE="button" VALUE="Browse Server..." onClick="browseServer('LogDirectory')"><BR>
Type in the directory to which error log files are written or click <B>Browse Server</B> to select from the directory tree. The drive
you specify must have sufficient disk space and security privileges for the KoldFusion system service.</FONT>
<P>#Request.f#<B>Log Slow Pages</B><BR><INPUT TYPE="checkbox" NAME="LogSlowPages" VALUE="1"<cfif L.LogSlowPages EQ 1> CHECKED</cfif>>
Log pages taking longer than <INPUT TYPE="text" NAME="SlowPageSeconds" VALUE="#L.SlowPageSeconds#" SIZE=3> seconds<BR>
To help diagnose potential problems or bottlenecks in your site, you can have KoldFusion log the names of any pages that take over a
specified length of time to return. When enabled, any output will be written to the "server.log".</FONT>
<P>#Request.f#<B>System Logging</B><BR><INPUT TYPE="checkbox" NAME="SystemLogging" VALUE="1"<cfif L.SystemLogging EQ 1> CHECKED</cfif>>
Use UNIX syslog<BR>Send error messages to the system log in addition to the KoldFusion log files.</FONT>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Apply" VALUE="Apply"> <INPUT TYPE="reset" VALUE="Cancel">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
