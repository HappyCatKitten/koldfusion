<!--- New / edit CFX Tag --->
<cfparam name="Form.TagName" default="">
<cfif IsDefined("URL.TagName")><cfset Form.TagName = URL.TagName></cfif>
<cfset Form.TagName = UCase(Trim(Form.TagName))>
<cfif Left(Form.TagName, 4) NEQ "CFX_" OR Len(Form.TagName) LTE 4>
	<cfset pageTitle = "New CFX Tag">
	<cfinclude template="../_header.cfm">
	<cfmodule template="../_tags/status.cfm" message="CFX tag names must begin with CFX_ (for example CFX_ZIP)." back="cfx.cfm">
	<cfinclude template="../_footer.cfm">
	<cfabort>
</cfif>
<cfset k = Request.reg & "\CFX\" & Form.TagName>
<cfif IsDefined("Form.Delete")>
	<cfregistry action="delete" branch="#k#"><cflocation url="cfx.cfm" addtoken="no">
</cfif>
<cfif IsDefined("Form.Save")>
	<cfif IsDefined("Form.ClassName")>
		<!--- a class name, not a file name: "JavaHello.class" or "com/acme/Zip" work too --->
		<cfset Form.ClassName = Replace(REReplaceNoCase(Trim(Form.ClassName), "\.class$", ""), "/", ".", "ALL")>
		<cfif NOT Len(Form.ClassName)>
			<cfset pageTitle = "Edit CFX Tag">
			<cfinclude template="../_header.cfm">
			<cfmodule template="../_tags/status.cfm" message="Enter the name of the Java class that implements the tag." back="cfxedit.cfm?TagName=#URLEncodedFormat(Form.TagName)#">
			<cfinclude template="../_footer.cfm">
			<cfabort>
		</cfif>
	</cfif>
	<cfloop list="Type,LibraryPath,Procedure,ClassName,Description" index="f">
		<cfif IsDefined("Form." & f)><cfregistry action="set" branch="#k#" entry="#f#" value="#Trim(Form[f])#"></cfif>
	</cfloop>
	<cfif Form.Type NEQ "Java"><cfregistry action="set" branch="#k#" entry="KeepLoaded" value="#IIf(IsDefined('Form.KeepLoaded'), 1, 0)#"></cfif>
	<cflocation url="cfx.cfm" addtoken="no">
</cfif>
<cfmodule template="../_tags/getreg.cfm" key="CFX\#Form.TagName#" variable="T">
<cfset isNew = NOT StructKeyExists(T, "Type")>
<cfif isNew>
	<cfparam name="Form.TagType" default="C++">
	<cfset T = StructNew()><cfset T.Type = Form.TagType><cfset T.LibraryPath = ""><cfset T.Procedure = "ProcessTagRequest">
	<cfset T.KeepLoaded = 1><cfset T.Description = ""><cfset T.ClassName = "">
</cfif>
<cfparam name="T.ClassName" default="">
<cfset pageTitle = IIf(isNew, DE("New CFX Tag"), DE("Edit CFX Tag"))>
<cfinclude template="../_header.cfm">
<cfoutput>
<FORM ACTION="cfxedit.cfm" METHOD="POST"><INPUT TYPE="hidden" NAME="TagName" VALUE="#Form.TagName#"><INPUT TYPE="hidden" NAME="Type" VALUE="#T.Type#">
<TABLE BORDER=0 CELLPADDING=4>
<TR><TD>#Request.f#<B>Tag name</B></FONT></TD><TD>#Request.f#<B>#Form.TagName#</B> (#T.Type#)</FONT></TD></TR>
<cfif T.Type EQ "Java">
<TR><TD>#Request.f#<B>Class Name</B></FONT></TD><TD><INPUT TYPE="text" NAME="ClassName" VALUE="#HTMLEditFormat(T.ClassName)#" SIZE=40 STYLE="font-family:Courier New,monospace"><BR>
	#Request.f#The Java class that implements <TT>CustomTag</TT>, without <TT>.class</TT> (e.g. <TT>JavaHello</TT> or
	<TT>com.acme.cfx.Zip</TT>). Put it in <TT>java/classes</TT> under the KoldFusion installation, or on the Java Class Path.</FONT></TD></TR>
<cfelse>
<TR><TD>#Request.f#<B>Server library (.so)</B></FONT></TD><TD><INPUT TYPE="text" NAME="LibraryPath" VALUE="#HTMLEditFormat(T.LibraryPath)#" SIZE=40 STYLE="font-family:Courier New,monospace">
	<INPUT TYPE="button" VALUE="Browse Server..." onClick="browseServer('LibraryPath')"></TD></TR>
<TR><TD>#Request.f#<B>Procedure</B></FONT></TD><TD><INPUT TYPE="text" NAME="Procedure" VALUE="#HTMLEditFormat(T.Procedure)#" SIZE=30 STYLE="font-family:Courier New,monospace"></TD></TR>
<TR><TD></TD><TD>#Request.f#<INPUT TYPE="checkbox" NAME="KeepLoaded" VALUE="1"<cfif T.KeepLoaded EQ 1> CHECKED</cfif>> <B>Keep library loaded</B> - Check this box to retain the library in RAM.</FONT></TD></TR>
</cfif>
<TR><TD VALIGN=TOP>#Request.f#<B>Description</B></FONT></TD><TD><TEXTAREA NAME="Description" ROWS=4 COLS=50 WRAP=VIRTUAL>#HTMLEditFormat(T.Description)#</TEXTAREA></TD></TR>
</TABLE>
<HR NOSHADE SIZE=1>
<INPUT TYPE="submit" NAME="Save" VALUE="#IIf(isNew, DE('Add'), DE('Update'))#">
<cfif NOT isNew><INPUT TYPE="submit" NAME="Delete" VALUE="Delete" onClick="return confirm('Remove this CFX tag?')"></cfif>
<INPUT TYPE="button" VALUE="Cancel" onClick="location='cfx.cfm'">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
