<CFSET TmpFile = GetTempFile(GetTempDirectory(), "kfs")>
<CFOUTPUT>
<P>Created: <TT>#GetFileFromPath(TmpFile)#</TT>
<P>Exists right away: #FileExists(TmpFile)#
</CFOUTPUT>
<CFFILE ACTION="APPEND" FILE="#TmpFile#" OUTPUT="Line one">
<CFFILE ACTION="APPEND" FILE="#TmpFile#" OUTPUT="Line two">
<CFFILE ACTION="READ" FILE="#TmpFile#" VARIABLE="Text">
<CFFILE ACTION="DELETE" FILE="#TmpFile#">
<CFOUTPUT>
<P>Contents:<PRE>#Text#</PRE>
<P>After CFFILE ACTION="DELETE": #FileExists(TmpFile)#
</CFOUTPUT>
