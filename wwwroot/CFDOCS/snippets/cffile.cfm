<CFSET Scratch = GetTempDirectory() & "cffile_demo.txt">
<CFFILE ACTION="WRITE" FILE="#Scratch#" OUTPUT="Line 1: written #DateFormat(Now(), 'mmm d, yyyy')#">
<CFFILE ACTION="APPEND" FILE="#Scratch#" OUTPUT="Line 2: appended">
<CFFILE ACTION="READ" FILE="#Scratch#" VARIABLE="Contents">
<CFFILE ACTION="DELETE" FILE="#Scratch#">
<CFOUTPUT><P>WRITE, APPEND, READ and DELETE:</P><PRE>#HTMLEditFormat(Contents)#</PRE></CFOUTPUT>

<CFIF IsDefined("Form.Upload") AND Len(Form.Upload)>
  <CFFILE ACTION="UPLOAD" FILEFIELD="Upload" DESTINATION="#GetTempDirectory()#" NAMECONFLICT="MakeUnique">
  <CFOUTPUT>
  <TABLE BORDER=1 CELLPADDING=3>
  <TR><TD>ClientFile</TD><TD>#HTMLEditFormat(CFFILE.ClientFile)#</TD></TR>
  <TR><TD>ServerFile</TD><TD>#HTMLEditFormat(CFFILE.ServerFile)#</TD></TR>
  <TR><TD>FileSize</TD><TD>#CFFILE.FileSize# bytes</TD></TR>
  <TR><TD>ContentType</TD><TD>#CFFILE.ContentType#/#CFFILE.ContentSubType#</TD></TR>
  <TR><TD>FileWasRenamed</TD><TD>#CFFILE.FileWasRenamed#</TD></TR>
  </TABLE>
  </CFOUTPUT>
  <!--- This is only a demo: throw the upload away again --->
  <CFFILE ACTION="DELETE" FILE="#CFFILE.ServerDirectory#/#CFFILE.ServerFile#">
</CFIF>

<FORM ACTION="cffile.cfm" METHOD="POST" ENCTYPE="multipart/form-data">
Upload a small file: <INPUT TYPE="File" NAME="Upload">
<INPUT TYPE="Submit" VALUE="Upload">
</FORM>
