<!--- Register New Applet --->
<cfparam name="Form.AppletName" default="">
<cfif IsDefined("URL.AppletName")><cfset Form.AppletName = URL.AppletName></cfif>
<cfset Form.AppletName = Trim(Form.AppletName)>
<cfif NOT Len(Form.AppletName)><cflocation url="applets.cfm" addtoken="no"></cfif>
<cfset k = Request.reg & "\Applets\" & Form.AppletName>
<cfif IsDefined("Form.Delete")><cfregistry action="delete" branch="#k#"><cflocation url="applets.cfm" addtoken="no"></cfif>
<cfif IsDefined("Form.Save")>
	<cfloop list="Codebase,Code,Method,Height,Width,VSpace,HSpace,Align,NotSupported" index="f">
		<cfregistry action="set" branch="#k#" entry="#f#" value="#Trim(Form[f])#">
	</cfloop>
	<cfregistry action="delete" branch="#k#\Params">
	<cfloop index="i" from="1" to="5">
		<cfif Len(Trim(Form["ParamName" & i]))>
			<cfregistry action="set" branch="#k#\Params" entry="#Trim(Form['ParamName' & i])#" value="#Form['ParamValue' & i]#">
		</cfif>
	</cfloop>
	<cflocation url="applets.cfm" addtoken="no">
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="Applets\#Form.AppletName#" variable="A">
<cfset isNew = NOT StructKeyExists(A, "Code")>
<cfloop list="Codebase,Code,Method,NotSupported" index="f"><cfparam name="A.#f#" default=""></cfloop>
<cfparam name="A.Height" default="100"><cfparam name="A.Width" default="200"><cfparam name="A.VSpace" default="0">
<cfparam name="A.HSpace" default="0"><cfparam name="A.Align" default="LEFT">
<cfif isNew><cfset A.NotSupported = "<B>Browser must support Java to view KoldFusion Java Applets</B>"></cfif>
<cfregistry action="getall" branch="#k#\Params" name="params" type="string">
<cfset pageTitle = "Register New Applet">
<cfinclude template="../_header.cfm">
<cfoutput>
<FORM ACTION="appletedit.cfm" METHOD="POST"><INPUT TYPE="hidden" NAME="AppletName" VALUE="#HTMLEditFormat(Form.AppletName)#">
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD>#Request.f#<B>Applet Name</B></FONT></TD><TD>#Request.f#<B>#HTMLEditFormat(Form.AppletName)#</B></FONT></TD></TR>
<TR><TD>#Request.f#<B>Codebase</B></FONT></TD><TD><INPUT TYPE="text" NAME="Codebase" VALUE="#HTMLEditFormat(A.Codebase)#" SIZE=40></TD></TR>
<TR><TD>#Request.f#<B>Code</B></FONT></TD><TD><INPUT TYPE="text" NAME="Code" VALUE="#HTMLEditFormat(A.Code)#" SIZE=40></TD></TR>
<TR><TD>#Request.f#<B>Method</B></FONT></TD><TD><INPUT TYPE="text" NAME="Method" VALUE="#HTMLEditFormat(A.Method)#" SIZE=20></TD></TR>
<TR><TD>#Request.f#<B>Height</B></FONT></TD><TD><INPUT TYPE="text" NAME="Height" VALUE="#A.Height#" SIZE=4> #Request.f#<B>Width</B></FONT> <INPUT TYPE="text" NAME="Width" VALUE="#A.Width#" SIZE=4>
	#Request.f#<B>VSpace</B></FONT> <INPUT TYPE="text" NAME="VSpace" VALUE="#A.VSpace#" SIZE=3> #Request.f#<B>HSpace</B></FONT> <INPUT TYPE="text" NAME="HSpace" VALUE="#A.HSpace#" SIZE=3></TD></TR>
<TR><TD>#Request.f#<B>Align</B></FONT></TD><TD><SELECT NAME="Align"><cfloop list="LEFT,RIGHT,TOP,TEXTTOP,MIDDLE,ABSMIDDLE,BASELINE,BOTTOM,ABSBOTTOM" index="al"><OPTION<cfif A.Align EQ al> SELECTED</cfif>>#al#</cfloop></SELECT></TD></TR>
<TR><TD VALIGN=TOP>#Request.f#<B>Java Not Supported Message</B></FONT></TD><TD><TEXTAREA NAME="NotSupported" ROWS=3 COLS=45>#HTMLEditFormat(A.NotSupported)#</TEXTAREA></TD></TR>
</TABLE>
<P><TABLE BORDER=0 CELLPADDING=2><TR><TD>#Request.f#<B>Parameter Name</B></FONT></TD><TD>#Request.f#<B>Value</B></FONT></TD></TR>
<cfloop index="i" from="1" to="5">
<TR><TD><INPUT TYPE="text" NAME="ParamName#i#" VALUE="<cfif i LTE params.RecordCount>#HTMLEditFormat(params.Entry[i])#</cfif>" SIZE=20></TD>
<TD><INPUT TYPE="text" NAME="ParamValue#i#" VALUE="<cfif i LTE params.RecordCount>#HTMLEditFormat(params.Value[i])#</cfif>" SIZE=30></TD></TR>
</cfloop></TABLE>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Save" VALUE="#IIf(isNew, DE('Create'), DE('Update'))#">
<cfif NOT isNew><INPUT TYPE="submit" NAME="Delete" VALUE="Delete"></cfif>
<INPUT TYPE="button" VALUE="Cancel" onClick="location='applets.cfm'">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
