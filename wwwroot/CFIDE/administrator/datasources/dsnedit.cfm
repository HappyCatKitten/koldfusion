<!--- Create / edit a data source --->
<cfparam name="Form.DSN" default="">
<cfif IsDefined("URL.DSN")><cfset Form.DSN = URL.DSN></cfif>
<cfset Form.DSN = Trim(Form.DSN)>
<cfset base = Request.reg & "\DataSources">
<cfset msg = "">
<cfset back = "odbc.cfm">
<cfif NOT Len(Form.DSN)><cflocation url="odbc.cfm" addtoken="no"></cfif>
<cfif REFind("[^A-Za-z0-9_ -]", Form.DSN)>
	<cfset msg = "Data source names may contain only letters, digits, spaces, hyphens and underscores.">
</cfif>
<cfif IsDefined("Form.Delete")>
	<cfregistry action="delete" branch="#base#\#Form.DSN#">
	<cfset pageTitle = "Data Source Deleted">
	<cfinclude template="../_header.cfm">
	<cfmodule template="../_tags/status.cfm" message="The data source #HTMLEditFormat(Form.DSN)# has been deleted. (Its database directory was left on disk.)" back="odbc.cfm">
	<cfinclude template="../_footer.cfm">
	<cfabort>
</cfif>
<cfif IsDefined("Form.Save") AND NOT Len(msg)>
	<cfset k = base & "\" & Form.DSN>
	<cfloop list="Driver,Kind,Database,Description,Username,LoginTimeout,MaxConnections,ConnectionTimeout,PageTimeout,BufferSize,SystemDatabase,Server,HostString,Provider,LongTextBuffer" index="f">
		<cfif IsDefined("Form." & f)><cfregistry action="set" branch="#k#" entry="#f#" value="#Trim(Form[f])#"></cfif>
	</cfloop>
	<cfif Form.Password NEQ "********"><cfregistry action="set" branch="#k#" entry="Password" value="#KFUSION_ENCRYPT(Form.Password)#"></cfif>
	<cfloop list="LimitConnections,MaintainConnections,Disabled,LongText" index="f">
		<cfregistry action="set" branch="#k#" entry="#f#" value="#IIf(IsDefined('Form.' & f), 1, 0)#">
	</cfloop>
	<cfparam name="Form.Restrict" default="">
	<cfregistry action="set" branch="#k#" entry="Restrict" value="#Form.Restrict#">
	<cfset KFUSION_DBCREATE(Form.DSN)>
	<cfset v = KFUSION_VERIFYDSN(Form.DSN)>
	<cfset msg = IIf(v.OK, DE("The data source #Form.DSN# has been saved. #v.Message#"), DE("The data source #Form.DSN# has been saved, but it could not be verified: #v.Message#"))>
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="DataSources\#Form.DSN#" variable="D">
<cfset isNew = NOT StructKeyExists(D, "Driver")>
<cfif isNew>
	<cfparam name="Form.Kind" default="ODBC">
	<cfparam name="Form.Driver" default="Microsoft Access Driver (*.mdb)">
	<cfset D = StructNew()>
	<cfset D.Driver = Form.Driver><cfset D.Kind = Form.Kind><cfset D.Database = LCase(REReplace(Form.DSN, "[^A-Za-z0-9_]", "", "ALL"))>
	<cfset D.Description = ""><cfset D.Username = ""><cfset D.LoginTimeout = 30><cfset D.MaintainConnections = 1><cfset D.Disabled = 0>
	<cfset D.Restrict = ""><cfset D.PageTimeout = 600><cfset D.BufferSize = 0><cfset D.LongText = 0><cfset D.LongTextBuffer = 65000>
</cfif>
<cfloop list="Server,HostString,Provider,SystemDatabase,LimitConnections,MaxConnections,ConnectionTimeout,LongText,LongTextBuffer,PageTimeout,BufferSize" index="f">
	<cfif NOT StructKeyExists(D, f)><cfset D[f] = ""></cfif>
</cfloop>
<cfif D.Kind EQ "Native"><cfset back = "native.cfm"><cfelseif D.Kind EQ "OLEDB"><cfset back = "oledb.cfm"></cfif>
<cfset pageTitle = IIf(isNew, DE("Create #D.Kind# Data Source"), DE("Edit #D.Kind# Data Source"))>
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<SCRIPT LANGUAGE="JavaScript">
<!--
function toggleCF() {
	var el = document.getElementById ? document.getElementById('cfsettings') : null;
	if (el) el.style.display = (el.style.display == 'none') ? 'block' : 'none';
}
//-->
</SCRIPT>
<FORM ACTION="dsnedit.cfm" METHOD="POST">
<INPUT TYPE="hidden" NAME="Kind" VALUE="#D.Kind#">
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD>#Request.f#<B>Data Source Name</B></FONT></TD><TD>#Request.f#<B>#HTMLEditFormat(Form.DSN)#</B></FONT><INPUT TYPE="hidden" NAME="DSN" VALUE="#HTMLEditFormat(Form.DSN)#"></TD></TR>
<TR><TD>#Request.f#<B>#IIf(D.Kind EQ "OLEDB", DE("Provider"), DE("Driver"))#</B></FONT></TD><TD><INPUT TYPE="text" NAME="Driver" VALUE="#HTMLEditFormat(D.Driver)#" SIZE=40></TD></TR>
<TR><TD>#Request.f#<B>Description</B></FONT></TD><TD><INPUT TYPE="text" NAME="Description" VALUE="#HTMLEditFormat(D.Description)#" SIZE=40></TD></TR>
<cfif D.Kind EQ "Native">
<TR><TD>#Request.f#<B>Host String</B></FONT></TD><TD><INPUT TYPE="text" NAME="HostString" VALUE="#HTMLEditFormat(D.HostString)#" SIZE=30> #Request.f#<I>(the Net8 / Sybase server alias)</I></FONT></TD></TR>
<cfelseif D.Driver CONTAINS "SQL Server">
<TR><TD>#Request.f#<B>Server</B></FONT></TD><TD><INPUT TYPE="text" NAME="Server" VALUE="#HTMLEditFormat(D.Server)#" SIZE=30></TD></TR>
</cfif>
<TR><TD>#Request.f#<B>Database #IIf(D.Driver CONTAINS "Access" OR D.Driver CONTAINS "*.", DE("File"), DE(""))#</B></FONT></TD>
	<TD><INPUT TYPE="text" NAME="Database" VALUE="#HTMLEditFormat(D.Database)#" SIZE=40 STYLE="font-family:Courier New,monospace"></TD></TR>
<cfif D.Driver CONTAINS "Access">
<TR><TD>#Request.f#<B>System Database</B></FONT></TD><TD><INPUT TYPE="text" NAME="SystemDatabase" VALUE="#HTMLEditFormat(D.SystemDatabase)#" SIZE=40></TD></TR>
<TR><TD>#Request.f#<B>Page Timeout</B></FONT></TD><TD><INPUT TYPE="text" NAME="PageTimeout" VALUE="#D.PageTimeout#" SIZE=5> &nbsp; #Request.f#<B>Buffer Size</B></FONT> <INPUT TYPE="text" NAME="BufferSize" VALUE="#D.BufferSize#" SIZE=5></TD></TR>
</cfif>
<TR><TD>#Request.f#<B>Login Name</B></FONT></TD><TD><INPUT TYPE="text" NAME="Username" VALUE="#HTMLEditFormat(D.Username)#" SIZE=20></TD></TR>
<TR><TD>#Request.f#<B>Password</B></FONT></TD><TD><INPUT TYPE="password" NAME="Password" VALUE="********" SIZE=20></TD></TR>
</TABLE>
<P>#Request.f#<I>The database is a directory of KoldFusion tables. A plain name is created under #KFUSION_SERVERINFO().Root#/db.</I></FONT>
<P><INPUT TYPE="button" VALUE="CF Settings &gt;&gt;" onClick="toggleCF()">
<DIV ID="cfsettings" STYLE="display:none">
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>KoldFusion Settings</B></FONT></TD></TR></TABLE>
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD>#Request.f#<B>Login Timeout</B></FONT></TD><TD>#Request.f#<INPUT TYPE="text" NAME="LoginTimeout" VALUE="#D.LoginTimeout#" SIZE=4> seconds</FONT></TD></TR>
<TR><TD>#Request.f#<B>Limit Connections</B></FONT></TD><TD>#Request.f#<INPUT TYPE="checkbox" NAME="LimitConnections" VALUE="1"<cfif D.LimitConnections EQ 1> CHECKED</cfif>> to <INPUT TYPE="text" NAME="MaxConnections" VALUE="#D.MaxConnections#" SIZE=4> connections</FONT></TD></TR>
<TR><TD>#Request.f#<B>Maintain database connections</B></FONT></TD><TD><INPUT TYPE="checkbox" NAME="MaintainConnections" VALUE="1"<cfif D.MaintainConnections EQ 1> CHECKED</cfif>></TD></TR>
<TR><TD>#Request.f#<B>Disable Database Connections</B></FONT></TD><TD><INPUT TYPE="checkbox" NAME="Disabled" VALUE="1"<cfif D.Disabled EQ 1> CHECKED</cfif>></TD></TR>
<TR><TD>#Request.f#<B>Connection timeout</B></FONT></TD><TD>#Request.f#<INPUT TYPE="text" NAME="ConnectionTimeout" VALUE="#D.ConnectionTimeout#" SIZE=4> minutes</FONT></TD></TR>
<TR><TD VALIGN=TOP>#Request.f#<B>Restrict SQL Operations</B></FONT></TD><TD>#Request.f#
	<cfloop list="SELECT,INSERT,UPDATE,DELETE,SP" index="op"><INPUT TYPE="checkbox" NAME="Restrict" VALUE="#op#"<cfif ListFindNoCase(D.Restrict, op)> CHECKED</cfif>> #IIf(op EQ "SP", DE("Stored Procedures"), DE(op))# &nbsp;</cfloop>
	<BR><I>Checked operations are not allowed on this data source.</I></FONT></TD></TR>
<TR><TD>#Request.f#<B>Enable retrieval of long text</B></FONT></TD><TD><INPUT TYPE="checkbox" NAME="LongText" VALUE="1"<cfif D.LongText EQ 1> CHECKED</cfif>></TD></TR>
<TR><TD>#Request.f#<B>Long Text Buffer Size</B></FONT></TD><TD><INPUT TYPE="text" NAME="LongTextBuffer" VALUE="#D.LongTextBuffer#" SIZE=7></TD></TR>
</TABLE>
</DIV>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Save" VALUE="#IIf(isNew, DE('Create'), DE('Update'))#">
<cfif NOT isNew><INPUT TYPE="submit" NAME="Delete" VALUE="Delete" onClick="return confirm('Delete this data source?')">
<INPUT TYPE="button" VALUE="View Tables..." onClick="location='tables.cfm?DSN=#URLEncodedFormat(Form.DSN)#'"></cfif>
<INPUT TYPE="button" VALUE="Cancel" onClick="location='#back#'">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
