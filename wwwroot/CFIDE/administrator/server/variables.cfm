<!--- Variables: client storage, session and application variables --->
<cfset msg = "">
<cfif IsDefined("Form.Apply")>
	<cfset ok = true>
	<cfloop list="AppMax,AppDef,SessMax,SessDef" index="g">
		<cfloop list="d,h,m,s" index="u">
			<cfif NOT IsNumeric(Form[g & u])><cfset ok = false></cfif>
		</cfloop>
	</cfloop>
	<cfif ok>
		<cfmodule template="../_tags/setreg.cfm" key="Variables" entry="ApplicationTimeoutMax" value="#CreateTimeSpan(Form.AppMaxd, Form.AppMaxh, Form.AppMaxm, Form.AppMaxs)#">
		<cfmodule template="../_tags/setreg.cfm" key="Variables" entry="ApplicationTimeoutDefault" value="#CreateTimeSpan(Form.AppDefd, Form.AppDefh, Form.AppDefm, Form.AppDefs)#">
		<cfmodule template="../_tags/setreg.cfm" key="Variables" entry="SessionTimeoutMax" value="#CreateTimeSpan(Form.SessMaxd, Form.SessMaxh, Form.SessMaxm, Form.SessMaxs)#">
		<cfmodule template="../_tags/setreg.cfm" key="Variables" entry="SessionTimeoutDefault" value="#CreateTimeSpan(Form.SessDefd, Form.SessDefh, Form.SessDefm, Form.SessDefs)#">
		<cfmodule template="../_tags/setreg.cfm" key="Variables" entry="EnableApplicationVariables" value="#IIf(IsDefined('Form.EnableApplicationVariables'), 1, 0)#">
		<cfmodule template="../_tags/setreg.cfm" key="Variables" entry="EnableSessionVariables" value="#IIf(IsDefined('Form.EnableSessionVariables'), 1, 0)#">
		<cfmodule template="../_tags/setreg.cfm" key="Variables" entry="DefaultClientStorage" value="#Form.DefaultClientStorage#">
		<cfset msg = "Variable settings have been applied.">
	<cfelse>
		<cfset msg = "All timeout values must be numeric.">
	</cfif>
</cfif>
<cfif IsDefined("URL.removestore")>
	<cfregistry action="delete" branch="#Request.reg#\Variables\ClientStores\#URL.removestore#">
	<cfset msg = "Client storage #URL.removestore# has been removed.">
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="Variables" variable="V">
<cfregistry action="getall" branch="#Request.reg#\Variables\ClientStores" name="stores" type="key">
<cfset dsns = KFUSION_DSNLIST()>
<cfset pageTitle = "Variables">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="clientstore.cfm" METHOD="POST">
<P>#Request.f#<B>Client Variable Storage</B><BR>
To configure a data source for client variable storage, first configure an ODBC or native data source, then select it from the list below.</FONT>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="##669966"><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Name</B></FONT></TD><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>Type</B></FONT></TD></TR>
<TR BGCOLOR="##FFFFFF"><TD><SELECT NAME="StoreDSN"><cfloop query="dsns"><OPTION>#dsns.Name#</cfloop></SELECT> <INPUT TYPE="submit" VALUE="Add..."></TD><TD></TD></TR>
<TR BGCOLOR="##FFFBF0"><TD>#Request.f#<B><U>Registry</U></B></FONT></TD><TD>#Request.f#System Registry</FONT></TD></TR>
<TR BGCOLOR="##FFFFFF"><TD>#Request.f#<B><U>Cookie</U></B></FONT></TD><TD>#Request.f#Browser Cookie</FONT></TD></TR>
<cfloop query="stores">
<TR BGCOLOR="#IIf(stores.CurrentRow MOD 2, DE('FFFBF0'), DE('FFFFFF'))#"><TD>#Request.f#<B><A HREF="clientstore.cfm?StoreDSN=#URLEncodedFormat(stores.Entry)#">#stores.Entry#</A></B></FONT></TD>
<TD>#Request.f#Data Source &nbsp; <A HREF="variables.cfm?removestore=#URLEncodedFormat(stores.Entry)#">remove</A></FONT></TD></TR>
</cfloop>
</TABLE>
</FORM>

<FORM ACTION="variables.cfm" METHOD="POST">
<P>#Request.f#<B>Default Client Variable Storage</B><BR>
<SELECT NAME="DefaultClientStorage">
<cfloop list="Registry,Cookie" index="s"><OPTION<cfif V.DefaultClientStorage EQ s> SELECTED</cfif>>#s#</cfloop>
<cfloop query="stores"><OPTION<cfif V.DefaultClientStorage EQ stores.Entry> SELECTED</cfif>>#stores.Entry#</cfloop>
</SELECT><BR>
Select the system-wide default for client variable storage. This setting is used when no CLIENTSTORAGE attribute is specified in a
CFAPPLICATION tag.</FONT>

<P><TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>Session and Application Variables</B></FONT></TD></TR></TABLE>
<P>#Request.f#<INPUT TYPE="checkbox" NAME="EnableApplicationVariables" VALUE="1"<cfif V.EnableApplicationVariables EQ 1> CHECKED</cfif>> <B>Enable application variables</B>
&nbsp;&nbsp;&nbsp; <INPUT TYPE="checkbox" NAME="EnableSessionVariables" VALUE="1"<cfif V.EnableSessionVariables EQ 1> CHECKED</cfif>> <B>Enable session variables</B></FONT>
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD></TD><TD>#Request.f#<I>days</I></FONT></TD><TD>#Request.f#<I>hrs</I></FONT></TD><TD>#Request.f#<I>mins</I></FONT></TD><TD>#Request.f#<I>secs</I></FONT></TD></TR>
<cfloop list="AppMax:ApplicationTimeoutMax:Application Variables Maximum Timeout,AppDef:ApplicationTimeoutDefault:Application Variables Default Timeout,SessMax:SessionTimeoutMax:Session Variables Maximum Timeout,SessDef:SessionTimeoutDefault:Session Variables Default Timeout" index="row">
	<cfset fld = ListGetAt(row, 1, ":")>
	<cfset t = V[ListGetAt(row, 2, ":")]>
	<cfset secs = Round(t * 86400)>
	<TR><TD>#Request.f#<B>#ListGetAt(row, 3, ":")#</B></FONT></TD>
	<TD><INPUT TYPE="text" NAME="#fld#d" VALUE="#Int(secs / 86400)#" SIZE=2></TD>
	<TD><INPUT TYPE="text" NAME="#fld#h" VALUE="#Int(secs / 3600) MOD 24#" SIZE=2></TD>
	<TD><INPUT TYPE="text" NAME="#fld#m" VALUE="#Int(secs / 60) MOD 60#" SIZE=2></TD>
	<TD><INPUT TYPE="text" NAME="#fld#s" VALUE="#secs MOD 60#" SIZE=2></TD></TR>
</cfloop>
</TABLE>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Apply" VALUE="Apply"> <INPUT TYPE="reset" VALUE="Cancel">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
