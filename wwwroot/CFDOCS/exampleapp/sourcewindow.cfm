<!---
	sourcewindow.cfm - shows the CFML source of an example template.
	  ?file=GlobalCorp/index.cfm    (path relative to /CFDOCS/exampleapp/)
	Only .cfm files inside /CFDOCS/exampleapp/ can be shown: the path may
	contain only letters, digits, _ - . and /, may not start with / and may
	not contain "..", so nobody can wander off to read other files.
--->
<CFPARAM NAME="URL.file" DEFAULT="">
<CFSET BaseDir = ExpandPath("/CFDOCS/exampleapp/")>
<CFSET FileName = Trim(URL.file)>
<CFSET ErrorMessage = "">

<CFIF NOT Len(FileName)>
	<CFSET ErrorMessage = "No file was requested.">
<CFELSEIF Find("..", FileName) OR Left(FileName, 1) IS "/" OR Find("//", FileName)
	OR NOT REFindNoCase("^[A-Za-z0-9_./-]+\.cfm$", FileName)>
	<CFSET ErrorMessage = "Sorry, only the source of the example application templates can be viewed.">
<CFELSEIF NOT FileExists(BaseDir & FileName)>
	<CFSET ErrorMessage = "There is no example template named #FileName#.">
<CFELSE>
	<CFFILE ACTION="Read" FILE="#BaseDir##FileName#" VARIABLE="SourceCode">
	<!--- the other templates in the same directory, for the "jump to" list --->
	<CFIF Find("/", FileName)>
		<CFSET SubDir = Left(FileName, Len(FileName) - Len(ListLast(FileName, "/")))>
	<CFELSE>
		<CFSET SubDir = "">
	</CFIF>
	<CFDIRECTORY ACTION="List" DIRECTORY="#BaseDir##SubDir#" FILTER="*.cfm" NAME="Siblings" SORT="Name ASC">
</CFIF>

<HTML>
<HEAD>
<TITLE>Source: <CFOUTPUT>#HTMLEditFormat(FileName)#</CFOUTPUT></TITLE>
</HEAD>
<BODY BGCOLOR="#FFFFFF" TOPMARGIN=0 LEFTMARGIN=0 MARGINWIDTH=0 MARGINHEIGHT=0>
<CFOUTPUT>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=4 CELLSPACING=0>
<TR BGCOLOR="##003399">
	<TD><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>/CFDOCS/exampleapp/#HTMLEditFormat(FileName)#</B></FONT></TD>
	<TD ALIGN=RIGHT><FORM STYLE="margin:0"><INPUT TYPE="Button" VALUE="Close" onClick="window.close()"></FORM></TD>
</TR>
<CFIF NOT Len(ErrorMessage)>
<TR BGCOLOR="##CCCCCC">
	<TD COLSPAN=2>
	<FORM ACTION="sourcewindow.cfm" METHOD="GET" STYLE="margin:0">
	<FONT FACE="Arial, Helvetica" SIZE=1><B>Other templates here:</B></FONT>
	<SELECT NAME="file" onChange="this.form.submit()">
		<CFLOOP QUERY="Siblings"><OPTION VALUE="#SubDir##Name#"<CFIF SubDir & Name IS FileName> SELECTED</CFIF>>#Name#</CFLOOP>
	</SELECT>
	<NOSCRIPT><INPUT TYPE="Submit" VALUE="View"></NOSCRIPT>
	<FONT FACE="Arial, Helvetica" SIZE=1>&nbsp; #NumberFormat(Len(SourceCode))# bytes, #ListLen(SourceCode, Chr(10))# lines</FONT>
	</FORM>
	</TD>
</TR>
</CFIF>
</TABLE>
<CFIF Len(ErrorMessage)>
	<P><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##CC0000"><B>#HTMLEditFormat(ErrorMessage)#</B></FONT></P>
<CFELSE>
	<FONT SIZE=2>#HTMLCodeFormat(SourceCode)#</FONT>
</CFIF>
</CFOUTPUT>
</BODY>
</HTML>
